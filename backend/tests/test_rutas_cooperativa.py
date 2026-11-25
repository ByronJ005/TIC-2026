from decimal import Decimal
import pytest
from src.core.permissions import CODE_COOPERATIVA_ASIGNADA_INACTIVA
from src.core.security import create_access_token, hash_password
from src.models.cooperativa import Cooperativa
from src.models.locality import Locality
from src.models.route import CooperativaGeneralRoute, Route
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.route_schemas import (
    AdoptGeneralRouteEstadoUpdate,
    AdoptGeneralRoutesRequest,
    RouteCreate,
    RouteEstadoUpdate,
    RouteUpdate,
)
from src.services.cooperativa_route_service import CooperativaRouteService


def make_user(
    db,
    email: str,
    doc: str,
    roles: list[UserRole],
    cooperativa_id: int = None,
    is_active: bool = True,
) -> User:
    repo = UserRepository(db)
    u = User(
        document_type=DocumentType.CEDULA,
        document_number=doc,
        first_name="User",
        last_name="Test",
        email=email,
        hashed_password=hash_password("Pass1234"),
        cooperativa_id=cooperativa_id,
        is_active=is_active,
    )
    u.roles = roles
    return repo.create(u)


def make_locality(db, name: str) -> Locality:
    loc = Locality(name=name, is_active=True)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def make_coop(db, name: str, ruc: str, is_active: bool = True) -> Cooperativa:
    coop = Cooperativa(name=name, ruc=ruc, is_active=is_active)
    db.add(coop)
    db.commit()
    db.refresh(coop)
    return coop


def make_general_route(db, origin_id: int, destination_id: int, distance: Decimal, is_active: bool = True) -> Route:
    r = Route(
        cooperativa_id=None,
        origin_id=origin_id,
        destination_id=destination_id,
        name=f"Ruta {origin_id}-{destination_id}",
        distance_km=distance,
        estimated_time_minutes=300,
        is_active=is_active,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def coop_setup(db_session):
    coop1 = make_coop(db_session, "Cooperativa Loja", "1104609829001")
    admin1 = make_user(
        db_session,
        "admin1@loja.ec",
        "1104609829",
        [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
        cooperativa_id=coop1.id,
    )
    token1 = f"Bearer {create_access_token(subject=admin1.id)}"

    coop2 = make_coop(db_session, "Cooperativa Cariamanga", "1104609829002")
    admin2 = make_user(
        db_session,
        "admin2@cariamanga.ec",
        "0928923075",
        [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
        cooperativa_id=coop2.id,
    )
    token2 = f"Bearer {create_access_token(subject=admin2.id)}"

    return {
        "coop1": coop1,
        "admin1": admin1,
        "token1": token1,
        "coop2": coop2,
        "admin2": admin2,
        "token2": token2,
    }


def test_cooperativa_route_service_adoption_flow(db_session, coop_setup):
    service = CooperativaRouteService(db_session)
    coop1 = coop_setup["coop1"]
    admin1 = coop_setup["admin1"]

    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")
    cuenca = make_locality(db_session, "Cuenca")

    r_active = make_general_route(db_session, loja.id, quito.id, Decimal("650.00"), is_active=True)
    r_inactive = make_general_route(db_session, loja.id, cuenca.id, Decimal("210.00"), is_active=False)

    # CP-86: Only active general routes not yet adopted appear in available list
    available = service.list_available_general_routes(coop1.id)
    assert len(available) == 1
    assert available[0].id == r_active.id

    # CP-87: Adopt general route
    adopted = service.adopt_general_routes(
        cooperativa_id=coop1.id,
        route_ids=[r_active.id],
        current_user=admin1,
    )
    assert len(adopted) == 1
    assert adopted[0].route_id == r_active.id
    assert adopted[0].is_active is True

    # Now available list is empty
    available_after = service.list_available_general_routes(coop1.id)
    assert len(available_after) == 0

    # Adopting again raises 409
    with pytest.raises(Exception) as exc:
        service.adopt_general_routes(
            cooperativa_id=coop1.id,
            route_ids=[r_active.id],
            current_user=admin1,
        )
    assert exc.value.status_code == 409

    # CP-88: Disable adopted route
    adoption_id = adopted[0].id
    res_disabled = service.update_adoption_estado(
        cooperativa_id=coop1.id,
        adoption_id=adoption_id,
        data=AdoptGeneralRouteEstadoUpdate(is_active=False),
        current_user=admin1,
    )
    assert res_disabled.is_active is False

    # CP-90: Reactivate adopted route
    res_reactivated = service.update_adoption_estado(
        cooperativa_id=coop1.id,
        adoption_id=adoption_id,
        data=AdoptGeneralRouteEstadoUpdate(is_active=True),
        current_user=admin1,
    )
    assert res_reactivated.is_active is True

    # CP-91: If general route becomes inactive, reactivating adopted route raises 409
    r_active.is_active = False
    db_session.commit()

    service.update_adoption_estado(
        cooperativa_id=coop1.id,
        adoption_id=adoption_id,
        data=AdoptGeneralRouteEstadoUpdate(is_active=False),
        current_user=admin1,
    )
    with pytest.raises(Exception) as exc:
        service.update_adoption_estado(
            cooperativa_id=coop1.id,
            adoption_id=adoption_id,
            data=AdoptGeneralRouteEstadoUpdate(is_active=True),
            current_user=admin1,
        )
    assert exc.value.status_code == 409
    assert "se encuentra desactivada por la administración del terminal" in str(exc.value.detail)


def test_cooperativa_specific_routes_flow_and_uniqueness(db_session, coop_setup):
    service = CooperativaRouteService(db_session)
    coop1 = coop_setup["coop1"]
    admin1 = coop_setup["admin1"]
    coop2 = coop_setup["coop2"]
    admin2 = coop_setup["admin2"]

    loja = make_locality(db_session, "Loja")
    orianga = make_locality(db_session, "Orianga")

    # CP-92: Register specific route for coop1
    r_coop1 = service.create_specific_route(
        cooperativa_id=coop1.id,
        data=RouteCreate(
            origin_id=loja.id,
            destination_id=orianga.id,
            distance_km=Decimal("40.00"),
            estimated_time_minutes=90,
            name_suffix="Rural",
        ),
        current_user=admin1,
    )
    assert r_coop1.cooperativa_id == coop1.id
    assert r_coop1.name == "Loja - Orianga Rural"

    # CP-93: coop2 can register the SAME combination without conflict!
    r_coop2 = service.create_specific_route(
        cooperativa_id=coop2.id,
        data=RouteCreate(
            origin_id=loja.id,
            destination_id=orianga.id,
            distance_km=Decimal("40.00"),
            estimated_time_minutes=90,
        ),
        current_user=admin2,
    )
    assert r_coop2.cooperativa_id == coop2.id

    # But coop1 registering duplicate combination fails with 409
    with pytest.raises(Exception) as exc:
        service.create_specific_route(
            cooperativa_id=coop1.id,
            data=RouteCreate(
                origin_id=loja.id,
                destination_id=orianga.id,
                distance_km=Decimal("40.00"),
                estimated_time_minutes=95,
            ),
            current_user=admin1,
        )
    assert exc.value.status_code == 409

    # CP-94: Edit specific route
    edited = service.update_specific_route(
        cooperativa_id=coop1.id,
        route_id=r_coop1.id,
        data=RouteUpdate(estimated_time_minutes=100, description="Actualizada"),
        current_user=admin1,
    )
    assert edited.estimated_time_minutes == 100
    assert edited.description == "Actualizada"

    # CP-95: Deactivate specific route
    deactivated = service.update_specific_route_estado(
        cooperativa_id=coop1.id,
        route_id=r_coop1.id,
        data=RouteEstadoUpdate(is_active=False),
        current_user=admin1,
    )
    assert deactivated.is_active is False

    # CP-96: Reactivate specific route
    reactivated = service.update_specific_route_estado(
        cooperativa_id=coop1.id,
        route_id=r_coop1.id,
        data=RouteEstadoUpdate(is_active=True),
        current_user=admin1,
    )
    assert reactivated.is_active is True


def test_rutas_cooperativa_api_endpoints_and_isolation(client, db_session, coop_setup):
    coop1 = coop_setup["coop1"]
    token1 = coop_setup["token1"]
    token2 = coop_setup["token2"]

    loja = make_locality(db_session, "Loja")
    catamayo = make_locality(db_session, "Catamayo")

    # 1. Create specific route via API as admin1
    create_payload = {
        "origin_id": loja.id,
        "destination_id": catamayo.id,
        "distance_km": "36.00",
        "estimated_time_minutes": 45,
    }
    resp = client.post("/api/v1/rutas-cooperativa/especificas", json=create_payload, headers={"Authorization": token1})
    assert resp.status_code == 201
    route_id = resp.json()["id"]

    # 2. admin1 lists specific routes -> 1 route
    resp = client.get("/api/v1/rutas-cooperativa/especificas", headers={"Authorization": token1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # 3. admin2 lists specific routes -> 0 routes (isolated!)
    resp = client.get("/api/v1/rutas-cooperativa/especificas", headers={"Authorization": token2})
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    # CP-97: admin2 attempts to access admin1's route via shared route detail endpoint -> 403 Forbidden
    resp = client.get(f"/api/v1/rutas/{route_id}", headers={"Authorization": token2})
    assert resp.status_code == 403
    assert "Recurso de otra cooperativa" in resp.json()["detail"]

    # CP-98: When coop1 is deactivated -> 403 with COOPERATIVA_ASIGNADA_INACTIVA
    coop1.is_active = False
    db_session.commit()

    resp = client.get("/api/v1/rutas-cooperativa/especificas", headers={"Authorization": token1})
    assert resp.status_code == 403
    error_data = resp.json()["detail"]
    assert error_data["code"] == CODE_COOPERATIVA_ASIGNADA_INACTIVA
    assert "Por el momento, su cooperativa se encuentra desactivada" in error_data["message"]
