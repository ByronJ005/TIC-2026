from typing import Callable
from fastapi import Depends, HTTPException, status
from src.core.dependencies import get_current_user
from src.models.user import User


def require_role(*roles: str) -> Callable[[User], User]:
    """
    Centralized role authorization dependency factory.
    Verifies that the current user possesses one of the allowed roles.
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_str = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        )
        allowed_roles_str = [
            r.value if hasattr(r, "value") else str(r) for r in roles
        ]

        if user_role_str not in allowed_roles_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para este recurso",
            )
        return current_user

    return checker
