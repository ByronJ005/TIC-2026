from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload
from src.models.cooperativa import Cooperativa
from src.models.locality import Locality
from src.models.route import CooperativaGeneralRoute, Route, RouteStop


class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, route_id: int) -> Optional[Route]:
        return (
            self.db.query(Route)
            .options(
                joinedload(Route.origin),
                joinedload(Route.destination),
                joinedload(Route.cooperativa),
                selectinload(Route.stops).joinedload(RouteStop.locality),
            )
            .filter(Route.id == route_id)
            .first()
        )

    def get_by_id_for_update(self, route_id: int) -> Optional[Route]:
        return (
            self.db.query(Route)
            .filter(Route.id == route_id)
            .with_for_update()
            .first()
        )

    def exists_route(
        self,
        origin_id: int,
        destination_id: int,
        distance_km: Decimal,
        cooperativa_id: Optional[int] = None,
        exclude_id: Optional[int] = None,
    ) -> bool:
        q = self.db.query(Route.id).filter(
            Route.origin_id == origin_id,
            Route.destination_id == destination_id,
            Route.distance_km == distance_km,
        )
        if cooperativa_id is None:
            q = q.filter(Route.cooperativa_id.is_(None))
        else:
            q = q.filter(Route.cooperativa_id == cooperativa_id)

        if exclude_id is not None:
            q = q.filter(Route.id != exclude_id)

        return q.first() is not None

    def create(self, route: Route) -> Route:
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route

    def update(self, route: Route) -> Route:
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route

    def replace_stops(self, route_id: int, stops: List[RouteStop]) -> None:
        self.db.query(RouteStop).filter(RouteStop.route_id == route_id).delete()
        for stop in stops:
            stop.route_id = route_id
            self.db.add(stop)
        self.db.commit()

    def list_general_routes(
        self,
        origin_id: Optional[int] = None,
        destination_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Route], int]:
        q = self.db.query(Route).options(
            joinedload(Route.origin),
            joinedload(Route.destination),
        ).filter(Route.cooperativa_id.is_(None))

        if origin_id is not None:
            q = q.filter(Route.origin_id == origin_id)
        if destination_id is not None:
            q = q.filter(Route.destination_id == destination_id)
        if is_active is not None:
            q = q.filter(Route.is_active == is_active)

        total = q.count()
        items = q.order_by(Route.created_at.desc(), Route.id.desc()).offset(offset).limit(limit).all()
        return items, total

    def count_adoptions(self, route_id: int) -> int:
        return (
            self.db.query(func.count(CooperativaGeneralRoute.id))
            .filter(CooperativaGeneralRoute.route_id == route_id)
            .scalar()
            or 0
        )

    def deactivate_cascade_adoptions(self, route_id: int) -> List[int]:
        """
        Deactivates all active adoptions of this general route.
        Returns the list of affected cooperativa_ids.
        """
        active_adoptions = (
            self.db.query(CooperativaGeneralRoute)
            .filter(
                CooperativaGeneralRoute.route_id == route_id,
                CooperativaGeneralRoute.is_active.is_(True),
            )
            .all()
        )
        affected_coop_ids = [a.cooperativa_id for a in active_adoptions]
        if active_adoptions:
            for a in active_adoptions:
                a.is_active = False
            self.db.commit()
        return affected_coop_ids

    def list_specific_routes_grouped_by_cooperativa(self) -> List[Tuple[Cooperativa, List[Route]]]:
        """
        Returns all specific routes grouped by cooperative.
        """
        routes = (
            self.db.query(Route)
            .options(
                joinedload(Route.origin),
                joinedload(Route.destination),
                joinedload(Route.cooperativa),
            )
            .filter(Route.cooperativa_id.isnot(None))
            .order_by(Route.cooperativa_id, Route.created_at.desc())
            .all()
        )

        coops_map: Dict[int, Tuple[Cooperativa, List[Route]]] = {}
        for r in routes:
            if r.cooperativa_id not in coops_map:
                coops_map[r.cooperativa_id] = (r.cooperativa, [])
            coops_map[r.cooperativa_id][1].append(r)

        return list(coops_map.values())
