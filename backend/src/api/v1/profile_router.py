from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.profile_schemas import ProfileResponse, ProfileUpdate
from src.schemas.user_schemas import UserResponse
from src.services.profile_service import ProfileService

router = APIRouter(prefix="/perfil", tags=["Perfil"])


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar el perfil del usuario autenticado",
)
def get_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserResponse:
    return profile_service.get_profile(current_user)


@router.put(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar el perfil del usuario autenticado",
)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    return profile_service.update_profile(current_user, data)

