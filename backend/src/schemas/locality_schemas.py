from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from src.schemas.validators import (
    ERROR_LOCALITY_NAME_EMPTY,
    ERROR_LOCALITY_NAME_TOO_LONG,
    LOCALITY_NAME_MAX_LENGTH,
    normalize_locality_name,
)


class LocalityCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = normalize_locality_name(value)
        if not normalized:
            raise ValueError(ERROR_LOCALITY_NAME_EMPTY)
        if len(normalized) > LOCALITY_NAME_MAX_LENGTH:
            raise ValueError(ERROR_LOCALITY_NAME_TOO_LONG)
        return normalized


class LocalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LocalityListResponse(BaseModel):
    items: List[LocalityResponse]
    total: int
