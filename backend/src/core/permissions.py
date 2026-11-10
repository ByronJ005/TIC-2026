from typing import Callable
from fastapi import Depends, HTTPException, status
from src.core.dependencies import get_current_user
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
