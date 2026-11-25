from decimal import Decimal
import pytest
from src.core.security import create_access_token, hash_password
from src.models.cooperativa import Cooperativa
from src.models.locality import Locality
from src.models.route import CooperativaGeneralRoute, Route
from src.models.user import DocumentType, User, UserRole
from src.repositories.locality_repository import LocalityRepository
from src.repositories.user_repository import UserRepository
from src.schemas.route_schemas import RouteCreate, RouteEstadoUpdate, RouteStopInput, RouteUpdate
from src.services.notification_service import NotificationService
from src.services.route_service import RouteService
from src.services.trip_guard import ActiveTripsReport, TripReservationGuard


class MockTripGuard:
    def __init__(self, trips: int = 0, reservations: int = 0):
        self.trips = trips
        self.reservations = reservations

    def check_active_trips_or_reservations(self, route_id: int) -> ActiveTripsReport:
        return ActiveTripsReport(
            active_trips_count=self.trips,
            active_reservations_count=self.reservations,
            affected_user_ids=[],
        )


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


def make_coop(db, name: str, ruc: str) -> Cooperativa:
    coop = Cooperativa(name=name, ruc=ruc, is_active=True)
    db.add(coop)
    db.commit()
    db.refresh(coop)
    return coop


@pytest.fixture
def admin_general(db_session):
    return make_user(
        db_session,
        "admin.gen@test.ec",
        "1104609829",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )


@pytest.fixture
def admin_gen_token(admin_general):
    return f"Bearer {create_access_token(subject=admin_general.id)}"


@pytest.fixture
def admin_coop_data(db_session):
    coop = make_coop(db_session, "Coop Loja", "1104609829001")
    admin = make_user(
        db_session,
        "admin.coop@test.ec",
        "0928923075",
        [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
        cooperativa_id=coop.id,
    )
    return coop, admin, f"Bearer {create_access_token(subject=admin.id)}"


def test_route_service_crud_and_uniqueness(db_session, admin_general):
    service = RouteService(db_session)
    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")
    cuenca = make_locality(db_session, "Cuenca")

    # 1. CP-65: Create valid general route
    create_dto = RouteCreate(
        origin_id=loja.id,
        destination_id=quito.id,
        name_suffix=None,
        distance_km=Decimal("650.00"),
        estimated_time_minutes=480,
        description="Directa nocturna",
        stops=[],
    )
    res = service.create_general_route(create_dto, current_user=admin_general)
    assert res.name == "Loja - Quito"
    assert res.origin_name == "Loja"
    assert res.destination_name == "Quito"
    assert res.is_active is True
    assert res.has_associations is False

    # 2. CP-66: Create with name_suffix
    create_with_suffix = RouteCreate(
        origin_id=loja.id,
        destination_id=cuenca.id,
        name_suffix="Vía Saraguro",
        distance_km=Decimal("210.50"),
        estimated_time_minutes=240,
    )
    res2 = service.create_general_route(create_with_suffix, current_user=admin_general)
    assert res2.name == "Loja - Cuenca Vía Saraguro"

    # 3. CP-75: Duplicated combination (origin, destination, distance) fails with 409
    dup_dto = RouteCreate(
        origin_id=loja.id,
        destination_id=quito.id,
        name_suffix="Otra",
        distance_km=Decimal("650.00"),
        estimated_time_minutes=500,
    )
    with pytest.raises(Exception) as exc:
        service.create_general_route(dup_dto, current_user=admin_general)
    assert exc.value.status_code == 409

    # 4. CP-76: Same origin and destination with different distance is allowed
    diff_dist_dto = RouteCreate(
        origin_id=loja.id,
        destination_id=quito.id,
        name_suffix="Vía Costanera",
        distance_km=Decimal("720.00"),
        estimated_time_minutes=550,
    )
    res3 = service.create_general_route(diff_dist_dto, current_user=admin_general)
    assert res3.id != res.id


def test_route_service_update_and_association_restriction(db_session, admin_general):
    service = RouteService(db_session)
    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")
    cuenca = make_locality(db_session, "Cuenca")
    ambato = make_locality(db_session, "Ambato")

    r = service.create_general_route(
        RouteCreate(
            origin_id=loja.id,
            destination_id=quito.id,
            distance_km=Decimal("650.00"),
            estimated_time_minutes=480,
            stops=[RouteStopInput(locality_id=cuenca.id, stop_order=1)],
        ),
        current_user=admin_general,
    )

    # CP-78: Edit all fields when route has NO associations
    update_dto = RouteUpdate(
        origin_id=loja.id,
        destination_id=ambato.id,
        name_suffix="Modificada",
        distance_km=Decimal("520.00"),
        estimated_time_minutes=400,
    )
    updated = service.update_general_route(r.id, update_dto, current_user=admin_general)
    assert updated.name == "Loja - Ambato Modificada"
    assert updated.destination_name == "Ambato"

    # Now associate a cooperative adoption
    coop = make_coop(db_session, "Coop Cariamanga", "1104609829002")
    adoption = CooperativaGeneralRoute(cooperativa_id=coop.id, route_id=r.id, is_active=True)
    db_session.add(adoption)
    db_session.commit()

    detail = service.get_route_detail(r.id)
    assert detail.has_associations is True

    # CP-79: Attempting to change origin or destination when route has associations raises 409
    restricted_update = RouteUpdate(destination_id=quito.id)
    with pytest.raises(Exception) as exc:
        service.update_general_route(r.id, restricted_update, current_user=admin_general)
    assert exc.value.status_code == 409
    assert "no pueden modificarse porque la ruta tiene asociaciones" in str(exc.value.detail)

    # But editing informative fields (distance, time, description) succeeds
    allowed_update = RouteUpdate(estimated_time_minutes=410, description="Nueva descripción")
    up2 = service.update_general_route(r.id, allowed_update, current_user=admin_general)
    assert up2.estimated_time_minutes == 410
    assert up2.description == "Nueva descripción"


def test_route_deactivation_cascade_and_notification(db_session, admin_general):
    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")
    coop = make_coop(db_session, "Coop Sur", "1104609829003")
    coop_admin = make_user(
        db_session,
        "coop.admin@sur.ec",
        "1710034065",
        [UserRole.ADMIN_COOPERATIVA],
        cooperativa_id=coop.id,
    )

    notif_service = NotificationService(db_session)
    service = RouteService(db_session, notification_service=notif_service)

    r = service.create_general_route(
        RouteCreate(
            origin_id=loja.id,
            destination_id=quito.id,
            distance_km=Decimal("650.00"),
            estimated_time_minutes=480,
        ),
        current_user=admin_general,
    )

    # Adopt route by cooperative
    adoption = CooperativaGeneralRoute(cooperativa_id=coop.id, route_id=r.id, is_active=True)
    db_session.add(adoption)
    db_session.commit()

    # CP-81: Deactivate general route -> cascade deactivates adoption & notifies admin
    res = service.update_general_route_estado(
        route_id=r.id,
        data=RouteEstadoUpdate(is_active=False),
        current_user=admin_general,
    )
    assert res.is_active is False

    # Check adoption is now inactive
    db_session.refresh(adoption)
    assert adoption.is_active is False

    # Check coop_admin received in-app notification
    notifs = notif_service.get_user_notifications(coop_admin.id)
    assert notifs.total == 1
    assert "Ruta General Desactivada" in notifs.items[0].title

    # CP-82: Reactivate general route -> adoption remains inactive
    res_reactivate = service.update_general_route_estado(
        route_id=r.id,
        data=RouteEstadoUpdate(is_active=True),
        current_user=admin_general,
    )
    assert res_reactivate.is_active is True
    db_session.refresh(adoption)
    assert adoption.is_active is False  # Remained false


def test_route_deactivation_guard_confirmation_required(db_session, admin_general):
    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")

    # Guard reporting active trips
    guard_with_trips = MockTripGuard(trips=2, reservations=5)
    service = RouteService(db_session, trip_guard=guard_with_trips)

    r = service.create_general_route(
        RouteCreate(
            origin_id=loja.id,
            destination_id=quito.id,
            distance_km=Decimal("650.00"),
            estimated_time_minutes=480,
        ),
        current_user=admin_general,
    )

    # Deactivating without confirm=True raises 409 REQUIRES_CONFIRMATION
    with pytest.raises(Exception) as exc:
        service.update_general_route_estado(
            route_id=r.id,
            data=RouteEstadoUpdate(is_active=False, confirm=False),
            current_user=admin_general,
        )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "REQUIRES_CONFIRMATION"

    # With confirm=True, deactivation succeeds
    res = service.update_general_route_estado(
        route_id=r.id,
        data=RouteEstadoUpdate(is_active=False, confirm=True),
        current_user=admin_general,
    )
    assert res.is_active is False


def test_rutas_generales_api_endpoints_and_permissions(client, db_session, admin_gen_token, admin_coop_data):
    coop, coop_admin, coop_token = admin_coop_data
    loja = make_locality(db_session, "Loja")
    quito = make_locality(db_session, "Quito")
    cuenca = make_locality(db_session, "Cuenca")

    # 1. Create general route as ADMIN_GENERAL -> 201
    create_payload = {
        "origin_id": loja.id,
        "destination_id": quito.id,
        "name_suffix": "Expreso",
        "distance_km": "650.00",
        "estimated_time_minutes": 480,
        "stops": [{"locality_id": cuenca.id, "stop_order": 1}],
    }
    resp = client.post("/api/v1/rutas-generales", json=create_payload, headers={"Authorization": admin_gen_token})
    assert resp.status_code == 201
    route_id = resp.json()["id"]

    # 2. ADMIN_COOPERATIVA forbidden to create general route -> 403
    resp = client.post("/api/v1/rutas-generales", json=create_payload, headers={"Authorization": coop_token})
    assert resp.status_code == 403

    # 3. List general routes with filters (CP-83)
    resp = client.get(f"/api/v1/rutas-generales?origin_id={loja.id}", headers={"Authorization": admin_gen_token})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    # 4. Shared detail route authorization (Decision 12)
    # ADMIN_GENERAL can view
    resp = client.get(f"/api/v1/rutas/{route_id}", headers={"Authorization": admin_gen_token})
    assert resp.status_code == 200

    # ADMIN_COOPERATIVA cannot view if route not adopted -> 403
    resp = client.get(f"/api/v1/rutas/{route_id}", headers={"Authorization": coop_token})
    assert resp.status_code == 403

    # Adopt route
    db_session.add(CooperativaGeneralRoute(cooperativa_id=coop.id, route_id=route_id, is_active=True))
    db_session.commit()

    # Now ADMIN_COOPERATIVA can view detail -> 200
    resp = client.get(f"/api/v1/rutas/{route_id}", headers={"Authorization": coop_token})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Loja - Quito Expreso"
