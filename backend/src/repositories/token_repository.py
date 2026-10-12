from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from src.models.blacklisted_token import BlacklistedToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_to_blacklist(self, jti: str, expires_at: datetime) -> BlacklistedToken:
        token = BlacklistedToken(jti=jti, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def is_blacklisted(self, jti: str) -> bool:
        return (
            self.db.query(BlacklistedToken)
            .filter(BlacklistedToken.jti == jti)
            .first()
            is not None
        )
