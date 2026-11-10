import pytest
from fastapi import HTTPException
from src.core.security import hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import (
    UserListQuery,
    UserRolesUpdate,
    UserStatusUpdate,
)
from src.services.user_service import UserService


def create_user_helper(
    db,
    email: str,
    doc_number: str,
    first_name: str,
    last_name: str,
    roles: list[UserRole],
    is_active: bool = True,
) -> User:
    repo = UserRepository(db)
    u = User(
        document_type=DocumentType.CEDULA,
        document_number=doc_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hash_password("Pass1234"),
        is_active=is_active,
    )
    u.roles = roles
    return repo.create(u)


def test_list_users_search_no_matches(db_session):
    """U-01: list_users with search term that matches nothing returns empty list."""
    create_user_helper(
        db_session,
        "ana@example.com",
        "1710034065",
        "Ana",
        "Gomez",
        [UserRole.PASAJERO],
    )
    service = UserService(db_session)
    result = service.list_users(UserListQuery(search="inexistente_xyz_123"))

    assert len(result.items) == 0
    assert result.total == 0
    assert result.pages == 0


def test_list_users_ilike_case_insensitive(db_session):
    """U-02: list_users search is case-insensitive (ILIKE)."""
    create_user_helper(
        db_session,
        "marcos.paredes@example.com",
        "1104609829",
        "Marcos",
        "Paredes",
        [UserRole.PASAJERO],
    )
    service = UserService(db_session)

    # Search with uppercase should find lowercase Marcos
    result = service.list_users(UserListQuery(search="MARCOS"))
    assert len(result.items) == 1
    assert result.items[0].email == "marcos.paredes@example.com"


def test_list_users_page_out_of_range(db_session):
    """U-03: Requesting a page beyond total pages returns empty items without error."""
    create_user_helper(
        db_session,
        "p1@example.com",
        "0926691452",
        "Persona",
        "Uno",
        [UserRole.PASAJERO],
    )
    service = UserService(db_session)
    result = service.list_users(UserListQuery(page=999, size=10))

    assert len(result.items) == 0
    assert result.total == 1
    assert result.pages == 1
    assert result.page == 999


def test_assign_roles_forces_pasajero(db_session):
    """U-05: Assigning roles without PASAJERO automatically includes PASAJERO."""
    admin = create_user_helper(
        db_session,
        "admin@boletoya.com",
        "1710034065",
        "Admin",
        "General",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    target = create_user_helper(
        db_session,
        "user@example.com",
        "0102555547",
        "Usuario",
        "Prueba",
        [UserRole.PASAJERO],
    )
    service = UserService(db_session)

    # Payload with only ADMIN_COOPERATIVA
    roles_data = UserRolesUpdate(roles=[UserRole.ADMIN_COOPERATIVA])
    res = service.update_user_roles(
        target_user_id=target.id,
        roles_data=roles_data,
        current_user=admin,
    )

    assert UserRole.PASAJERO in res.roles
    assert UserRole.ADMIN_COOPERATIVA in res.roles


def test_assign_roles_to_nonexistent_user(db_session):
    """U-08: Assigning roles to a nonexistent user raises 404."""
    admin = create_user_helper(
        db_session,
        "admin2@boletoya.com",
        "1710034065",
        "Admin",
        "Dos",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    service = UserService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.update_user_roles(
            target_user_id=99999,
            roles_data=UserRolesUpdate(roles=[UserRole.SECRETARIA_COOPERATIVA]),
            current_user=admin,
        )
    assert exc_info.value.status_code == 404


def test_assign_roles_self_modification_forbidden(db_session):
    """U-09: Admin attempting to modify own roles raises 403."""
    admin = create_user_helper(
        db_session,
        "admin3@boletoya.com",
        "1710034065",
        "Admin",
        "Tres",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    service = UserService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.update_user_roles(
            target_user_id=admin.id,
            roles_data=UserRolesUpdate(roles=[UserRole.PASAJERO]),
            current_user=admin,
        )
    assert exc_info.value.status_code == 403
    assert "propia cuenta" in exc_info.value.detail.lower()


def test_deactivate_self_forbidden(db_session):
    """U-10: Admin attempting to deactivate own account raises 403."""
    admin = create_user_helper(
        db_session,
        "admin4@boletoya.com",
        "1710034065",
        "Admin",
        "Cuatro",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    service = UserService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.update_user_status(
            target_user_id=admin.id,
            status_data=UserStatusUpdate(is_active=False),
            current_user=admin,
        )
    assert exc_info.value.status_code == 403
    assert "propia cuenta" in exc_info.value.detail.lower()


def test_deactivate_already_inactive_user_rejected(db_session):
    """U-11: Deactivating an already inactive user raises 400."""
    admin = create_user_helper(
        db_session,
        "admin5@boletoya.com",
        "1710034065",
        "Admin",
        "Cinco",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    inactive_user = create_user_helper(
        db_session,
        "inactive@example.com",
        "0926691452",
        "Inactivo",
        "User",
        [UserRole.PASAJERO],
        is_active=False,
    )
    service = UserService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.update_user_status(
            target_user_id=inactive_user.id,
            status_data=UserStatusUpdate(is_active=False),
            current_user=admin,
        )
    assert exc_info.value.status_code == 400
    assert "ya se encuentra inactivo" in exc_info.value.detail.lower()


def test_reactivate_already_active_user_rejected(db_session):
    """U-12: Reactivating an already active user raises 400."""
    admin = create_user_helper(
        db_session,
        "admin6@boletoya.com",
        "1710034065",
        "Admin",
        "Seis",
        [UserRole.ADMIN_GENERAL, UserRole.PASAJERO],
    )
    active_user = create_user_helper(
        db_session,
        "active@example.com",
        "0102555547",
        "Activo",
        "User",
        [UserRole.PASAJERO],
        is_active=True,
    )
    service = UserService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.update_user_status(
            target_user_id=active_user.id,
            status_data=UserStatusUpdate(is_active=True),
            current_user=admin,
        )
    assert exc_info.value.status_code == 400
    assert "ya se encuentra activo" in exc_info.value.detail.lower()

