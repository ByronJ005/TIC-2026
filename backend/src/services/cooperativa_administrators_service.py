from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.user import User, UserRole
from src.repositories.cooperativa_repository import CooperativaRepository
from src.repositories.user_repository import UserRepository
from src.schemas.cooperativa_schemas import (
    ERROR_MAX_ADMINS_EXCEEDED,
    AdministradorSummary,
    EligibleAdminResponse,
)
from src.services.audit_service import AuditService
from src.services.cooperativa_service import (
    CODE_COOPERATIVA_INACTIVA,
    ERROR_COOPERATIVA_INACTIVE,
    ERROR_COOPERATIVA_NOT_FOUND,
)


class CooperativaAdministratorsService:
    def __init__(self, db: Session):
        self.db = db
        self.coop_repo = CooperativaRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    def list_eligible_administrators(
        self, cooperativa_id: int, search: str = ""
    ) -> List[EligibleAdminResponse]:
        if cooperativa_id != 0:
            coop = self.coop_repo.get_by_id(cooperativa_id)
            if not coop:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ERROR_COOPERATIVA_NOT_FOUND,
                )

        target_coop_id = cooperativa_id if cooperativa_id != 0 else None
        eligible_users = self.user_repo.list_eligible_cooperative_admins(
            cooperativa_id=target_coop_id,
            search=search,
        )

        return [
            EligibleAdminResponse(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                document_number=u.document_number,
                is_already_assigned=(u.cooperativa_id == cooperativa_id if cooperativa_id != 0 else False),
            )
            for u in eligible_users
        ]

    def get_administrators(
        self, cooperativa_id: int
    ) -> List[AdministradorSummary]:
        coop = self.coop_repo.get_by_id(cooperativa_id)
        if not coop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COOPERATIVA_NOT_FOUND,
            )
        admins = self.user_repo.get_cooperative_admins(cooperativa_id)
        return [AdministradorSummary.model_validate(a) for a in admins]

    def update_administrators(
        self,
        cooperativa_id: int,
        user_ids: List[int],
        current_user: User,
    ) -> List[AdministradorSummary]:
        # 1. Enforce limit <= 3
        deduped_ids = list(dict.fromkeys(user_ids))
        if len(deduped_ids) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MAX_ADMINS_EXCEEDED,
            )

        # 2. Lock cooperativa
        coop = self.coop_repo.get_by_id_for_update(cooperativa_id)
        if not coop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COOPERATIVA_NOT_FOUND,
            )

        # 3. Check active state
        if not coop.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": CODE_COOPERATIVA_INACTIVA,
                    "message": ERROR_COOPERATIVA_INACTIVE,
                },
            )

        # 4. Get current administrators
        current_admins = self.user_repo.get_cooperative_admins(cooperativa_id)
        current_admin_ids = {a.id for a in current_admins}

        # 5. Lock and validate target users
        target_users = []
        if deduped_ids:
            target_users = self.user_repo.get_users_by_ids_for_update(deduped_ids)
            if len(target_users) != len(deduped_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uno o más usuarios seleccionados no existen",
                )

            for user in target_users:
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El usuario {user.email} se encuentra inactivo",
                    )
                if UserRole.ADMIN_COOPERATIVA not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El usuario {user.email} no posee el rol de Administrador de cooperativa",
                    )
                if user.cooperativa_id is not None and user.cooperativa_id != cooperativa_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El usuario {user.email} ya está asignado a otra cooperativa",
                    )

        # 6. Apply diff
        # Remove unselected
        for admin in current_admins:
            if admin.id not in deduped_ids:
                admin.cooperativa_id = None
                self.db.add(admin)

        # Assign newly selected
        for user in target_users:
            if user.cooperativa_id != cooperativa_id:
                user.cooperativa_id = cooperativa_id
                self.db.add(user)

        self.db.commit()

        # 7. Audit log
        target_emails = [u.email for u in target_users]
        self.audit_service.record(
            user_id=current_user.id,
            action="ASSIGN_ADMINS",
            module="COOPERATIVAS",
            entity="COOPERATIVA",
            entity_id=cooperativa_id,
            result="SUCCESS",
            details=f"Administradores de '{coop.name}' actualizados: {target_emails}",
        )

        updated_admins = self.user_repo.get_cooperative_admins(cooperativa_id)
        return [AdministradorSummary.model_validate(a) for a in updated_admins]

