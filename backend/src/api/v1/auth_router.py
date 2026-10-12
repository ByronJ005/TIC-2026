from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_user, get_db, get_token_payload
from src.models.user import User
from src.schemas.auth_schemas import LoginRequest, TokenResponse
from src.schemas.user_schemas import UserCreate, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo usuario",
)
def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return auth_service.register_user(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Inicio de sesión con email y contraseña",
)
def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return auth_service.login_user(credentials)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cierre de sesión e invalidación de token",
)
def logout(
    payload: Dict[str, Any] = Depends(get_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    auth_service.logout_user(payload)
    return {"message": "Sesión cerrada satisfactoriamente"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil del usuario autenticado",
)
def get_me(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return auth_service.get_current_user_profile(current_user)
