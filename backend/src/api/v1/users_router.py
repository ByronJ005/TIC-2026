from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.permissions import require_role
from src.models.user import User
from src.schemas.user_schemas import (
    UserListQuery,
    UserPaginationResponse,
    UserResponse,
    UserRolesUpdate,
    UserStatusUpdate,
)
from src.services.user_service import UserService

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get(
    "",
    response_model=UserPaginationResponse,
    status_code=status.HTTP_200_OK,
    summary="Listado paginado de usuarios con búsqueda",
)
def list_users(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Cantidad por página"),
    search: str = Query("", description="Término de búsqueda"),
    include_inactive: bool = Query(
        False, description="Incluir usuarios inactivos"
    ),
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    user_service: UserService = Depends(get_user_service),
) -> UserPaginationResponse:
    query = UserListQuery(
        page=page,
        size=size,
        search=search,
        include_inactive=include_inactive,
    )
    return user_service.list_users(query)


@router.put(
    "/{user_id}/roles",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar roles de un usuario",
)
def update_user_roles(
    user_id: int,
    roles_data: UserRolesUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.update_user_roles(
        target_user_id=user_id,
        roles_data=roles_data,
        current_user=current_user,
    )


@router.patch(
    "/{user_id}/estado",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar estado activo/inactivo (borrado lógico o reactivación)",
)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return user_service.update_user_status(
        target_user_id=user_id,
        status_data=status_data,
        current_user=current_user,
    )

