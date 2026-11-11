from datetime import date, datetime
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.http_status import VALIDATION_ERROR_STATUS
from src.core.datetime_utils import utc_now
from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.profile_schemas import ProfileResponse, ProfileUpdate
from src.schemas.user_schemas import UserResponse
from src.schemas.validators import (
    ADDRESS_MAX_LENGTH,
    ERROR_ADDRESS_TOO_LONG,
    ERROR_CURRENT_PASSWORD_REQUIRED,
    ERROR_CURRENT_PASSWORD_WRONG,
    ERROR_INVALID_BIRTH_DATE,
    ERROR_INVALID_NAME,
    ERROR_INVALID_PASSWORD,
    ERROR_MANDATORY_FIELDS_EMPTY,
    ERROR_NEW_PASSWORD_SAME_AS_CURRENT,
    ERROR_PASSWORD_CONFIRMATION_MISMATCH,
    ERROR_REQUIRED_FIELD,
    get_phone_error,
    is_blank,
    validate_address_length,
    validate_birth_date,
    validate_name_format,
    validate_password_format,
)

PROFILE_UPDATED_MESSAGE = "Perfil actualizado exitosamente"
PASSWORD_UPDATED_MESSAGE = "Contraseña actualizada exitosamente"


def _validation_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=VALIDATION_ERROR_STATUS,
        detail=detail,
    )


class ProfileService:
    def __init__(
        self,
        db: Session,
        today_provider: Callable[[], date] = date.today,
        now_provider: Callable[[], datetime] = utc_now,
    ):
        self.user_repo = UserRepository(db)
        self.today_provider = today_provider
        self.now_provider = now_provider

    def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def update_profile(self, user: User, data: ProfileUpdate) -> ProfileResponse:
        # Everything is validated before touching the database so a failure persists nothing
        fields_to_update = self._validate_personal_data(data)
        password_is_changing = self._validate_password_change(user, data)

        if password_is_changing:
            fields_to_update["hashed_password"] = hash_password(data.new_password)
            fields_to_update["password_changed_at"] = self.now_provider()

        updated_user = self.user_repo.update_profile(user, fields_to_update)

        if not password_is_changing:
            return ProfileResponse(
                user=UserResponse.model_validate(updated_user),
                message=PROFILE_UPDATED_MESSAGE,
            )

        # Other sessions are revoked by password_changed_at; this fresh token keeps the current one
        new_token = create_access_token(subject=updated_user.id)
        return ProfileResponse(
            user=UserResponse.model_validate(updated_user),
            message=PASSWORD_UPDATED_MESSAGE,
            access_token=new_token,
            token_type="bearer",
        )

    def _validate_personal_data(self, data: ProfileUpdate) -> Dict[str, Any]:
        if is_blank(data.first_name) or is_blank(data.last_name):
            raise _validation_error(ERROR_MANDATORY_FIELDS_EMPTY)
        if not validate_name_format(data.first_name) or not validate_name_format(
            data.last_name
        ):
            raise _validation_error(ERROR_INVALID_NAME)

        phone_error = get_phone_error(data.phone)
        if phone_error:
            raise _validation_error(phone_error)

        if not validate_address_length(data.address):
            raise _validation_error(ERROR_ADDRESS_TOO_LONG)

        birth_date = self._parse_birth_date(data.birth_date)

        return {
            "first_name": data.first_name.strip(),
            "last_name": data.last_name.strip(),
            "phone": None if is_blank(data.phone) else data.phone,
            "address": None if is_blank(data.address) else data.address.strip()[:ADDRESS_MAX_LENGTH],
            "birth_date": birth_date,
        }

    def _parse_birth_date(self, raw_value: Optional[str]) -> Optional[date]:
        if is_blank(raw_value):
            return None
        try:
            parsed_date = date.fromisoformat(raw_value.strip())
        except ValueError:
            raise _validation_error(ERROR_INVALID_BIRTH_DATE)
        if not validate_birth_date(parsed_date, today=self.today_provider()):
            raise _validation_error(ERROR_INVALID_BIRTH_DATE)
        return parsed_date

    def _validate_password_change(self, user: User, data: ProfileUpdate) -> bool:
        """Returns True when a valid password change was requested (all-or-nothing rule)."""
        password_fields = (data.current_password, data.new_password, data.confirm_password)
        if all(is_blank(field) for field in password_fields):
            return False

        if is_blank(data.current_password):
            raise _validation_error(ERROR_CURRENT_PASSWORD_REQUIRED)
        if is_blank(data.new_password) or is_blank(data.confirm_password):
            raise _validation_error(ERROR_REQUIRED_FIELD)

        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_CURRENT_PASSWORD_WRONG,
            )
        if not validate_password_format(data.new_password):
            raise _validation_error(ERROR_INVALID_PASSWORD)
        if data.new_password != data.confirm_password:
            raise _validation_error(ERROR_PASSWORD_CONFIRMATION_MISMATCH)
        if data.new_password == data.current_password:
            raise _validation_error(ERROR_NEW_PASSWORD_SAME_AS_CURRENT)
        return True
