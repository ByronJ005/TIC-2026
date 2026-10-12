from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from src.models.user import DocumentType, UserRole
from src.schemas.validators import (
    ERROR_INVALID_DOCUMENT,
    ERROR_INVALID_EMAIL,
    ERROR_INVALID_NAME,
    ERROR_INVALID_PASSWORD,
    ERROR_REQUIRED_FIELD,
    normalize_email,
    validate_ecuadorian_cedula,
    validate_email_format,
    validate_name_format,
    validate_passport,
    validate_password_format,
)


class UserCreate(BaseModel):
    document_type: DocumentType
    document_number: str
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("document_number")
    @classmethod
    def validate_document_number_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        return v.strip()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        if not validate_name_format(v):
            raise ValueError(ERROR_INVALID_NAME)
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        normalized = normalize_email(v)
        if not validate_email_format(normalized):
            raise ValueError(ERROR_INVALID_EMAIL)
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(ERROR_REQUIRED_FIELD)
        if not validate_password_format(v):
            raise ValueError(ERROR_INVALID_PASSWORD)
        return v

    @model_validator(mode="after")
    def validate_document_by_type(self) -> "UserCreate":
        doc_type = self.document_type
        doc_number = self.document_number

        if doc_type == DocumentType.CEDULA:
            if not validate_ecuadorian_cedula(doc_number):
                raise ValueError(ERROR_INVALID_DOCUMENT)
        elif doc_type == DocumentType.PASAPORTE:
            if not validate_passport(doc_number):
                raise ValueError(ERROR_INVALID_DOCUMENT)
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: DocumentType
    document_number: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
