from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.services.audit_service import AuditService


def test_audit_service_record(db_session):
    user_repo = UserRepository(db_session)
    admin = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1104609829",
            first_name="Admin",
            last_name="General",
            email="admin@terminal.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.ADMIN_GENERAL],
        )
    )

    audit_service = AuditService(db_session)
    log = audit_service.record(
        user_id=admin.id,
        action="CREATE_COOPERATIVA",
        module="COOPERATIVAS",
        entity="COOPERATIVA",
        entity_id=1,
        result="SUCCESS",
        details="Cooperativa Loja creada con RUC 1104609829001",
    )

    assert log.id is not None
    assert log.user_id == admin.id
    assert log.action == "CREATE_COOPERATIVA"
    assert log.module == "COOPERATIVAS"
    assert log.entity == "COOPERATIVA"
    assert log.entity_id == 1
    assert log.result == "SUCCESS"
    assert "1104609829001" in log.details
    assert log.created_at is not None

