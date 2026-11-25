import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.notification import Notification
from src.models.user import User
from src.repositories.notification_repository import NotificationRepository
from src.schemas.notification_schemas import NotificationListResponse, NotificationResponse
from src.services.email_service import EmailDeliveryError, EmailSender, get_email_sender

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        db: Session,
        email_sender: Optional[EmailSender] = None,
    ):
        self.db = db
        self.repository = NotificationRepository(db)
        self.email_sender = email_sender or get_email_sender()

    def get_user_notifications(
        self,
        user_id: int,
        page: int = 1,
        size: int = 5,
    ) -> NotificationListResponse:
        page = max(1, page)
        size = min(max(1, size), 20)
        offset = (page - 1) * size

        items, total, unread_count = self.repository.list_by_user(
            user_id=user_id,
            offset=offset,
            limit=size,
        )
        has_more = (offset + len(items)) < total

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            unread_count=unread_count,
            has_more=has_more,
            page=page,
            size=size,
        )

    def mark_all_as_read(self, user_id: int) -> int:
        return self.repository.mark_all_as_read(user_id)

    def notify_users(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        email_subject: Optional[str] = None,
        email_body: Optional[str] = None,
    ) -> None:
        """
        Creates in-app notifications and attempts email delivery.
        Email failures never roll back in-app notifications or raise exceptions (resilient CP-104).
        """
        if not user_ids:
            return

        unique_user_ids = list(set(user_ids))
        notifications = [
            Notification(user_id=uid, title=title, message=message, is_read=False)
            for uid in unique_user_ids
        ]
        self.repository.create_batch(notifications)

        # Retrieve emails to send
        users = (
            self.db.query(User)
            .filter(User.id.in_(unique_user_ids), User.is_active.is_(True))
            .all()
        )

        subject = email_subject or title
        body = email_body or message

        for user in users:
            if not user.email:
                continue
            try:
                self.email_sender.send(
                    to_address=user.email,
                    subject=subject,
                    body=body,
                )
            except Exception as exc:
                # Log without exposing sensitive data
                logger.warning(
                    "Fallo al enviar notificación por correo a usuario %s: %s",
                    user.id,
                    type(exc).__name__,
                )
