from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from src.schemas.validators import (
    ERROR_ADDRESS_TOO_LONG,
    ERROR_INVALID_EMAIL,
    ERROR_REQUIRED_FIELD,
    get_cooperativa_name_error,
    get_phone_error,
    get_ruc_error,
    is_blank,
    normalize_email,
    validate_address_length,
    validate_email_format,
)

ERROR_MAX_ADMINS_EXCEEDED = "Una cooperativa puede tener como máximo 3 administradores"
ERROR_INVALID_LOGO_URL = "La URL del logo debe comenzar con http:// o https://"


class AdministradorSummary(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    document_number: str
    phone: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CooperativaCreate(BaseModel):
    name: str
    ruc: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        error = get_cooperativa_name_error(v)
        if error:
            raise ValueError(error)
        return v.strip()

    @field_validator("ruc")
    @classmethod
    def validate_ruc_field(cls, v: str) -> str:
        error = get_ruc_error(v)
        if error:
            raise ValueError(error)
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if is_blank(v):
            return None
        if not validate_address_length(v):
            raise ValueError(ERROR_ADDRESS_TOO_LONG)
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if is_blank(v):
            return None
        error = get_phone_error(v)
        if error:
            raise ValueError(error)
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if is_blank(v):
            return None
        if not validate_email_format(v):
            raise ValueError(ERROR_INVALID_EMAIL)
        return normalize_email(v)

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        if is_blank(v):
            return None
        cleaned = v.strip()
        if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
            raise ValueError(ERROR_INVALID_LOGO_URL)
        if len(cleaned) > 500:
            raise ValueError("La URL del logo no puede exceder los 500 caracteres")
        return cleaned


class CooperativaUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        error = get_cooperativa_name_error(v)
        if error:
            raise ValueError(error)
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if is_blank(v):
            return None
        if not validate_address_length(v):
            raise ValueError(ERROR_ADDRESS_TOO_LONG)
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if is_blank(v):
            return None
        error = get_phone_error(v)
        if error:
            raise ValueError(error)
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if is_blank(v):
            return None
        if not validate_email_format(v):
            raise ValueError(ERROR_INVALID_EMAIL)
        return normalize_email(v)

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or is_blank(v):
            return None
        cleaned = v.strip()
        # En actualización se permiten URLs absolutas (http/https) o rutas relativas generadas por la subida (/static/logos/...)
        if not (
            cleaned.startswith("http://")
            or cleaned.startswith("https://")
            or cleaned.startswith("/static/")
            or cleaned.startswith("/")
        ):
            raise ValueError(ERROR_INVALID_LOGO_URL)
        if len(cleaned) > 500:
            raise ValueError("La URL del logo no puede exceder los 500 caracteres")
        return cleaned


class CooperativaEstadoUpdate(BaseModel):
    is_active: bool


class CooperativaAdministradoresUpdate(BaseModel):
    user_ids: List[int]

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v: List[int]) -> List[int]:
        if len(v) > 3:
            raise ValueError(ERROR_MAX_ADMINS_EXCEEDED)
        # deduplicate maintaining order
        seen = set()
        deduped = []
        for uid in v:
            if uid not in seen:
                seen.add(uid)
                deduped.append(uid)
        return deduped


class CooperativaResponse(BaseModel):
    id: int
    name: str
    ruc: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    administradores: List[AdministradorSummary] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CooperativaPaginationResponse(BaseModel):
    items: List[CooperativaResponse]
    total: int
    page: int
    size: int
    total_pages: int


class EligibleAdminResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    document_number: str
    is_already_assigned: bool = False

    model_config = ConfigDict(from_attributes=True)

