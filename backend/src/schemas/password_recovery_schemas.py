from typing import Optional

from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    # Validation lives in PasswordRecoveryService so error messages stay exact (CP-35/CP-36)
    email: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    token: Optional[str] = None
    new_password: Optional[str] = None


class MessageResponse(BaseModel):
    message: str

