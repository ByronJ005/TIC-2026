from pydantic import BaseModel, field_validator
from src.schemas.validators import (
    ERROR_REQUIRED_FIELD,
    normalize_email,
)


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        return normalize_email(v)

    @field_validator("password")
    @classmethod
    def validate_password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
