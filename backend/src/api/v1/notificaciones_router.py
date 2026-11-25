from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from src.core.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.notification_schemas import NotificationListResponse
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar notificaciones del usuario autenticado (paginado de 5 en 5)",
)
def list_notifications(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(5, ge=1, le=20, description="Cantidad por página (por defecto 5)"),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return service.get_user_notifications(
        user_id=current_user.id,
        page=page,
        size=size,
    )


@router.patch(
    "/leidas",
    status_code=status.HTTP_200_OK,
    summary="Marcar todas las notificaciones del usuario como leídas",
)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    count = service.mark_all_as_read(user_id=current_user.id)
    return {"message": "Notificaciones marcadas como leídas", "count": count}
