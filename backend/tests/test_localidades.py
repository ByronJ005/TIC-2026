import pytest
from src.core.security import create_access_token, hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.locality_repository import LocalityRepository
from src.repositories.user_repository import UserRepository
from src.schemas.locality_schemas import LocalityCreate
from src.services.locality_service import LocalityService


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
def admin_general_token(db_session):
    u = make_user(
        db_session,
        "admin.gen@test.ec",
        "1104609829",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    return f"Bearer {create_access_token(subject=u.id)}"


@pytest.fixture
def admin_coop_token(db_session):
    u = make_user(
        db_session,
        "admin.coop@test.ec",
        "0928923075",
        [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
    )
    return f"Bearer {create_access_token(subject=u.id)}"


@pytest.fixture
def passenger_token(db_session):
    u = make_user(
        db_session,
        "passenger@test.ec",
        "1710034065",
        [UserRole.PASAJERO],
    )
    return f"Bearer {create_access_token(subject=u.id)}"


def test_locality_service_crud_and_idempotency(db_session):
    service = LocalityService(db_session)

    # 1. Create new locality
    loc1, created1 = service.get_or_create(LocalityCreate(name="  Loja  "))
    assert created1 is True
    assert loc1.name == "Loja"
    assert loc1.id is not None

    # 2. Get existing locality with different casing and spaces (CP-77)
    loc2, created2 = service.get_or_create(LocalityCreate(name="  loja   "))
    assert created2 is False
    assert loc2.id == loc1.id
    assert loc2.name == "Loja"

    # 3. Search
    service.get_or_create(LocalityCreate(name="Quito"))
    service.get_or_create(LocalityCreate(name="Cuenca"))
    results = service.search("ui")
    assert len(results) == 1
    assert results[0].name == "Quito"


def test_localidades_api_endpoints_and_permissions(client, admin_general_token, admin_coop_token, passenger_token):
    # 1. Unauthenticated -> 401
    resp = client.get("/api/v1/localidades")
    assert resp.status_code == 401

    # 2. Forbidden for passenger -> 403
    resp = client.get("/api/v1/localidades", headers={"Authorization": passenger_token})
    assert resp.status_code == 403

    resp = client.post(
        "/api/v1/localidades",
        json={"name": "Ambato"},
        headers={"Authorization": passenger_token},
    )
    assert resp.status_code == 403

    # 3. Allowed for ADMIN_GENERAL -> 201 on new
    resp = client.post(
        "/api/v1/localidades",
        json={"name": "Ambato"},
        headers={"Authorization": admin_general_token},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Ambato"

    # 4. Idempotent create -> 200 on existing for ADMIN_COOPERATIVA
    resp = client.post(
        "/api/v1/localidades",
        json={"name": "  ambato  "},
        headers={"Authorization": admin_coop_token},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == data["id"]

    # 5. List localities for ADMIN_COOPERATIVA
    resp = client.get("/api/v1/localidades?search=amb", headers={"Authorization": admin_coop_token})
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["total"] == 1
    assert res_data["items"][0]["name"] == "Ambato"
