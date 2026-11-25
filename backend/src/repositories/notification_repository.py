from typing import List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, notifications: List[Notification]) -> List[Notification]:
        self.db.add_all(notifications)
        self.db.commit()
        for n in notifications:
            self.db.refresh(n)
        return notifications

    def list_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 5,
    ) -> Tuple[List[Notification], int, int]:
        total = (
            self.db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .scalar()
            or 0
        )
        unread_count = (
            self.db.query(func.count(Notification.id))
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .scalar()
            or 0
        )
        items = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total, unread_count

    def mark_all_as_read(self, user_id: int) -> int:
        updated = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .update({"is_read": True}, synchronize_session=False)
        )
        self.db.commit()
        return updated
