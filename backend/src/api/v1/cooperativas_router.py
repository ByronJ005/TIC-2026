from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.core.permissions import require_role
from src.models.user import User
from src.schemas.cooperativa_schemas import (
    AdministradorSummary,
    CooperativaAdministradoresUpdate,
    CooperativaCreate,
    CooperativaEstadoUpdate,
    CooperativaPaginationResponse,
    CooperativaResponse,
    CooperativaUpdate,
    EligibleAdminResponse,
)
from src.services.audit_service import AuditService
from src.services.cooperativa_administrators_service import (
    CooperativaAdministratorsService,
)
from src.services.cooperativa_service import (
    CODE_COOPERATIVA_INACTIVA,
    ERROR_COOPERATIVA_INACTIVE,
    CooperativaService,
)
from src.services.logo_storage_service import LogoStorageService

router = APIRouter(prefix="/cooperativas", tags=["Gestión de Cooperativas"])


def get_coop_service(db: Session = Depends(get_db)) -> CooperativaService:
    return CooperativaService(db)


def get_coop_admin_service(
    db: Session = Depends(get_db),
) -> CooperativaAdministratorsService:
    return CooperativaAdministratorsService(db)


def get_logo_storage_service() -> LogoStorageService:
    return LogoStorageService()


@router.post(
    "",
    response_model=CooperativaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva cooperativa",
)
def create_cooperativa(
    data: CooperativaCreate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
) -> CooperativaResponse:
    return service.create_cooperativa(data, current_user=current_user)


@router.get(
    "",
    response_model=CooperativaPaginationResponse,
    status_code=status.HTTP_200_OK,
    summary="Listado paginado de cooperativas con búsqueda",
)
def list_cooperativas(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Cantidad por página"),
    search: str = Query("", description="Término de búsqueda por nombre o RUC"),
    is_active: Optional[bool] = Query(
        None, description="Filtrar por estado activo/inactivo"
    ),
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
) -> CooperativaPaginationResponse:
    return service.list_cooperativas(
        search=search,
        is_active=is_active,
        page=page,
        size=size,
    )


@router.get(
    "/{cooperativa_id}",
    response_model=CooperativaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de cooperativa por ID",
)
def get_cooperativa(
    cooperativa_id: int,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
) -> CooperativaResponse:
    return service.get_cooperativa_by_id(cooperativa_id)


@router.put(
    "/{cooperativa_id}",
    response_model=CooperativaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de cooperativa",
)
def update_cooperativa(
    cooperativa_id: int,
    data: CooperativaUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
) -> CooperativaResponse:
    return service.update_cooperativa(
        cooperativa_id=cooperativa_id,
        data=data,
        current_user=current_user,
    )


@router.patch(
    "/{cooperativa_id}/estado",
    response_model=CooperativaResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar estado activo/inactivo de cooperativa (baja lógica o reactivación)",
)
def update_estado(
    cooperativa_id: int,
    data: CooperativaEstadoUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
) -> CooperativaResponse:
    return service.update_estado(
        cooperativa_id=cooperativa_id,
        data=data,
        current_user=current_user,
    )


@router.post(
    "/{cooperativa_id}/logo",
    response_model=CooperativaResponse,
    status_code=status.HTTP_200_OK,
    summary="Subir archivo de logo para cooperativa",
)
def upload_logo(
    cooperativa_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    service: CooperativaService = Depends(get_coop_service),
    logo_storage: LogoStorageService = Depends(get_logo_storage_service),
    db: Session = Depends(get_db),
) -> CooperativaResponse:
    coop_model = service.repository.get_by_id(cooperativa_id)
    if not coop_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cooperativa no encontrada",
        )

    if not coop_model.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": CODE_COOPERATIVA_INACTIVA,
                "message": ERROR_COOPERATIVA_INACTIVE,
            },
        )

    file_bytes = file.file.read()
    new_logo_url = logo_storage.save_logo_file(
        file_bytes=file_bytes,
        previous_logo_url=coop_model.logo_url,
    )

    coop_model.logo_url = new_logo_url
    updated = service.repository.update(coop_model)

    audit_service = AuditService(db)
    audit_service.record(
        user_id=current_user.id,
        action="UPLOAD_LOGO",
        module="COOPERATIVAS",
        entity="COOPERATIVA",
        entity_id=cooperativa_id,
        result="SUCCESS",
        details=f"Logo subido para cooperativa '{updated.name}' ({new_logo_url})",
    )

    return CooperativaResponse.model_validate(updated)


@router.get(
    "/{cooperativa_id}/administradores",
    response_model=List[AdministradorSummary],
    status_code=status.HTTP_200_OK,
    summary="Listar administradores asignados a la cooperativa",
)
def get_administradores(
    cooperativa_id: int,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    admin_service: CooperativaAdministratorsService = Depends(get_coop_admin_service),
) -> List[AdministradorSummary]:
    return admin_service.get_administrators(cooperativa_id)


@router.get(
    "/{cooperativa_id}/administradores/elegibles",
    response_model=List[EligibleAdminResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios elegibles para ser administradores de la cooperativa",
)
def list_eligible_administrators(
    cooperativa_id: int,
    search: str = Query("", description="Búsqueda por nombre, apellido, correo o documento"),
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    admin_service: CooperativaAdministratorsService = Depends(get_coop_admin_service),
) -> List[EligibleAdminResponse]:
    return admin_service.list_eligible_administrators(
        cooperativa_id=cooperativa_id,
        search=search,
    )


@router.put(
    "/{cooperativa_id}/administradores",
    response_model=List[AdministradorSummary],
    status_code=status.HTTP_200_OK,
    summary="Asignar y actualizar administradores de la cooperativa (máximo 3)",
)
def update_administrators(
    cooperativa_id: int,
    data: CooperativaAdministradoresUpdate,
    current_user: User = Depends(require_role("ADMIN_GENERAL")),
    admin_service: CooperativaAdministratorsService = Depends(get_coop_admin_service),
) -> List[AdministradorSummary]:
    return admin_service.update_administrators(
        cooperativa_id=cooperativa_id,
        user_ids=data.user_ids,
        current_user=current_user,
    )
