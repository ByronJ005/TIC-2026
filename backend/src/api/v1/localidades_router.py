from typing import List
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.core.permissions import require_role
from src.models.user import User
from src.schemas.locality_schemas import LocalityCreate, LocalityListResponse, LocalityResponse
from src.services.locality_service import LocalityService

router = APIRouter(prefix="/localidades", tags=["Catálogo de Localidades"])


def get_locality_service(db: Session = Depends(get_db)) -> LocalityService:
    return LocalityService(db)


@router.get(
    "",
    response_model=LocalityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar localidades en el catálogo",
)
def list_localities(
    search: str = Query("", description="Término de búsqueda de localidad"),
    current_user: User = Depends(require_role("ADMIN_GENERAL", "ADMIN_COOPERATIVA")),
    service: LocalityService = Depends(get_locality_service),
) -> LocalityListResponse:
    items = service.search(query=search)
    return LocalityListResponse(items=[LocalityResponse.model_validate(loc) for loc in items], total=len(items))


@router.post(
    "",
    response_model=LocalityResponse,
    summary="Crear u obtener localidad existente de forma idempotente",
)
def create_locality(
    data: LocalityCreate,
    response: Response,
    current_user: User = Depends(require_role("ADMIN_GENERAL", "ADMIN_COOPERATIVA")),
    service: LocalityService = Depends(get_locality_service),
) -> LocalityResponse:
    locality, created = service.get_or_create(data)
    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK
    return LocalityResponse.model_validate(locality)
