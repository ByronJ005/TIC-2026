import pytest
from src.models.cooperativa import Cooperativa
from src.models.user import DocumentType, User, UserRole
from src.repositories.cooperativa_repository import CooperativaRepository
from src.repositories.user_repository import UserRepository


def test_user_repository_eligible_admins(db_session):
    coop_repo = CooperativaRepository(db_session)
    user_repo = UserRepository(db_session)

    # Create two cooperatives
    c1 = coop_repo.create(Cooperativa(name="Coop Uno", ruc="1104609829001"))
    c2 = coop_repo.create(Cooperativa(name="Coop Dos", ruc="1790011216001"))

    # User 1: Eligible (active, ADMIN_COOPERATIVA, no coop)
    u1 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1104609829",
            first_name="Carlos",
            last_name="Perez",
            email="carlos@example.com",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO, UserRole.ADMIN_COOPERATIVA],
        )
    )

    # User 2: Not eligible - inactive
    u2 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1710034065",
            first_name="Ana",
            last_name="Gomez",
            email="ana@example.com",
            hashed_password="hash",
            is_active=False,
            roles=[UserRole.ADMIN_COOPERATIVA],
        )
    )

    # User 3: Not eligible - no ADMIN_COOPERATIVA role (only PASAJERO)
    u3 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="0926691452",
            first_name="Luis",
            last_name="Vera",
            email="luis@example.com",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.PASAJERO],
        )
    )

    # User 4: Assigned to c2 (eligible for c2, but NOT for c1)
    u4 = user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="0102555547",
            first_name="Maria",
            last_name="Lopez",
            email="maria@example.com",
            hashed_password="hash",
            is_active=True,
            cooperativa_id=c2.id,
            roles=[UserRole.ADMIN_COOPERATIVA],
        )
    )

    # User 5: Already assigned to c1 (eligible for c1)
    u5 = user_repo.create(
        User(
            document_type=DocumentType.PASAPORTE,
            document_number="AB123456",
            first_name="Juan",
            last_name="Castro",
            email="juan@example.com",
            hashed_password="hash",
            is_active=True,
            cooperativa_id=c1.id,
            roles=[UserRole.ADMIN_COOPERATIVA],
        )
    )

    # Test for c1: should contain u1 (free) and u5 (already c1), NOT u2 (inactive), u3 (no role), u4 (c2)
    eligible_c1 = user_repo.list_eligible_cooperative_admins(c1.id)
    ids_c1 = [u.id for u in eligible_c1]
    assert u1.id in ids_c1
    assert u5.id in ids_c1
    assert u2.id not in ids_c1
    assert u3.id not in ids_c1
    assert u4.id not in ids_c1

    # Test search
    search_carlos = user_repo.list_eligible_cooperative_admins(c1.id, search="carlos")
    assert len(search_carlos) == 1
    assert search_carlos[0].id == u1.id

    # Test get_cooperative_admins
    c1_admins = user_repo.get_cooperative_admins(c1.id)
    assert len(c1_admins) == 1
    assert c1_admins[0].id == u5.id

    # Test get_users_by_ids_for_update
    locked = user_repo.get_users_by_ids_for_update([u5.id, u1.id])
    assert len(locked) == 2
    # must be sorted by ID asc
    assert locked[0].id < locked[1].id

