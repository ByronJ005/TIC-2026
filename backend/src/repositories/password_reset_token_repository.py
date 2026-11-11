from datetime import datetime
from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from src.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

    def invalidate_unused_for_user(self, user_id: int, used_at: datetime) -> None:
        self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=used_at)
        )
        self.db.commit()

    def mark_as_used(self, token: PasswordResetToken, used_at: datetime) -> None:
        token.used_at = used_at
        self.db.commit()

