from typing import Optional
from sqlalchemy.orm import Session
from src.models.audit_log import AuditLog
from src.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)

    def record(
        self,
        user_id: Optional[int],
        action: str,
        module: str,
        entity: str,
        entity_id: Optional[int] = None,
        result: str = "SUCCESS",
        details: Optional[str] = None,
    ) -> AuditLog:
        """
        Records an audit event in the database.
        Ensures no passwords, tokens, or sensitive credentials are included in details.
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            entity=entity,
            entity_id=entity_id,
            result=result,
            details=details,
        )
        return self.repository.create(audit_log)

