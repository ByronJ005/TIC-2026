from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from src.schemas.validators import (
    ERROR_ROUTE_DESCRIPTION_TOO_LONG,
    ERROR_ROUTE_DISTANCE_INVALID,
    ERROR_ROUTE_NAME_SUFFIX_TOO_LONG,
    ERROR_ROUTE_ORIGIN_DESTINATION_SAME,
    ERROR_ROUTE_STOP_DUPLICATED,
    ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION,
    ERROR_ROUTE_STOPS_EMPTY,
    ERROR_ROUTE_TIME_INVALID,
    ROUTE_DESCRIPTION_MAX_LENGTH,
    ROUTE_NAME_SUFFIX_MAX_LENGTH,
)


class RouteStopInput(BaseModel):
    locality_id: int
    stop_order: int


class RouteStopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_id: int
    locality_id: int
    stop_order: int
    locality_name: Optional[str] = None


class RouteCreate(BaseModel):
    origin_id: int
    destination_id: int
    name_suffix: Optional[str] = None
    distance_km: Decimal
    estimated_time_minutes: int
    description: Optional[str] = None
    stops: Optional[List[RouteStopInput]] = None

    @field_validator("name_suffix")
    @classmethod
    def validate_suffix(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) > ROUTE_NAME_SUFFIX_MAX_LENGTH:
            raise ValueError(ERROR_ROUTE_NAME_SUFFIX_TOO_LONG)
        return trimmed if trimmed else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) > ROUTE_DESCRIPTION_MAX_LENGTH:
            raise ValueError(ERROR_ROUTE_DESCRIPTION_TOO_LONG)
        return trimmed if trimmed else None

    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, v: Decimal) -> Decimal:
        if v <= Decimal(0):
            raise ValueError(ERROR_ROUTE_DISTANCE_INVALID)
        return round(v, 2)

    @field_validator("estimated_time_minutes")
    @classmethod
    def validate_time(cls, v: int) -> int:
        if v <= 0 or v > 5999:
            raise ValueError(ERROR_ROUTE_TIME_INVALID)
        return v

    @model_validator(mode="after")
    def validate_route_logic(self) -> "RouteCreate":
        if self.origin_id == self.destination_id:
            raise ValueError(ERROR_ROUTE_ORIGIN_DESTINATION_SAME)

        if self.stops:
            seen_localities = set()
            for stop in self.stops:
                if stop.locality_id in (self.origin_id, self.destination_id):
                    raise ValueError(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
                if stop.locality_id in seen_localities:
                    raise ValueError(ERROR_ROUTE_STOP_DUPLICATED)
                seen_localities.add(stop.locality_id)
        return self


class RouteUpdate(BaseModel):
    origin_id: Optional[int] = None
    destination_id: Optional[int] = None
    name_suffix: Optional[str] = None
    distance_km: Optional[Decimal] = None
    estimated_time_minutes: Optional[int] = None
    description: Optional[str] = None
    stops: Optional[List[RouteStopInput]] = None

    @field_validator("name_suffix")
    @classmethod
    def validate_suffix(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) > ROUTE_NAME_SUFFIX_MAX_LENGTH:
            raise ValueError(ERROR_ROUTE_NAME_SUFFIX_TOO_LONG)
        return trimmed if trimmed else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) > ROUTE_DESCRIPTION_MAX_LENGTH:
            raise ValueError(ERROR_ROUTE_DESCRIPTION_TOO_LONG)
        return trimmed if trimmed else None

    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v <= Decimal(0):
                raise ValueError(ERROR_ROUTE_DISTANCE_INVALID)
            return round(v, 2)
        return v

    @field_validator("estimated_time_minutes")
    @classmethod
    def validate_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v <= 0 or v > 5999:
                raise ValueError(ERROR_ROUTE_TIME_INVALID)
        return v

    @model_validator(mode="after")
    def validate_route_logic(self) -> "RouteUpdate":
        if self.origin_id is not None and self.destination_id is not None:
            if self.origin_id == self.destination_id:
                raise ValueError(ERROR_ROUTE_ORIGIN_DESTINATION_SAME)

        if self.stops:
            seen_localities = set()
            for stop in self.stops:
                if self.origin_id and stop.locality_id == self.origin_id:
                    raise ValueError(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
                if self.destination_id and stop.locality_id == self.destination_id:
                    raise ValueError(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
                if stop.locality_id in seen_localities:
                    raise ValueError(ERROR_ROUTE_STOP_DUPLICATED)
                seen_localities.add(stop.locality_id)
        return self


class RouteEstadoUpdate(BaseModel):
    is_active: bool
    confirm: Optional[bool] = False


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cooperativa_id: Optional[int] = None
    origin_id: int
    destination_id: int
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    name: str
    name_suffix: Optional[str] = None
    distance_km: Decimal
    estimated_time_minutes: int
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RouteDetailResponse(RouteResponse):
    stops: List[RouteStopResponse] = []
    has_associations: bool = False
    cooperativa_name: Optional[str] = None


class RoutePaginationResponse(BaseModel):
    items: List[RouteResponse]
    total: int
    page: int
    size: int
    total_pages: int


class CooperativaRoutesGroup(BaseModel):
    cooperativa_id: int
    cooperativa_name: str
    routes: List[RouteResponse]


class CooperativaGeneralRouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cooperativa_id: int
    route_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    route: RouteResponse


class AdoptGeneralRoutesRequest(BaseModel):
    route_ids: List[int]


class AdoptGeneralRouteEstadoUpdate(BaseModel):
    is_active: bool
    confirm: Optional[bool] = False
