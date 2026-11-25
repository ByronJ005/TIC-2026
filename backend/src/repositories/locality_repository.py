from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.locality import Locality


class LocalityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, locality_id: int) -> Optional[Locality]:
        return self.db.query(Locality).filter(Locality.id == locality_id).first()

    def get_by_lower_name(self, name: str) -> Optional[Locality]:
        clean_name = " ".join(name.strip().split()).lower()
        return (
            self.db.query(Locality)
            .filter(func.lower(Locality.name) == clean_name)
            .first()
        )

    def search_localities(
        self,
        query: str = "",
        is_active: Optional[bool] = True,
        limit: int = 100,
    ) -> List[Locality]:
        q = self.db.query(Locality)
        if is_active is not None:
            q = q.filter(Locality.is_active == is_active)
        if query and query.strip():
            clean_q = f"%{query.strip()}%"
            q = q.filter(Locality.name.ilike(clean_q))
        return q.order_by(Locality.name.asc()).limit(limit).all()

    def create(self, locality: Locality) -> Locality:
        self.db.add(locality)
        self.db.commit()
        self.db.refresh(locality)
        return locality
