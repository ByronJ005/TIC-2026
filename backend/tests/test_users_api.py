import pytest
from src.core.security import create_access_token, hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository


def make_user(
    db,
    email: str,
    doc: str,
    first: str,
    last: str,
    roles: list[UserRole],
    is_active: bool = True,
) -> User:
    repo = UserRepository(db)
    u = User(
        document_type=DocumentType.CEDULA,
        document_number=doc,
        first_name=first,
        last_name=last,
        email=email,
        hashed_password=hash_password("Pass1234"),
        is_active=is_active,
    )
    u.roles = roles
    return repo.create(u)


def test_list_users_as_admin_general(client, db_session):
    admin = make_user(
        db_session,
        "admin@test.com",
        "1710034065",
        "Admin",
        "Principal",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    make_user(
        db_session,
        "user1@test.com",
        "0926691452",
        "Usuario",
        "Uno",
        [UserRole.PASAJERO],
    )
    token = create_access_token(subject=admin.id)

    res = client.get(
        "/api/v1/usuarios?page=1&size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1


def test_list_users_forbidden_for_pasajero(client, db_session):
    pasajero = make_user(
        db_session,
        "pasajero@test.com",
        "1710034065",
        "Pasajero",
        "Comun",
        [UserRole.PASAJERO],
    )
    token = create_access_token(subject=pasajero.id)

    res = client.get(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
    assert "No autorizado" in res.json()["detail"]


def test_update_roles_flow(client, db_session):
    admin = make_user(
        db_session,
        "admin_r@test.com",
        "1710034065",
        "Admin",
        "Roles",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    target = make_user(
        db_session,
        "target_r@test.com",
        "1104609829",
        "Target",
        "Roles",
        [UserRole.PASAJERO],
    )
    token = create_access_token(subject=admin.id)

    # Assign ADMIN_COOPERATIVA
    res = client.put(
        f"/api/v1/usuarios/{target.id}/roles",
        json={"roles": ["ADMIN_COOPERATIVA"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    roles = res.json()["roles"]
    assert "ADMIN_COOPERATIVA" in roles
    assert "PASAJERO" in roles  # Inmutable

    # Revoke ADMIN_COOPERATIVA
    res_revoke = client.put(
        f"/api/v1/usuarios/{target.id}/roles",
        json={"roles": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_revoke.status_code == 200
    roles_revoked = res_revoke.json()["roles"]
    assert roles_revoked == ["PASAJERO"]


def test_update_status_flow(client, db_session):
    admin = make_user(
        db_session,
        "admin_s@test.com",
        "1710034065",
        "Admin",
        "Status",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    target = make_user(
        db_session,
        "target_s@test.com",
        "0102555547",
        "Target",
        "Status",
        [UserRole.PASAJERO],
    )
    token = create_access_token(subject=admin.id)

    # Deactivate
    res_deact = client.patch(
        f"/api/v1/usuarios/{target.id}/estado",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_deact.status_code == 200
    assert res_deact.json()["is_active"] is False

    # Reactivate
    res_act = client.patch(
        f"/api/v1/usuarios/{target.id}/estado",
        json={"is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_act.status_code == 200
    assert res_act.json()["is_active"] is True


def test_inactive_user_login_message(client, db_session):
    """CP-31: Login with inactive user displays exact alert message."""
    make_user(
        db_session,
        "inactivo.login@example.com",
        "1710034065",
        "Inactivo",
        "Login",
        [UserRole.PASAJERO],
        is_active=False,
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "inactivo.login@example.com", "password": "Pass1234"},
    )
    assert res.status_code == 400
    assert (
        res.json()["detail"]
        == "Su cuenta se encuentra inactiva. Contacte al administrador"
    )

