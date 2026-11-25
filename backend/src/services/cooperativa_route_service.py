from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.route import CooperativaGeneralRoute, Route, RouteStop
from src.models.user import User
from src.repositories.cooperativa_general_route_repository import (
    CooperativaGeneralRouteRepository,
)
from src.repositories.locality_repository import LocalityRepository
from src.repositories.route_repository import RouteRepository
from src.schemas.route_schemas import (
    AdoptGeneralRouteEstadoUpdate,
    CooperativaGeneralRouteResponse,
    RouteCreate,
    RouteDetailResponse,
    RouteEstadoUpdate,
    RouteResponse,
    RouteStopResponse,
    RouteUpdate,
)
from src.schemas.validators import (
    ERROR_COOP_ROUTE_DUPLICATED,
    ERROR_ROUTE_ALREADY_ADOPTED,
    ERROR_ROUTE_GENERAL_INACTIVE,
    ERROR_ROUTE_ORIGIN_DEST_MUTATION_RESTRICTED,
)
from src.services.audit_service import AuditService
from src.services.notification_service import NotificationService
from src.services.trip_guard import TripReservationGuard, get_trip_guard


class CooperativaRouteService:
    def __init__(
        self,
        db: Session,
        trip_guard: Optional[TripReservationGuard] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self.db = db
        self.adoption_repo = CooperativaGeneralRouteRepository(db)
        self.route_repo = RouteRepository(db)
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

    # -------------------------------------------------------------
    # Adopted General Routes
    # -------------------------------------------------------------
    def list_available_general_routes(self, cooperativa_id: int) -> List[RouteResponse]:
        routes = self.adoption_repo.list_available_general_routes(cooperativa_id)
        return [
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

    def list_adopted_general_routes(
        self, cooperativa_id: int
    ) -> List[CooperativaGeneralRouteResponse]:
        adoptions = self.adoption_repo.list_by_cooperativa(cooperativa_id)
        result = []
        for a in adoptions:
            r = a.route
            r_resp = RouteResponse(
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
            result.append(
                CooperativaGeneralRouteResponse(
                    id=a.id,
                    cooperativa_id=a.cooperativa_id,
                    route_id=a.route_id,
                    is_active=a.is_active,
                    created_at=a.created_at,
                    updated_at=a.updated_at,
                    route=r_resp,
                )
            )
        return result

    def adopt_general_routes(
        self,
        cooperativa_id: int,
        route_ids: List[int],
        current_user: User,
    ) -> List[CooperativaGeneralRouteResponse]:
        if not route_ids:
            return []

        # Validate that each route exists, is a general route, and is active
        created_adoptions = []
        for rid in route_ids:
            route = self.route_repo.get_by_id(rid)
            if not route or route.cooperativa_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"La ruta general con ID {rid} no existe",
                )
            if not route.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La ruta general '{route.name}' está inactiva y no puede ser adoptada",
                )

            # Check if already adopted
            existing = self.adoption_repo.get_by_cooperativa_and_route(cooperativa_id, rid)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ERROR_ROUTE_ALREADY_ADOPTED,
                )

            new_adoption = CooperativaGeneralRoute(
                cooperativa_id=cooperativa_id,
                route_id=rid,
                is_active=True,
            )
            saved = self.adoption_repo.create(new_adoption)
            created_adoptions.append(saved)

            self.audit_service.record(
                user_id=current_user.id,
                action="ADOPT_ROUTE",
                module="RUTAS",
                entity="COOPERATIVA_GENERAL_ROUTE",
                entity_id=saved.id,
                result="SUCCESS",
                details=f"Ruta general '{route.name}' adoptada por cooperativa {cooperativa_id}",
            )

        return self.list_adopted_general_routes(cooperativa_id)

    def update_adoption_estado(
        self,
        cooperativa_id: int,
        adoption_id: int,
        data: AdoptGeneralRouteEstadoUpdate,
        current_user: User,
    ) -> CooperativaGeneralRouteResponse:
        adoption = self.adoption_repo.get_by_id(adoption_id)
        if not adoption or adoption.cooperativa_id != cooperativa_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asociación de ruta general no encontrada",
            )

        # Reactivation rule: general route must be active
        if data.is_active and not adoption.is_active:
            if not adoption.route.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ERROR_ROUTE_GENERAL_INACTIVE,
                )
            adoption.is_active = True
            self.adoption_repo.update(adoption)

            self.audit_service.record(
                user_id=current_user.id,
                action="TOGGLE_ADOPTION",
                module="RUTAS",
                entity="COOPERATIVA_GENERAL_ROUTE",
                entity_id=adoption.id,
                result="SUCCESS",
                details=f"Ruta adoptada '{adoption.route.name}' reactivada en cooperativa",
            )

        # Deactivation rule: check guard
        elif not data.is_active and adoption.is_active:
            report = self.trip_guard.check_active_trips_or_reservations(adoption.route_id)
            if report.has_active_trips_or_reservations and not data.confirm:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "REQUIRES_CONFIRMATION",
                        "message": "La ruta tiene turnos o pasajes reservados activos. Confirme para desactivar.",
                        "report": report.model_dump(),
                    },
                )

            adoption.is_active = False
            self.adoption_repo.update(adoption)

            self.audit_service.record(
                user_id=current_user.id,
                action="TOGGLE_ADOPTION",
                module="RUTAS",
                entity="COOPERATIVA_GENERAL_ROUTE",
                entity_id=adoption.id,
                result="SUCCESS",
                details=f"Ruta adoptada '{adoption.route.name}' desactivada en cooperativa",
            )

        r = adoption.route
        r_resp = RouteResponse(
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
        return CooperativaGeneralRouteResponse(
            id=adoption.id,
            cooperativa_id=adoption.cooperativa_id,
            route_id=adoption.route_id,
            is_active=adoption.is_active,
            created_at=adoption.created_at,
            updated_at=adoption.updated_at,
            route=r_resp,
        )

    # -------------------------------------------------------------
    # Specific Routes ("Mis Rutas")
    # -------------------------------------------------------------
    def list_specific_routes(self, cooperativa_id: int) -> List[RouteResponse]:
        routes = (
            self.db.query(Route)
            .filter(Route.cooperativa_id == cooperativa_id)
            .order_by(Route.created_at.desc())
            .all()
        )
        return [
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

    def create_specific_route(
        self,
        cooperativa_id: int,
        data: RouteCreate,
        current_user: User,
    ) -> RouteDetailResponse:
        origin = self.locality_repo.get_by_id(data.origin_id)
        dest = self.locality_repo.get_by_id(data.destination_id)
        if not origin or not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El origen o el destino especificado no existe",
            )

        # Uniqueness per cooperative
        if self.route_repo.exists_route(
            origin_id=data.origin_id,
            destination_id=data.destination_id,
            distance_km=data.distance_km,
            cooperativa_id=cooperativa_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR_COOP_ROUTE_DUPLICATED,
            )

        full_name = self._resolve_route_name(origin.name, dest.name, data.name_suffix)
        new_route = Route(
            cooperativa_id=cooperativa_id,
            origin_id=data.origin_id,
            destination_id=data.destination_id,
            name=full_name,
            name_suffix=data.name_suffix,
            distance_km=data.distance_km,
            estimated_time_minutes=data.estimated_time_minutes,
            description=data.description,
            is_active=True,
        )
        created = self.route_repo.create(new_route)

        if data.stops:
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
            self.route_repo.replace_stops(created.id, stops_to_save)

        self.audit_service.record(
            user_id=current_user.id,
            action="CREATE_ROUTE",
            module="RUTAS",
            entity="ROUTE",
            entity_id=created.id,
            result="SUCCESS",
            details=f"Ruta específica '{created.name}' creada para cooperativa {cooperativa_id}",
        )

        return self.get_specific_route_detail(cooperativa_id, created.id)

    def update_specific_route(
        self,
        cooperativa_id: int,
        route_id: int,
        data: RouteUpdate,
        current_user: User,
    ) -> RouteDetailResponse:
        route = self.route_repo.get_by_id_for_update(route_id)
        if not route or route.cooperativa_id != cooperativa_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta específica no encontrada",
            )

        # Check trips guard
        report = self.trip_guard.check_active_trips_or_reservations(route.id)
        has_associations = report.has_active_trips_or_reservations

        new_origin_id = data.origin_id if data.origin_id is not None else route.origin_id
        new_destination_id = (
            data.destination_id if data.destination_id is not None else route.destination_id
        )

        if has_associations and (
            new_origin_id != route.origin_id or new_destination_id != route.destination_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR_ROUTE_ORIGIN_DEST_MUTATION_RESTRICTED,
            )

        new_distance = data.distance_km if data.distance_km is not None else route.distance_km
        if (
            new_origin_id != route.origin_id
            or new_destination_id != route.destination_id
            or new_distance != route.distance_km
        ):
            if self.route_repo.exists_route(
                origin_id=new_origin_id,
                destination_id=new_destination_id,
                distance_km=new_distance,
                cooperativa_id=cooperativa_id,
                exclude_id=route.id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ERROR_COOP_ROUTE_DUPLICATED,
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

        updated = self.route_repo.update(route)

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
            self.route_repo.replace_stops(updated.id, stops_to_save)

        self.audit_service.record(
            user_id=current_user.id,
            action="UPDATE_ROUTE",
            module="RUTAS",
            entity="ROUTE",
            entity_id=updated.id,
            result="SUCCESS",
            details=f"Ruta específica '{updated.name}' actualizada",
        )

        return self.get_specific_route_detail(cooperativa_id, updated.id)

    def update_specific_route_estado(
        self,
        cooperativa_id: int,
        route_id: int,
        data: RouteEstadoUpdate,
        current_user: User,
    ) -> RouteDetailResponse:
        route = self.route_repo.get_by_id_for_update(route_id)
        if not route or route.cooperativa_id != cooperativa_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta específica no encontrada",
            )

        if not data.is_active and route.is_active:
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
            route.is_active = False
            self.route_repo.update(route)

            self.audit_service.record(
                user_id=current_user.id,
                action="DEACTIVATE_ROUTE",
                module="RUTAS",
                entity="ROUTE",
                entity_id=route.id,
                result="SUCCESS",
                details=f"Ruta específica '{route.name}' desactivada",
            )

        elif data.is_active and not route.is_active:
            route.is_active = True
            self.route_repo.update(route)

            self.audit_service.record(
                user_id=current_user.id,
                action="ACTIVATE_ROUTE",
                module="RUTAS",
                entity="ROUTE",
                entity_id=route.id,
                result="SUCCESS",
                details=f"Ruta específica '{route.name}' reactivada",
            )

        return self.get_specific_route_detail(cooperativa_id, route.id)

    def get_specific_route_detail(
        self, cooperativa_id: int, route_id: int
    ) -> RouteDetailResponse:
        route = self.route_repo.get_by_id(route_id)
        if not route or route.cooperativa_id != cooperativa_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta específica no encontrada",
            )

        report = self.trip_guard.check_active_trips_or_reservations(route.id)
        has_associations = report.has_active_trips_or_reservations

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
