import math
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user import User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import (
    UserListQuery,
    UserPaginationResponse,
    UserResponse,
    UserRolesUpdate,
    UserStatusUpdate,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def list_users(self, query: UserListQuery) -> UserPaginationResponse:
        offset = (query.page - 1) * query.size
        users, total = self.user_repo.list_users(
            search=query.search,
            include_inactive=query.include_inactive,
            offset=offset,
            limit=query.size,
        )
        total_pages = math.ceil(total / query.size) if total > 0 else 0
        items = [UserResponse.model_validate(u) for u in users]
        return UserPaginationResponse(
            items=items,
            total=total,
            page=query.page,
            size=query.size,
            pages=total_pages,
        )

    def update_user_roles(
        self,
        target_user_id: int,
        roles_data: UserRolesUpdate,
        current_user: User,
    ) -> UserResponse:
        if current_user.id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se permite modificar los roles de la propia cuenta administrativa",
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        roles = list(roles_data.roles)
        if UserRole.PASAJERO not in roles:
            roles.append(UserRole.PASAJERO)

        updated_user = self.user_repo.update_roles(target_user, roles)
        return UserResponse.model_validate(updated_user)

    def update_user_status(
        self,
        target_user_id: int,
        status_data: UserStatusUpdate,
        current_user: User,
    ) -> UserResponse:
        if current_user.id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se permite cambiar el estado de la propia cuenta administrativa",
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        if target_user.is_active == status_data.is_active:
            msg = (
                "El usuario ya se encuentra activo"
                if status_data.is_active
                else "El usuario ya se encuentra inactivo"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )

        updated_user = self.user_repo.update_status(
            target_user, status_data.is_active
        )
        return UserResponse.model_validate(updated_user)

