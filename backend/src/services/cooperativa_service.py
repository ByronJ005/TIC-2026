import math
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.cooperativa import Cooperativa
from src.models.user import User
from src.repositories.cooperativa_repository import CooperativaRepository
from src.schemas.cooperativa_schemas import (
    CooperativaCreate,
    CooperativaEstadoUpdate,
    CooperativaPaginationResponse,
    CooperativaResponse,
    CooperativaUpdate,
)
from src.services.audit_service import AuditService

ERROR_RUC_DUPLICATED = "Ya existe una cooperativa registrada con este RUC"
ERROR_NAME_DUPLICATED = "Ya existe una cooperativa registrada con este nombre"
ERROR_COOPERATIVA_NOT_FOUND = "Cooperativa no encontrada"
ERROR_COOPERATIVA_INACTIVE = "La cooperativa ha sido desactivada"
CODE_COOPERATIVA_INACTIVA = "COOPERATIVA_INACTIVA"


class CooperativaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CooperativaRepository(db)
        self.audit_service = AuditService(db)

    def create_cooperativa(
        self, data: CooperativaCreate, current_user: User
    ) -> CooperativaResponse:
        # 1. Unicidad de RUC
        existing_by_ruc = self.repository.get_by_ruc(data.ruc)
        if existing_by_ruc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_RUC_DUPLICATED,
            )

        # 2. Unicidad de Nombre (case-insensitive)
        existing_by_name = self.repository.get_by_lower_name(data.name)
        if existing_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_NAME_DUPLICATED,
            )

        # 3. Crear cooperativa en estado Activa
        cooperativa = Cooperativa(
            name=data.name.strip(),
            ruc=data.ruc.strip(),
            address=data.address.strip() if data.address else None,
            phone=data.phone.strip() if data.phone else None,
            email=data.email.strip().lower() if data.email else None,
            logo_url=data.logo_url.strip() if data.logo_url else None,
            is_active=True,
        )
        created = self.repository.create(cooperativa)

        # 4. Auditoría
        self.audit_service.record(
            user_id=current_user.id,
            action="CREATE",
            module="COOPERATIVAS",
            entity="COOPERATIVA",
            entity_id=created.id,
            result="SUCCESS",
            details=f"Cooperativa '{created.name}' registrada con RUC {created.ruc}",
        )

        return CooperativaResponse.model_validate(created)

    def get_cooperativa_by_id(self, cooperativa_id: int) -> CooperativaResponse:
        cooperativa = self.repository.get_by_id(cooperativa_id)
        if not cooperativa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COOPERATIVA_NOT_FOUND,
            )
        return CooperativaResponse.model_validate(cooperativa)

    def list_cooperativas(
        self,
        search: str = "",
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 10,
    ) -> CooperativaPaginationResponse:
        offset = (page - 1) * size
        items, total = self.repository.list_cooperativas(
            search=search,
            is_active=is_active,
            offset=offset,
            limit=size,
        )
        total_pages = math.ceil(total / size) if size > 0 else 0

        return CooperativaPaginationResponse(
            items=[CooperativaResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    def update_cooperativa(
        self,
        cooperativa_id: int,
        data: CooperativaUpdate,
        current_user: User,
    ) -> CooperativaResponse:
        cooperativa = self.repository.get_by_id(cooperativa_id)
        if not cooperativa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COOPERATIVA_NOT_FOUND,
            )

        # Regla de concurrencia: si está inactiva, rechazar edición
        if not cooperativa.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": CODE_COOPERATIVA_INACTIVA,
                    "message": ERROR_COOPERATIVA_INACTIVE,
                },
            )

        # Si se actualiza el nombre, validar unicidad
        if data.name and data.name.strip().lower() != cooperativa.name.lower():
            existing = self.repository.get_by_lower_name(data.name)
            if existing and existing.id != cooperativa.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_NAME_DUPLICATED,
                )
            cooperativa.name = data.name.strip()

        if data.address is not None:
            cooperativa.address = data.address.strip() if data.address else None
        if data.phone is not None:
            cooperativa.phone = data.phone.strip() if data.phone else None
        if data.email is not None:
            cooperativa.email = data.email.strip().lower() if data.email else None
        if data.logo_url is not None:
            cooperativa.logo_url = data.logo_url.strip() if data.logo_url else None

        updated = self.repository.update(cooperativa)

        # Auditoría
        self.audit_service.record(
            user_id=current_user.id,
            action="UPDATE",
            module="COOPERATIVAS",
            entity="COOPERATIVA",
            entity_id=updated.id,
            result="SUCCESS",
            details=f"Cooperativa '{updated.name}' actualizada",
        )

        return CooperativaResponse.model_validate(updated)

    def update_estado(
        self,
        cooperativa_id: int,
        data: CooperativaEstadoUpdate,
        current_user: User,
    ) -> CooperativaResponse:
        cooperativa = self.repository.get_by_id(cooperativa_id)
        if not cooperativa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COOPERATIVA_NOT_FOUND,
            )

        cooperativa.is_active = data.is_active
        updated = self.repository.update(cooperativa)

        # Auditoría
        action_name = "ACTIVATE" if data.is_active else "DEACTIVATE"
        status_text = "activada" if data.is_active else "desactivada"
        self.audit_service.record(
            user_id=current_user.id,
            action=action_name,
            module="COOPERATIVAS",
            entity="COOPERATIVA",
            entity_id=updated.id,
            result="SUCCESS",
            details=f"Cooperativa '{updated.name}' {status_text}",
        )

        return CooperativaResponse.model_validate(updated)

