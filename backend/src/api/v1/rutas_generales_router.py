from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.core.dependencies import get_current_user, get_db
from src.core.permissions import require_role
from src.models.route import CooperativaGeneralRoute
from src.models.user import User, UserRole
from src.schemas.route_schemas import (
    CooperativaRoutesGroup,
    RouteCreate,
    RouteDetailResponse,
    RouteEstadoUpdate,
    RoutePaginationResponse,
    RouteResponse,
    RouteUpdate,
)
from src.services.route_service import RouteService

router = APIRouter(prefix="/rutas-generales", tags=["Rutas Generales"])
shared_router = APIRouter(prefix="/rutas", tags=["Detalle de Rutas"])


def get_route_service(db: Session = Depends(get_db)) -> RouteService:
    return RouteService(db)


@router.post(
    "",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva ruta general",
)
def create_general_route(
    data: RouteCreate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: RouteService = Depends(get_route_service),
) -> RouteDetailResponse:
    return service.create_general_route(data, current_user=current_user)


@router.get(
    "",
    response_model=RoutePaginationResponse,
    status_code=status.HTTP_200_OK,
    summary="Listado paginado de rutas generales con filtros",
)
def list_general_routes(
    origin_id: Optional[int] = Query(None, description="Filtrar por localidad de origen"),
    destination_id: Optional[int] = Query(None, description="Filtrar por localidad de destino"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Cantidad por página"),
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: RouteService = Depends(get_route_service),
) -> RoutePaginationResponse:
    return service.list_general_routes(
        origin_id=origin_id,
        destination_id=destination_id,
        is_active=is_active,
        page=page,
        size=size,
    )


@router.get(
    "/especificas",
    response_model=List[CooperativaRoutesGroup],
    status_code=status.HTTP_200_OK,
    summary="Supervisar rutas específicas agrupadas por cooperativa (solo lectura)",
)
def list_specific_routes_grouped(
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: RouteService = Depends(get_route_service),
) -> List[CooperativaRoutesGroup]:
    return service.list_specific_routes_grouped()


@router.put(
    "/{route_id}",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de ruta general",
)
def update_general_route(
    route_id: int,
    data: RouteUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: RouteService = Depends(get_route_service),
) -> RouteDetailResponse:
    return service.update_general_route(
        route_id=route_id,
        data=data,
        current_user=current_user,
    )


@router.patch(
    "/{route_id}/estado",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar ruta general (con cascada transaccional)",
)
def update_general_route_estado(
    route_id: int,
    data: RouteEstadoUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: RouteService = Depends(get_route_service),
) -> RouteDetailResponse:
    return service.update_general_route_estado(
        route_id=route_id,
        data=data,
        current_user=current_user,
    )


@shared_router.get(
    "/{route_id}",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle completo de una ruta con autorización",
)
def get_route_detail(
    route_id: int,
    current_user: User = Depends(get_current_user),
    service: RouteService = Depends(get_route_service),
    db: Session = Depends(get_db),
) -> RouteDetailResponse:
    detail = service.get_route_detail(route_id)

    roles = {
        r.value if hasattr(r, "value") else str(r)
        for r in (current_user.roles or [])
    }

    if UserRole.ADMIN_GENERAL.value in roles:
        return detail

    if UserRole.ADMIN_COOPERATIVA.value in roles:
        # Check if it is a specific route belonging to own cooperative
        if detail.cooperativa_id is not None:
            if detail.cooperativa_id == current_user.cooperativa_id:
                return detail
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recurso de otra cooperativa",
            )
        # Check if it is a general route adopted by own cooperative
        if current_user.cooperativa_id:
            adopted = (
                db.query(CooperativaGeneralRoute.id)
                .filter(
                    CooperativaGeneralRoute.cooperativa_id == current_user.cooperativa_id,
                    CooperativaGeneralRoute.route_id == route_id,
                )
                .first()
            )
            if adopted:
                return detail

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para este recurso",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No autorizado para este recurso",
    )
