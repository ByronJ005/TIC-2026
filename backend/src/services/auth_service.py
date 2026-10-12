from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.models.user import User, UserRole
from src.repositories.token_repository import TokenRepository
from src.repositories.user_repository import UserRepository
from src.schemas.auth_schemas import LoginRequest, TokenResponse
from src.schemas.user_schemas import UserCreate, UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def register_user(self, data: UserCreate) -> UserResponse:
        # Check uniqueness of email
        normalized_email = data.email.strip().lower()
        if self.user_repo.get_by_email(normalized_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado",
            )

        # Check uniqueness of document (type + number)
        if self.user_repo.get_by_document(data.document_type, data.document_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de documento ya se encuentra registrado",
            )

        # Hash password
        hashed_pwd = hash_password(data.password)

        # Create user entity strictly with PASAJERO role
        new_user = User(
            document_type=data.document_type,
            document_number=data.document_number.strip(),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=normalized_email,
            hashed_password=hashed_pwd,
            role=UserRole.PASAJERO,
            is_active=True,
        )

        saved_user = self.user_repo.create(new_user)
        return UserResponse.model_validate(saved_user)

    def login_user(self, credentials: LoginRequest) -> TokenResponse:
        normalized_email = credentials.email.strip().lower()
        user = self.user_repo.get_by_email(normalized_email)

        # Generic error message to prevent user enumeration
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credenciales incorrectas",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo",
            )

        token = create_access_token(
            subject=user.id,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
        )

        return TokenResponse(access_token=token, token_type="bearer")

    def logout_user(self, payload: Dict[str, Any]) -> None:
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            return

        # If already blacklisted, ignore gracefully
        if self.token_repo.is_blacklisted(jti):
            return

        # Convert exp unix timestamp to UTC datetime
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        self.token_repo.add_to_blacklist(jti=jti, expires_at=expires_at)

    def get_current_user_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)
