from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.core.permissions import require_active_cooperativa, require_role
from src.models.user import User
from src.schemas.route_schemas import (
    AdoptGeneralRouteEstadoUpdate,
    AdoptGeneralRoutesRequest,
    CooperativaGeneralRouteResponse,
    RouteCreate,
    RouteDetailResponse,
    RouteEstadoUpdate,
    RouteResponse,
    RouteUpdate,
)
from src.services.cooperativa_route_service import CooperativaRouteService

router = APIRouter(prefix="/rutas-cooperativa", tags=["Rutas de Cooperativa"])


def get_coop_route_service(db: Session = Depends(get_db)) -> CooperativaRouteService:
    return CooperativaRouteService(db)


# -------------------------------------------------------------
# Adopted General Routes
# -------------------------------------------------------------
@router.get(
    "/generales",
    response_model=List[CooperativaGeneralRouteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar rutas generales adoptadas por la cooperativa",
)
def list_adopted_general_routes(
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> List[CooperativaGeneralRouteResponse]:
    return service.list_adopted_general_routes(cooperativa_id=current_user.cooperativa_id)


@router.get(
    "/generales/disponibles",
    response_model=List[RouteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar rutas generales activas disponibles para adoptar",
)
def list_available_general_routes(
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> List[RouteResponse]:
    return service.list_available_general_routes(cooperativa_id=current_user.cooperativa_id)


@router.post(
    "/generales",
    response_model=List[CooperativaGeneralRouteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Adoptar una o más rutas generales para la cooperativa",
)
def adopt_general_routes(
    data: AdoptGeneralRoutesRequest,
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> List[CooperativaGeneralRouteResponse]:
    return service.adopt_general_routes(
        cooperativa_id=current_user.cooperativa_id,
        route_ids=data.route_ids,
        current_user=current_user,
    )


@router.patch(
    "/generales/{adoption_id}/estado",
    response_model=CooperativaGeneralRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar ruta general adoptada en la cooperativa",
)
def update_adoption_estado(
    adoption_id: int,
    data: AdoptGeneralRouteEstadoUpdate,
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> CooperativaGeneralRouteResponse:
    return service.update_adoption_estado(
        cooperativa_id=current_user.cooperativa_id,
        adoption_id=adoption_id,
        data=data,
        current_user=current_user,
    )


# -------------------------------------------------------------
# Specific Routes ("Mis Rutas")
# -------------------------------------------------------------
@router.get(
    "/especificas",
    response_model=List[RouteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar rutas específicas propias de la cooperativa",
)
def list_specific_routes(
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> List[RouteResponse]:
    return service.list_specific_routes(cooperativa_id=current_user.cooperativa_id)


@router.post(
    "/especificas",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva ruta específica para la cooperativa",
)
def create_specific_route(
    data: RouteCreate,
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> RouteDetailResponse:
    return service.create_specific_route(
        cooperativa_id=current_user.cooperativa_id,
        data=data,
        current_user=current_user,
    )


@router.put(
    "/especificas/{route_id}",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar ruta específica de la cooperativa",
)
def update_specific_route(
    route_id: int,
    data: RouteUpdate,
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> RouteDetailResponse:
    return service.update_specific_route(
        cooperativa_id=current_user.cooperativa_id,
        route_id=route_id,
        data=data,
        current_user=current_user,
    )


@router.patch(
    "/especificas/{route_id}/estado",
    response_model=RouteDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar ruta específica de la cooperativa",
)
def update_specific_route_estado(
    route_id: int,
    data: RouteEstadoUpdate,
    current_user: User = Depends(require_role("ADMIN_COOPERATIVA")),
    active_user: User = Depends(require_active_cooperativa),
    service: CooperativaRouteService = Depends(get_coop_route_service),
) -> RouteDetailResponse:
    return service.update_specific_route_estado(
        cooperativa_id=current_user.cooperativa_id,
        route_id=route_id,
        data=data,
        current_user=current_user,
    )
