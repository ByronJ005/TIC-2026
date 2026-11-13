from typing import List, Optional, Tuple
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload
from src.models.cooperativa import Cooperativa


class CooperativaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cooperativa_id: int) -> Optional[Cooperativa]:
        return (
            self.db.query(Cooperativa)
            .options(selectinload(Cooperativa.administradores))
            .filter(Cooperativa.id == cooperativa_id)
            .first()
        )

    def get_by_id_for_update(self, cooperativa_id: int) -> Optional[Cooperativa]:
        return (
            self.db.query(Cooperativa)
            .options(selectinload(Cooperativa.administradores))
            .filter(Cooperativa.id == cooperativa_id)
            .with_for_update()
            .first()
        )

    def get_by_ruc(self, ruc: str) -> Optional[Cooperativa]:
        return (
            self.db.query(Cooperativa)
            .filter(Cooperativa.ruc == ruc.strip())
            .first()
        )

    def get_by_lower_name(self, name: str) -> Optional[Cooperativa]:
        return (
            self.db.query(Cooperativa)
            .filter(func.lower(Cooperativa.name) == name.strip().lower())
            .first()
        )

    def create(self, cooperativa: Cooperativa) -> Cooperativa:
        self.db.add(cooperativa)
        self.db.commit()
        self.db.refresh(cooperativa)
        return cooperativa

    def update(self, cooperativa: Cooperativa) -> Cooperativa:
        self.db.add(cooperativa)
        self.db.commit()
        self.db.refresh(cooperativa)
        return cooperativa

    def list_cooperativas(
        self,
        search: str = "",
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Cooperativa], int]:
        query = self.db.query(Cooperativa).options(
            selectinload(Cooperativa.administradores)
        )

        if is_active is not None:
            query = query.filter(Cooperativa.is_active == is_active)

        cleaned_search = search.strip()
        if cleaned_search:
            search_pattern = f"%{cleaned_search}%"
            query = query.filter(
                or_(
                    Cooperativa.name.ilike(search_pattern),
                    Cooperativa.ruc.ilike(search_pattern),
                )
            )

        total = query.count()
        cooperativas = (
            query.order_by(Cooperativa.name.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return cooperativas, total

