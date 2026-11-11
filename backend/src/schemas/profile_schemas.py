from typing import Optional

from pydantic import BaseModel

from src.schemas.user_schemas import UserResponse


class ProfileUpdate(BaseModel):
    """
    Input DTO for profile updates. It deliberately has no email or document fields,
    so those values cannot be modified through this endpoint.
    Field validation lives in ProfileService to keep error messages and their order exact.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    # ISO date (YYYY-MM-DD) as text so invalid dates map to the CP-41 message
    birth_date: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    confirm_password: Optional[str] = None


class ProfileResponse(BaseModel):
    user: UserResponse
    message: str
    # Only present when the password changed, so the current session can continue
    access_token: Optional[str] = None
    token_type: Optional[str] = None

