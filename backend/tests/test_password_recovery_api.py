import re
from datetime import datetime, timedelta, timezone

import pytest

from src.api.v1.auth_router import get_password_recovery_service
from src.core.security import create_access_token, hash_password, verify_password
from src.main import app
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.services.email_service import get_email_sender
from src.services.password_recovery_service import (
    EMAIL_NOT_REGISTERED_MESSAGE,
    INVALID_RESET_LINK_MESSAGE,
    PASSWORD_RESET_SUCCESS_MESSAGE,
    RESET_REQUEST_PROCESSED_MESSAGE,
    PasswordRecoveryService,
)
from tests.unit.fakes import FakeEmailSender

FORGOT_URL = "/api/v1/auth/forgot-password"
RESET_URL = "/api/v1/auth/reset-password"


@pytest.fixture
def fake_sender():
    sender = FakeEmailSender()
    app.dependency_overrides[get_email_sender] = lambda: sender
    yield sender
    app.dependency_overrides.pop(get_email_sender, None)


def make_user(db, is_active=True) -> User:
    user = User(
        document_type=DocumentType.CEDULA,
        document_number="1710034065",
        first_name="Ana",
        last_name="Gomez",
        email="ana@example.com",
        hashed_password=hash_password("OldPass123"),
        is_active=is_active,
    )
    user.roles = [UserRole.PASAJERO]
    return UserRepository(db).create(user)


def token_from(sender: FakeEmailSender) -> str:
    return re.search(r"token=(\S+)", sender.sent_messages[-1]["body"]).group(1)


def test_cp33_forgot_password_sends_email_and_shows_processed_message(client, db_session, fake_sender):
    make_user(db_session)

    res = client.post(FORGOT_URL, json={"email": "ana@example.com"})

    assert res.status_code == 200
    assert res.json()["message"] == RESET_REQUEST_PROCESSED_MESSAGE
    assert len(fake_sender.sent_messages) == 1


def test_cp35_forgot_password_unregistered_email(client, fake_sender):
    res = client.post(FORGOT_URL, json={"email": "nadie@example.com"})

    assert res.status_code == 404
    assert res.json()["detail"] == EMAIL_NOT_REGISTERED_MESSAGE
    assert fake_sender.sent_messages == []


@pytest.mark.parametrize("payload", [{"email": ""}, {"email": "   "}, {}])
def test_cp36_forgot_password_blank_email(client, fake_sender, payload):
    res = client.post(FORGOT_URL, json=payload)

    assert res.status_code == 422
    assert res.json()["detail"] == "Se requiere el correo electrónico"
    assert fake_sender.sent_messages == []


def test_forgot_password_inactive_account_gets_processed_message_without_email(
    client, db_session, fake_sender
):
    make_user(db_session, is_active=False)

    res = client.post(FORGOT_URL, json={"email": "ana@example.com"})

    assert res.status_code == 200
    assert res.json()["message"] == RESET_REQUEST_PROCESSED_MESSAGE
    assert fake_sender.sent_messages == []


def test_cp34_full_recovery_flow_allows_login_with_new_password(client, db_session, fake_sender):
    make_user(db_session)
    client.post(FORGOT_URL, json={"email": "ana@example.com"})

    res = client.post(
        RESET_URL, json={"token": token_from(fake_sender), "new_password": "NewPass456"}
    )

    assert res.status_code == 200
    assert res.json()["message"] == PASSWORD_RESET_SUCCESS_MESSAGE
    old_login = client.post("/api/v1/auth/login", json={"email": "ana@example.com", "password": "OldPass123"})
    new_login = client.post("/api/v1/auth/login", json={"email": "ana@example.com", "password": "NewPass456"})
    assert old_login.status_code == 400
    assert new_login.status_code == 200


def test_reset_with_reused_token_fails(client, db_session, fake_sender):
    make_user(db_session)
    client.post(FORGOT_URL, json={"email": "ana@example.com"})
    token = token_from(fake_sender)
    client.post(RESET_URL, json={"token": token, "new_password": "NewPass456"})

    res = client.post(RESET_URL, json={"token": token, "new_password": "Another789"})

    assert res.status_code == 400
    assert res.json()["detail"] == INVALID_RESET_LINK_MESSAGE


def test_reset_with_unknown_or_missing_token_fails(client):
    unknown = client.post(RESET_URL, json={"token": "desconocido", "new_password": "NewPass456"})
    missing = client.post(RESET_URL, json={"new_password": "NewPass456"})

    assert unknown.status_code == missing.status_code == 400
    assert unknown.json()["detail"] == missing.json()["detail"] == INVALID_RESET_LINK_MESSAGE


def test_reset_revokes_sessions_issued_before_the_change(client, db_session, fake_sender):
    user = make_user(db_session)
    old_session = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {old_session}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    client.post(FORGOT_URL, json={"email": "ana@example.com"})

    # The reset happens a few seconds later, so the earlier token is strictly older than the change
    def clock_in_the_future():
        return datetime.now(timezone.utc) + timedelta(seconds=5)

    app.dependency_overrides[get_password_recovery_service] = lambda: PasswordRecoveryService(
        db_session, fake_sender, now_provider=clock_in_the_future
    )
    client.post(RESET_URL, json={"token": token_from(fake_sender), "new_password": "NewPass456"})

    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401

def test_reset_stores_password_hash_not_plain_text(client, db_session, fake_sender):
    user = make_user(db_session)
    client.post(FORGOT_URL, json={"email": "ana@example.com"})

    client.post(RESET_URL, json={"token": token_from(fake_sender), "new_password": "NewPass456"})

    db_session.refresh(user)
    assert user.hashed_password != "NewPass456"
    assert verify_password("NewPass456", user.hashed_password)
