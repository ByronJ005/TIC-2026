from typing import Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.dependencies import get_current_user, get_db
from src.models.user import User


def require_role(*roles: str) -> Callable[[User], User]:
    """
    Centralized role authorization dependency factory.
    Verifies that the current user possesses at least one of the allowed roles.
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles_str = {
            r.value if hasattr(r, "value") else str(r)
            for r in (current_user.roles or [])
        }
        allowed_roles_str = {
            r.value if hasattr(r, "value") else str(r) for r in roles
        }

        if not user_roles_str.intersection(allowed_roles_str):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para este recurso",
            )
        return current_user

    return checker


def require_active_cooperativa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that verifies the current user has a valid and active cooperative assigned.
    Used for cooperative-restricted operational resources.
    Returns current_user if active cooperative, otherwise raises HTTP 403 Forbidden.
    """
    if not current_user.cooperativa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una cooperativa asignada",
        )

    from src.repositories.cooperativa_repository import CooperativaRepository

    coop_repo = CooperativaRepository(db)
    coop = coop_repo.get_by_id(current_user.cooperativa_id)

    if not coop or not coop.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cooperativa asignada se encuentra inactiva",
        )

    return current_user
