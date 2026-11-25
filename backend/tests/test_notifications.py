import pytest
from src.core.security import create_access_token, hash_password
from src.models.notification import Notification
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.services.email_service import EmailDeliveryError, EmailSender
from src.services.notification_service import NotificationService


class FailingEmailSender:
    def send(self, to_address: str, subject: str, body: str) -> None:
        raise EmailDeliveryError("Error simulado de conexión SMTP")


class RecordingEmailSender:
    def __init__(self):
        self.sent = []

    def send(self, to_address: str, subject: str, body: str) -> None:
        self.sent.append({"to": to_address, "subject": subject, "body": body})


def make_user(
    db,
    email: str,
    doc: str,
    roles: list[UserRole],
    is_active: bool = True,
) -> User:
    repo = UserRepository(db)
    u = User(
        document_type=DocumentType.CEDULA,
        document_number=doc,
        first_name="Notif",
        last_name="User",
        email=email,
        hashed_password=hash_password("Pass1234"),
        is_active=is_active,
    )
    u.roles = roles
    return repo.create(u)


def test_notification_service_flow(db_session):
    u1 = make_user(db_session, "u1@test.ec", "1104609829", [UserRole.PASAJERO])
    u2 = make_user(db_session, "u2@test.ec", "0928923075", [UserRole.PASAJERO])

    email_sender = RecordingEmailSender()
    service = NotificationService(db_session, email_sender=email_sender)

    # CP-99: When user has no notifications
    res = service.get_user_notifications(u1.id)
    assert res.total == 0
    assert res.unread_count == 0
    assert len(res.items) == 0
    assert res.has_more is False

    # Create 7 notifications for u1
    for i in range(1, 8):
        service.notify_users(
            user_ids=[u1.id],
            title=f"Aviso {i}",
            message=f"Mensaje de prueba {i}",
        )

    # Check emails sent
    assert len(email_sender.sent) == 7

    # CP-100 & CP-101: Page 1 with size 5
    p1 = service.get_user_notifications(u1.id, page=1, size=5)
    assert p1.total == 7
    assert p1.unread_count == 7
    assert len(p1.items) == 5
    assert p1.has_more is True
    assert p1.items[0].title == "Aviso 7"  # Most recent first

    # Page 2 (cargar más)
    p2 = service.get_user_notifications(u1.id, page=2, size=5)
    assert len(p2.items) == 2
    assert p2.has_more is False

    # CP-102: Mark all as read
    marked = service.mark_all_as_read(u1.id)
    assert marked == 7

    p1_read = service.get_user_notifications(u1.id, page=1, size=5)
    assert p1_read.unread_count == 0
    assert all(item.is_read is True for item in p1_read.items)

    # Privacy / Isolation: u2 has no notifications
    u2_res = service.get_user_notifications(u2.id)
    assert u2_res.total == 0


def test_notification_service_email_failure_resilience(db_session):
    u = make_user(db_session, "failing@test.ec", "1710034065", [UserRole.ADMIN_COOPERATIVA])
    failing_sender = FailingEmailSender()
    service = NotificationService(db_session, email_sender=failing_sender)

    # CP-104: Email fails, but in-app notification is still saved and no exception is raised
    service.notify_users(
        user_ids=[u.id],
        title="Ruta Desactivada",
        message="La ruta Loja - Quito ha sido desactivada por el terminal",
    )

    notifs = service.get_user_notifications(u.id)
    assert notifs.total == 1
    assert notifs.items[0].title == "Ruta Desactivada"


def test_notifications_api_endpoints(client, db_session):
    u1 = make_user(db_session, "api1@test.ec", "1104609829", [UserRole.PASAJERO])
    token1 = f"Bearer {create_access_token(subject=u1.id)}"

    # 1. Unauthenticated -> 401
    resp = client.get("/api/v1/notificaciones")
    assert resp.status_code == 401

    # 2. Authenticated user without notifs -> CP-99
    resp = client.get("/api/v1/notificaciones", headers={"Authorization": token1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert data["items"] == []

    # 3. Add notifications
    service = NotificationService(db_session, email_sender=RecordingEmailSender())
    service.notify_users([u1.id], "Alerta 1", "Contenido 1")
    service.notify_users([u1.id], "Alerta 2", "Contenido 2")

    resp = client.get("/api/v1/notificaciones", headers={"Authorization": token1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["unread_count"] == 2

    # 4. Mark all read
    resp = client.patch("/api/v1/notificaciones/leidas", headers={"Authorization": token1})
    assert resp.status_code == 200
    assert resp.json()["count"] == 2

    resp = client.get("/api/v1/notificaciones", headers={"Authorization": token1})
    assert resp.json()["unread_count"] == 0
