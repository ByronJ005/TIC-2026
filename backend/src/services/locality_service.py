from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.locality import Locality
from src.repositories.locality_repository import LocalityRepository
from src.schemas.locality_schemas import LocalityCreate
from src.schemas.validators import (
    ERROR_LOCALITY_NAME_EMPTY,
    ERROR_LOCALITY_NAME_TOO_LONG,
    LOCALITY_NAME_MAX_LENGTH,
    normalize_locality_name,
)


class LocalityService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = LocalityRepository(db)

    def get_by_id(self, locality_id: int) -> Locality:
        locality = self.repository.get_by_id(locality_id)
        if not locality:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localidad no encontrada",
            )
        return locality

    def search(self, query: str = "") -> List[Locality]:
        return self.repository.search_localities(query=query, is_active=True)

    def get_or_create(self, data: LocalityCreate) -> Tuple[Locality, bool]:
        """
        Idempotently gets or creates a locality.
        Returns (locality, created) where created is True if newly created, False if existing.
        """
        normalized_name = normalize_locality_name(data.name)
        if not normalized_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_LOCALITY_NAME_EMPTY,
            )
        if len(normalized_name) > LOCALITY_NAME_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_LOCALITY_NAME_TOO_LONG,
            )

        existing = self.repository.get_by_lower_name(normalized_name)
        if existing:
            return existing, False

        new_locality = Locality(name=normalized_name, is_active=True)
        created = self.repository.create(new_locality)
        return created, True
