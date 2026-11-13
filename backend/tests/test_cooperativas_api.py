import io
import pytest
from src.core.security import create_access_token, hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.services.logo_storage_service import PNG_MAGIC


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
        first_name="Test",
        last_name="User",
        email=email,
        hashed_password=hash_password("Pass1234"),
        is_active=is_active,
    )
    u.roles = roles
    return repo.create(u)


@pytest.fixture
def admin_token(db_session):
    admin = make_user(
        db_session,
        "admin@test.ec",
        "1104609829",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    token = create_access_token(subject=admin.id)
    return f"Bearer {token}"


def test_cooperativas_api_crud_flow(client, admin_token):
    headers = {"Authorization": admin_token}

    # 1. Create cooperative (CP-46)
    create_payload = {
        "name": "Cooperativa Loja",
        "ruc": "1104609829001",
        "address": "Av. Isidro Ayora",
        "phone": "0987654321",
        "email": "contacto@cooploja.ec",
        "logo_url": "https://example.com/logo.png",
    }
    res = client.post("/api/v1/cooperativas", json=create_payload, headers=headers)
    assert res.status_code == 201
    coop_data = res.json()
    coop_id = coop_data["id"]
    assert coop_data["name"] == "Cooperativa Loja"
    assert coop_data["is_active"] is True

    # 2. List cooperatives
    list_res = client.get("/api/v1/cooperativas", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert len(list_res.json()["items"]) == 1

    # 3. Get single cooperative by ID
    get_res = client.get(f"/api/v1/cooperativas/{coop_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == coop_id

    # 4. Update cooperative (CP-55)
    update_res = client.put(
        f"/api/v1/cooperativas/{coop_id}",
        json={"name": "Coop Loja Internacional", "phone": "0911111111"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Coop Loja Internacional"
    assert update_res.json()["phone"] == "0911111111"

    # 5. Upload logo
    fake_png = PNG_MAGIC + b"\x00" * 32
    upload_res = client.post(
        f"/api/v1/cooperativas/{coop_id}/logo",
        files={"file": ("logo.png", io.BytesIO(fake_png), "image/png")},
        headers=headers,
    )
    assert upload_res.status_code == 200
    assert upload_res.json()["logo_url"].startswith("/static/logos/")

    # 6. Deactivate cooperative (CP-58)
    deact_res = client.patch(
        f"/api/v1/cooperativas/{coop_id}/estado",
        json={"is_active": False},
        headers=headers,
    )
    assert deact_res.status_code == 200
    assert deact_res.json()["is_active"] is False

    # 7. Edit on deactivated cooperative yields 409 COOPERATIVA_INACTIVA (CP-60)
    conflict_res = client.put(
        f"/api/v1/cooperativas/{coop_id}",
        json={"name": "Otro Nombre"},
        headers=headers,
    )
    assert conflict_res.status_code == 409
    assert conflict_res.json()["detail"]["code"] == "COOPERATIVA_INACTIVA"


def test_cooperativas_api_administrators(client, admin_token, db_session):
    headers = {"Authorization": admin_token}

    # Create coop
    coop_res = client.post(
        "/api/v1/cooperativas",
        json={"name": "Coop Calvas", "ruc": "1104609829001"},
        headers=headers,
    )
    coop_id = coop_res.json()["id"]

    # Create eligible user
    u1 = make_user(
        db_session,
        "coopadmin1@test.ec",
        "1710034065",
        [UserRole.ADMIN_COOPERATIVA],
    )

    # List eligible admins
    eligible_res = client.get(
        f"/api/v1/cooperativas/{coop_id}/administradores/elegibles",
        headers=headers,
    )
    assert eligible_res.status_code == 200
    assert len(eligible_res.json()) >= 1

    # Assign admin
    assign_res = client.put(
        f"/api/v1/cooperativas/{coop_id}/administradores",
        json={"user_ids": [u1.id]},
        headers=headers,
    )
    assert assign_res.status_code == 200
    assert len(assign_res.json()) == 1
    assert assign_res.json()[0]["email"] == "coopadmin1@test.ec"

    # Get assigned admins
    get_admins_res = client.get(
        f"/api/v1/cooperativas/{coop_id}/administradores",
        headers=headers,
    )
    assert get_admins_res.status_code == 200
    assert len(get_admins_res.json()) == 1


def test_cooperativas_api_unauthorized_and_roles(client, db_session):
    # 1. 401 without auth header
    res_no_auth = client.get("/api/v1/cooperativas")
    assert res_no_auth.status_code == 401

    # 2. 403 for other roles
    unauthorized_roles = [
        [UserRole.PASAJERO],
        [UserRole.ADMIN_COOPERATIVA],
        [UserRole.SECRETARIA_COOPERATIVA],
    ]
    for idx, roles in enumerate(unauthorized_roles, start=2):
        user = make_user(
            db_session,
            f"user_{roles[0].value.lower()}@test.ec",
            f"092669145{idx}",
            roles,
        )
        token = f"Bearer {create_access_token(subject=user.id)}"
        res = client.get("/api/v1/cooperativas", headers={"Authorization": token})
        assert res.status_code == 403, f"Failed for role {roles}"


def test_cooperativas_api_validation_errors(client, admin_token):
    headers = {"Authorization": admin_token}

    # Empty body or missing required fields -> 422
    res_422 = client.post("/api/v1/cooperativas", json={}, headers=headers)
    assert res_422.status_code == 422
