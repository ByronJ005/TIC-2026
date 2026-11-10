import pytest
from fastapi import HTTPException
from src.core.permissions import require_role
from src.models.user import DocumentType, User, UserRole


def build_mock_user(roles: list[UserRole], user_id: int = 1) -> User:
    u = User(
        id=user_id,
        document_type=DocumentType.CEDULA,
        document_number="1710034065",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hashed_password="hash",
        is_active=True,
    )
    u.roles = roles
    return u


def test_require_role_single_matching():
    """U-15: User with [PASAJERO, ADMIN_GENERAL] passes ADMIN_GENERAL check."""
    user = build_mock_user([UserRole.PASAJERO, UserRole.ADMIN_GENERAL])
    checker = require_role("ADMIN_GENERAL")
    # Calling the inner checker function directly with current_user
    result = checker(current_user=user)
    assert result == user


def test_require_role_non_matching_raises_403():
    """U-16: User with [PASAJERO] fails ADMIN_GENERAL check with 403."""
    user = build_mock_user([UserRole.PASAJERO])
    checker = require_role("ADMIN_GENERAL")

    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=user)
    assert exc_info.value.status_code == 403
    assert "No autorizado" in exc_info.value.detail


def test_require_role_admin_coop_fails_admin_general():
    """U-17: User with [ADMIN_COOPERATIVA, PASAJERO] fails ADMIN_GENERAL check."""
    user = build_mock_user([UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO])
    checker = require_role("ADMIN_GENERAL")

    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=user)
    assert exc_info.value.status_code == 403


def test_require_role_multiple_allowed_roles():
    """U-18: Endpoint allows [ADMIN_GENERAL, SECRETARIA_COOPERATIVA]; user has SECRETARIA_COOPERATIVA."""
    user = build_mock_user([UserRole.SECRETARIA_COOPERATIVA, UserRole.PASAJERO])
    checker = require_role("ADMIN_GENERAL", "SECRETARIA_COOPERATIVA")
    result = checker(current_user=user)
    assert result == user

