from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.models.route import CooperativaGeneralRoute, Route


class CooperativaGeneralRouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, adoption_id: int) -> Optional[CooperativaGeneralRoute]:
        return (
            self.db.query(CooperativaGeneralRoute)
            .options(
                joinedload(CooperativaGeneralRoute.route).joinedload(Route.origin),
                joinedload(CooperativaGeneralRoute.route).joinedload(Route.destination),
            )
            .filter(CooperativaGeneralRoute.id == adoption_id)
            .first()
        )

    def get_by_cooperativa_and_route(
        self,
        cooperativa_id: int,
        route_id: int,
    ) -> Optional[CooperativaGeneralRoute]:
        return (
            self.db.query(CooperativaGeneralRoute)
            .filter(
                CooperativaGeneralRoute.cooperativa_id == cooperativa_id,
                CooperativaGeneralRoute.route_id == route_id,
            )
            .first()
        )

    def list_by_cooperativa(self, cooperativa_id: int) -> List[CooperativaGeneralRoute]:
        return (
            self.db.query(CooperativaGeneralRoute)
            .options(
                joinedload(CooperativaGeneralRoute.route).joinedload(Route.origin),
                joinedload(CooperativaGeneralRoute.route).joinedload(Route.destination),
            )
            .filter(CooperativaGeneralRoute.cooperativa_id == cooperativa_id)
            .order_by(CooperativaGeneralRoute.created_at.desc())
            .all()
        )

    def list_available_general_routes(self, cooperativa_id: int) -> List[Route]:
        """
        Returns active general routes that have NOT been adopted by this cooperative.
        """
        adopted_route_ids = (
            self.db.query(CooperativaGeneralRoute.route_id)
            .filter(CooperativaGeneralRoute.cooperativa_id == cooperativa_id)
        )

        return (
            self.db.query(Route)
            .options(
                joinedload(Route.origin),
                joinedload(Route.destination),
            )
            .filter(
                Route.cooperativa_id.is_(None),
                Route.is_active.is_(True),
                Route.id.not_in(adopted_route_ids),
            )
            .order_by(Route.name.asc())
            .all()
        )

    def create(self, adoption: CooperativaGeneralRoute) -> CooperativaGeneralRoute:
        self.db.add(adoption)
        self.db.commit()
        self.db.refresh(adoption)
        return adoption

    def update(self, adoption: CooperativaGeneralRoute) -> CooperativaGeneralRoute:
        self.db.add(adoption)
        self.db.commit()
        self.db.refresh(adoption)
        return adoption
