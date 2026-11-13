import pytest
from fastapi import HTTPException
from src.core.permissions import require_active_cooperativa
from src.models.cooperativa import Cooperativa
from src.models.user import DocumentType, User, UserRole
from src.repositories.cooperativa_repository import CooperativaRepository
from src.repositories.user_repository import UserRepository
from src.services.cooperativa_administrators_service import (
    CooperativaAdministratorsService,
)
from src.services.cooperativa_service import CODE_COOPERATIVA_INACTIVA


@pytest.fixture
def admin_user(db_session):
    user_repo = UserRepository(db_session)
    return user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1104609829",
            first_name="Admin",
            last_name="General",
            email="admin@terminal.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.ADMIN_GENERAL],
        )
    )


def test_cooperativa_administrators_flow(db_session, admin_user):
    coop_repo = CooperativaRepository(db_session)
    user_repo = UserRepository(db_session)
    service = CooperativaAdministratorsService(db_session)

    # 1. Create cooperative
    coop = coop_repo.create(
        Cooperativa(name="Cooperativa Loja", ruc="1104609829001", is_active=True)
    )

    # 2. Create users
    u1 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1710034065",
            first_name="AdminUno",
            last_name="Perez",
            email="uno@coop.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO, UserRole.ADMIN_COOPERATIVA],
        )
    )
    u2 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="0926691452",
            first_name="AdminDos",
            last_name="Gomez",
            email="dos@coop.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO, UserRole.ADMIN_COOPERATIVA],
        )
    )
    u3 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="0102555547",
            first_name="AdminTres",
            last_name="Torres",
            email="tres@coop.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO, UserRole.ADMIN_COOPERATIVA],
        )
    )
    u4_extra = user_repo.create(
        User(
            document_type=DocumentType.PASAPORTE,
            document_number="P1234567",
            first_name="AdminCuatro",
            last_name="Extra",
            email="cuatro@coop.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO, UserRole.ADMIN_COOPERATIVA],
        )
    )

    # CP-64: Buscar usuarios elegibles
    search_res = service.list_eligible_administrators(coop.id, search="AdminUno")
    assert len(search_res) == 1
    assert search_res[0].email == "uno@coop.ec"

    # CP-61: Asignar administradores (hasta 3)
    assigned = service.update_administrators(
        cooperativa_id=coop.id,
        user_ids=[u1.id, u2.id],
        current_user=admin_user,
    )
    assert len(assigned) == 2
    assigned_emails = {a.email for a in assigned}
    assert "uno@coop.ec" in assigned_emails
    assert "dos@coop.ec" in assigned_emails

    # Check DB state
    refreshed_u1 = user_repo.get_by_id(u1.id)
    assert refreshed_u1.cooperativa_id == coop.id

    # CP-62: Bloquear / rechazar más de 3
    with pytest.raises(HTTPException) as exc:
        service.update_administrators(
            cooperativa_id=coop.id,
            user_ids=[u1.id, u2.id, u3.id, u4_extra.id],
            current_user=admin_user,
        )
    assert exc.value.status_code == 400
    assert "máximo 3" in exc.value.detail

    # Assign 3
    service.update_administrators(
        cooperativa_id=coop.id,
        user_ids=[u1.id, u2.id, u3.id],
        current_user=admin_user,
    )
    current_list = service.get_administrators(coop.id)
    assert len(current_list) == 3

    # CP-63: Desvincular a un administrador de la cooperativa
    # u2 is removed by only keeping u1 and u3
    service.update_administrators(
        cooperativa_id=coop.id,
        user_ids=[u1.id, u3.id],
        current_user=admin_user,
    )
    after_unlink_admins = service.get_administrators(coop.id)
    assert len(after_unlink_admins) == 2
    assert "dos@coop.ec" not in {a.email for a in after_unlink_admins}

    # Verify u2 retained ADMIN_COOPERATIVA role and cooperativa_id is None
    refreshed_u2 = user_repo.get_by_id(u2.id)
    assert refreshed_u2.cooperativa_id is None
    assert UserRole.ADMIN_COOPERATIVA in refreshed_u2.roles

    # Inactive cooperative rejects assignment
    coop.is_active = False
    coop_repo.update(coop)

    with pytest.raises(HTTPException) as exc:
        service.update_administrators(
            cooperativa_id=coop.id,
            user_ids=[u1.id],
            current_user=admin_user,
        )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == CODE_COOPERATIVA_INACTIVA


def test_require_active_cooperativa_dependency(db_session):
    coop_repo = CooperativaRepository(db_session)
    user_repo = UserRepository(db_session)

    # 1. User without cooperative assigned
    user_no_coop = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1104609829",
            first_name="User",
            last_name="NoCoop",
            email="nocoop@test.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.ADMIN_COOPERATIVA],
        )
    )
    with pytest.raises(HTTPException) as exc:
        require_active_cooperativa(user_no_coop, db_session)
    assert exc.value.status_code == 403

    # 2. User with active cooperative
    active_coop = coop_repo.create(
        Cooperativa(name="Coop Activa", ruc="1104609829001", is_active=True)
    )
    user_with_active = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1710034065",
            first_name="User",
            last_name="ActiveCoop",
            email="active@test.ec",
            hashed_password="hash",
            is_active=True,
            cooperativa_id=active_coop.id,
            roles=[UserRole.ADMIN_COOPERATIVA],
        )
    )
    res = require_active_cooperativa(user_with_active, db_session)
    assert res.id == user_with_active.id

    # 3. User with deactivated cooperative
    active_coop.is_active = False
    coop_repo.update(active_coop)

    with pytest.raises(HTTPException) as exc:
        require_active_cooperativa(user_with_active, db_session)
    assert exc.value.status_code == 403
    assert "inactiva" in exc.value.detail


def test_concurrency_max_admins_limit(db_session, admin_user):
    """5.3: Verify that under no circumstances can more than 3 admins be assigned."""
    coop_repo = CooperativaRepository(db_session)
    user_repo = UserRepository(db_session)
    service = CooperativaAdministratorsService(db_session)

    coop = coop_repo.create(
        Cooperativa(name="Coop Concurrency", ruc="1104609829001", is_active=True)
    )

    users = []
    for i in range(5):
        u = user_repo.create(
            User(
                document_type=DocumentType.PASAPORTE,
                document_number=f"PASS000{i}",
                first_name=f"Admin{i}",
                last_name="Test",
                email=f"admin{i}@test.ec",
                hashed_password="hash",
                is_active=True,
                roles=[UserRole.ADMIN_COOPERATIVA],
            )
        )
        users.append(u)

    # 1. Attempt assigning 4 users at once
    with pytest.raises(HTTPException) as exc:
        service.update_administrators(
            cooperativa_id=coop.id,
            user_ids=[u.id for u in users[:4]],
            current_user=admin_user,
        )
    assert exc.value.status_code == 400

    # 2. Assign exactly 3 users
    service.update_administrators(
        cooperativa_id=coop.id,
        user_ids=[u.id for u in users[:3]],
        current_user=admin_user,
    )
    current_admins = service.get_administrators(coop.id)
    assert len(current_admins) == 3

    # 3. Attempt to add a 4th user without removing existing
    with pytest.raises(HTTPException):
        service.update_administrators(
            cooperativa_id=coop.id,
            user_ids=[users[0].id, users[1].id, users[2].id, users[3].id],
            current_user=admin_user,
        )
    # The count must remain strictly 3
    assert len(service.get_administrators(coop.id)) == 3
