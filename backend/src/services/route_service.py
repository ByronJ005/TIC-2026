import math
from typing import Any, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.locality import Locality
from src.models.route import Route, RouteStop
from src.models.user import User, UserRole
from src.repositories.locality_repository import LocalityRepository
from src.repositories.route_repository import RouteRepository
from src.schemas.route_schemas import (
    CooperativaRoutesGroup,
    RouteCreate,
    RouteDetailResponse,
    RouteEstadoUpdate,
    RoutePaginationResponse,
    RouteResponse,
    RouteStopResponse,
    RouteUpdate,
)
from src.schemas.validators import (
    ERROR_ROUTE_DUPLICATED,
    ERROR_ROUTE_ORIGIN_DEST_MUTATION_RESTRICTED,
)
from src.services.audit_service import AuditService
from src.services.notification_service import NotificationService
from src.services.trip_guard import TripReservationGuard, get_trip_guard


class RouteService:
    def __init__(
        self,
        db: Session,
        trip_guard: Optional[TripReservationGuard] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self.db = db
        self.repository = RouteRepository(db)
        self.locality_repo = LocalityRepository(db)
        self.audit_service = AuditService(db)
        self.trip_guard = trip_guard or get_trip_guard()
        self.notification_service = notification_service or NotificationService(db)

    def _resolve_route_name(
        self,
        origin_name: str,
        destination_name: str,
        suffix: Optional[str] = None,
    ) -> str:
        base = f"{origin_name} - {destination_name}"
        if suffix and suffix.strip():
            return f"{base} {suffix.strip()}"
        return base

    def _check_associations(self, route_id: int) -> bool:
        """
        Returns True if the route has associations:
        - adoptions by cooperatives (for general routes)
        - active trips or reservations (via trip_guard)
        """
        adoptions_count = self.repository.count_adoptions(route_id)
        if adoptions_count > 0:
            return True
        report = self.trip_guard.check_active_trips_or_reservations(route_id)
        return report.has_active_trips_or_reservations

    def create_general_route(self, data: RouteCreate, current_user: User) -> RouteDetailResponse:
        # 1. Validate localities exist and are active
        origin = self.locality_repo.get_by_id(data.origin_id)
        dest = self.locality_repo.get_by_id(data.destination_id)
        if not origin or not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El origen o el destino especificado no existe",
            )

        # 2. Check uniqueness (origin_id, destination_id, distance_km) for general routes
        if self.repository.exists_route(
            origin_id=data.origin_id,
            destination_id=data.destination_id,
            distance_km=data.distance_km,
            cooperativa_id=None,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR_ROUTE_DUPLICATED,
            )

        # 3. Build route model
        full_name = self._resolve_route_name(origin.name, dest.name, data.name_suffix)
        new_route = Route(
            cooperativa_id=None,
            origin_id=data.origin_id,
            destination_id=data.destination_id,
            name=full_name,
            name_suffix=data.name_suffix,
            distance_km=data.distance_km,
            estimated_time_minutes=data.estimated_time_minutes,
            description=data.description,
            is_active=True,
        )
        created = self.repository.create(new_route)

        # 4. Handle stops
        stops_to_save = []
        if data.stops:
            for s in data.stops:
                stop_loc = self.locality_repo.get_by_id(s.locality_id)
                if not stop_loc:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"La parada con ID {s.locality_id} no existe",
                    )
                stops_to_save.append(
                    RouteStop(locality_id=s.locality_id, stop_order=s.stop_order)
                )
            self.repository.replace_stops(created.id, stops_to_save)

        # 5. Audit
        self.audit_service.record(
            user_id=current_user.id,
            action="CREATE_ROUTE",
            module="RUTAS",
            entity="ROUTE",
            entity_id=created.id,
            result="SUCCESS",
            details=f"Ruta general '{created.name}' creada exitosamente",
        )

        return self.get_route_detail(created.id)

    def update_general_route(
        self,
        route_id: int,
        data: RouteUpdate,
        current_user: User,
    ) -> RouteDetailResponse:
        route = self.repository.get_by_id_for_update(route_id)
        if not route or route.cooperativa_id is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta general no encontrada",
            )

        has_associations = self._check_associations(route.id)

        # Check origin/destination mutation
        new_origin_id = data.origin_id if data.origin_id is not None else route.origin_id
        new_destination_id = data.destination_id if data.destination_id is not None else route.destination_id

        if has_associations and (
            new_origin_id != route.origin_id or new_destination_id != route.destination_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR_ROUTE_ORIGIN_DEST_MUTATION_RESTRICTED,
            )

        # Check uniqueness if origin, destination, or distance changed
        new_distance = data.distance_km if data.distance_km is not None else route.distance_km
        if (
            new_origin_id != route.origin_id
            or new_destination_id != route.destination_id
            or new_distance != route.distance_km
        ):
            if self.repository.exists_route(
                origin_id=new_origin_id,
                destination_id=new_destination_id,
                distance_km=new_distance,
                cooperativa_id=None,
                exclude_id=route.id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ERROR_ROUTE_DUPLICATED,
                )

        origin = self.locality_repo.get_by_id(new_origin_id)
        dest = self.locality_repo.get_by_id(new_destination_id)
        if not origin or not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El origen o destino especificado no existe",
            )

        suffix = data.name_suffix if data.name_suffix is not None else route.name_suffix
        route.name = self._resolve_route_name(origin.name, dest.name, suffix)
        route.name_suffix = suffix
        route.origin_id = new_origin_id
        route.destination_id = new_destination_id
        route.distance_km = new_distance
        if data.estimated_time_minutes is not None:
            route.estimated_time_minutes = data.estimated_time_minutes
        if data.description is not None:
            route.description = data.description

        updated = self.repository.update(route)

        if data.stops is not None:
            stops_to_save = []
            for s in data.stops:
                stop_loc = self.locality_repo.get_by_id(s.locality_id)
                if not stop_loc:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"La parada con ID {s.locality_id} no existe",
                    )
                stops_to_save.append(
                    RouteStop(locality_id=s.locality_id, stop_order=s.stop_order)
                )
            self.repository.replace_stops(updated.id, stops_to_save)

        self.audit_service.record(
            user_id=current_user.id,
            action="UPDATE_ROUTE",
            module="RUTAS",
            entity="ROUTE",
            entity_id=updated.id,
            result="SUCCESS",
            details=f"Ruta general '{updated.name}' actualizada",
        )

        return self.get_route_detail(updated.id)

    def update_general_route_estado(
        self,
        route_id: int,
        data: RouteEstadoUpdate,
        current_user: User,
    ) -> RouteDetailResponse:
        route = self.repository.get_by_id_for_update(route_id)
        if not route or route.cooperativa_id is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta general no encontrada",
            )

        # Deactivation flow
        if not data.is_active and route.is_active:
            # Check trips / reservations guard
            report = self.trip_guard.check_active_trips_or_reservations(route.id)
            if report.has_active_trips_or_reservations and not data.confirm:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "REQUIRES_CONFIRMATION",
                        "message": "La ruta tiene turnos o pasajes reservados activos. Confirme para desactivar.",
                        "report": report.model_dump(),
                    },
                )

            # Deactivate route
            route.is_active = False
            self.repository.update(route)

            # Cascade deactivate adoptions
            affected_coop_ids = self.repository.deactivate_cascade_adoptions(route.id)

            # Notify active admins of affected cooperatives
            if affected_coop_ids:
                admin_users = (
                    self.db.query(User)
                    .filter(
                        User.cooperativa_id.in_(affected_coop_ids),
                        User.is_active.is_(True),
                    )
                    .all()
                )
                admin_ids = [
                    u.id
                    for u in admin_users
                    if any(
                        (r.value if hasattr(r, "value") else str(r)) == UserRole.ADMIN_COOPERATIVA.value
                        for r in (u.roles or [])
                    )
                ]
                if admin_ids:
                    title = "Ruta General Desactivada"
                    msg = (
                        f"La ruta general '{route.name}' ha sido desactivada por la administración del terminal. "
                        "Sus asociaciones han sido deshabilitadas."
                    )
                    self.notification_service.notify_users(
                        user_ids=admin_ids,
                        title=title,
                        message=msg,
                        email_subject=f"Aviso Terminal: Ruta '{route.name}' Desactivada",
                        email_body=msg,
                    )

            self.audit_service.record(
                user_id=current_user.id,
                action="DEACTIVATE_ROUTE",
                module="RUTAS",
                entity="ROUTE",
                entity_id=route.id,
                result="SUCCESS",
                details=f"Ruta general '{route.name}' desactivada con cascada",
            )

        elif data.is_active and not route.is_active:
            # Reactivation: only reactivates the general route, adoptions remain inactive until coops enable them
            route.is_active = True
            self.repository.update(route)
            self.audit_service.record(
                user_id=current_user.id,
                action="ACTIVATE_ROUTE",
                module="RUTAS",
                entity="ROUTE",
                entity_id=route.id,
                result="SUCCESS",
                details=f"Ruta general '{route.name}' reactivada",
            )

        return self.get_route_detail(route.id)

    def get_route_detail(self, route_id: int) -> RouteDetailResponse:
        route = self.repository.get_by_id(route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta no encontrada",
            )

        has_associations = self._check_associations(route.id)
        stops_resp = [
            RouteStopResponse(
                id=s.id,
                route_id=s.route_id,
                locality_id=s.locality_id,
                stop_order=s.stop_order,
                locality_name=s.locality.name if s.locality else None,
            )
            for s in route.stops
        ]

        return RouteDetailResponse(
            id=route.id,
            cooperativa_id=route.cooperativa_id,
            cooperativa_name=route.cooperativa.name if route.cooperativa else None,
            origin_id=route.origin_id,
            destination_id=route.destination_id,
            origin_name=route.origin.name if route.origin else None,
            destination_name=route.destination.name if route.destination else None,
            name=route.name,
            name_suffix=route.name_suffix,
            distance_km=route.distance_km,
            estimated_time_minutes=route.estimated_time_minutes,
            description=route.description,
            is_active=route.is_active,
            created_at=route.created_at,
            updated_at=route.updated_at,
            stops=stops_resp,
            has_associations=has_associations,
        )

    def list_general_routes(
        self,
        origin_id: Optional[int] = None,
        destination_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 10,
    ) -> RoutePaginationResponse:
        page = max(1, page)
        size = min(max(1, size), 100)
        offset = (page - 1) * size

        items, total = self.repository.list_general_routes(
            origin_id=origin_id,
            destination_id=destination_id,
            is_active=is_active,
            offset=offset,
            limit=size,
        )
        total_pages = math.ceil(total / size) if size > 0 else 0

        routes_resp = []
        for r in items:
            routes_resp.append(
                RouteResponse(
                    id=r.id,
                    cooperativa_id=r.cooperativa_id,
                    origin_id=r.origin_id,
                    destination_id=r.destination_id,
                    origin_name=r.origin.name if r.origin else None,
                    destination_name=r.destination.name if r.destination else None,
                    name=r.name,
                    name_suffix=r.name_suffix,
                    distance_km=r.distance_km,
                    estimated_time_minutes=r.estimated_time_minutes,
                    description=r.description,
                    is_active=r.is_active,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )

        return RoutePaginationResponse(
            items=routes_resp,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    def list_specific_routes_grouped(self) -> List[CooperativaRoutesGroup]:
        groups_raw = self.repository.list_specific_routes_grouped_by_cooperativa()
        result = []
        for coop, routes in groups_raw:
            coop_routes_resp = [
                RouteResponse(
                    id=r.id,
                    cooperativa_id=r.cooperativa_id,
                    origin_id=r.origin_id,
                    destination_id=r.destination_id,
                    origin_name=r.origin.name if r.origin else None,
                    destination_name=r.destination.name if r.destination else None,
                    name=r.name,
                    name_suffix=r.name_suffix,
                    distance_km=r.distance_km,
                    estimated_time_minutes=r.estimated_time_minutes,
                    description=r.description,
                    is_active=r.is_active,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
                for r in routes
            ]
            result.append(
                CooperativaRoutesGroup(
                    cooperativa_id=coop.id,
                    cooperativa_name=coop.name,
                    routes=coop_routes_resp,
                )
            )
        return result
