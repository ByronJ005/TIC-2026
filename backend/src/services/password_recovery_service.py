import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.http_status import VALIDATION_ERROR_STATUS
from src.core.datetime_utils import as_utc, utc_now
from src.core.security import hash_password
from src.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from src.repositories.user_repository import UserRepository
from src.schemas.password_recovery_schemas import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.schemas.validators import (
    ERROR_EMAIL_REQUIRED,
    ERROR_INVALID_EMAIL,
    ERROR_INVALID_PASSWORD,
    ERROR_REQUIRED_FIELD,
    is_blank,
    normalize_email,
    validate_email_format,
    validate_password_format,
)
from src.services.email_service import EmailDeliveryError, EmailSender

logger = logging.getLogger(__name__)

RESET_REQUEST_PROCESSED_MESSAGE = (
    "Hemos procesado tu solicitud. Si el correo corresponde a una cuenta activa, "
    "recibirás un enlace en los próximos minutos."
)
EMAIL_NOT_REGISTERED_MESSAGE = (
    "El correo ingresado no corresponde a una cuenta registrada en el sistema"
)
INVALID_RESET_LINK_MESSAGE = "El enlace de restablecimiento es inválido o ha expirado"
PASSWORD_RESET_SUCCESS_MESSAGE = "Contraseña restablecida exitosamente"
RESET_EMAIL_SUBJECT = "Restablece tu contraseña de BoletoYa"
RESET_TOKEN_BYTES = 32


@dataclass(frozen=True)
class OutgoingEmail:
    to_address: str
    subject: str
    body: str


@dataclass(frozen=True)
class PasswordResetRequestResult:
    response: MessageResponse
    # None when no email must be sent (inactive account)
    email: Optional[OutgoingEmail] = None


def hash_reset_token(raw_token: str) -> str:
    # SHA-256 is enough: the token is random with high entropy, unlike a password
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class PasswordRecoveryService:
    def __init__(
        self,
        db: Session,
        email_sender: EmailSender,
        now_provider: Callable = utc_now,
    ):
        self.user_repo = UserRepository(db)
        self.token_repo = PasswordResetTokenRepository(db)
        self.email_sender = email_sender
        self.now_provider = now_provider

    def request_reset(self, data: ForgotPasswordRequest) -> PasswordResetRequestResult:
        normalized_email = self._validate_email_input(data.email)

        user = self.user_repo.get_by_email(normalized_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=EMAIL_NOT_REGISTERED_MESSAGE,
            )

        processed_response = MessageResponse(message=RESET_REQUEST_PROCESSED_MESSAGE)
        if not user.is_active:
            # Same answer as an active account, but nothing is sent
            return PasswordResetRequestResult(response=processed_response)

        raw_token = self._issue_token(user.id)
        return PasswordResetRequestResult(
            response=processed_response,
            email=self._build_reset_email(user.email, raw_token),
        )

    def deliver_email(self, email: OutgoingEmail) -> None:
        """Sends the email; delivery failures are logged and never reach the user."""
        try:
            self.email_sender.send(email.to_address, email.subject, email.body)
        except EmailDeliveryError:
            logger.error("No se pudo entregar el correo de restablecimiento")

    def reset_password(self, data: ResetPasswordRequest) -> MessageResponse:
        self._validate_new_password(data.new_password)

        token_record = self._get_usable_token(data.token)
        user = self.user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise self._invalid_link_error()

        changed_at = self.now_provider()
        self.user_repo.update_password(user, hash_password(data.new_password), changed_at)
        self.token_repo.mark_as_used(token_record, changed_at)
        self.token_repo.invalidate_unused_for_user(user.id, changed_at)
        return MessageResponse(message=PASSWORD_RESET_SUCCESS_MESSAGE)

    def _validate_email_input(self, email: Optional[str]) -> str:
        if is_blank(email):
            raise HTTPException(
                status_code=VALIDATION_ERROR_STATUS,
                detail=ERROR_EMAIL_REQUIRED,
            )
        normalized_email = normalize_email(email)
        if not validate_email_format(normalized_email):
            raise HTTPException(
                status_code=VALIDATION_ERROR_STATUS,
                detail=ERROR_INVALID_EMAIL,
            )
        return normalized_email

    def _validate_new_password(self, new_password: Optional[str]) -> None:
        if is_blank(new_password):
            raise HTTPException(
                status_code=VALIDATION_ERROR_STATUS,
                detail=ERROR_REQUIRED_FIELD,
            )
        if not validate_password_format(new_password):
            raise HTTPException(
                status_code=VALIDATION_ERROR_STATUS,
                detail=ERROR_INVALID_PASSWORD,
            )

    def _issue_token(self, user_id: int) -> str:
        now = self.now_provider()
        # A new link replaces any previous one
        self.token_repo.invalidate_unused_for_user(user_id, now)

        raw_token = secrets.token_urlsafe(RESET_TOKEN_BYTES)
        expires_at = now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        self.token_repo.create(user_id, hash_reset_token(raw_token), expires_at)
        return raw_token

    def _get_usable_token(self, raw_token: Optional[str]):
        if is_blank(raw_token):
            raise self._invalid_link_error()

        token_record = self.token_repo.get_by_hash(hash_reset_token(raw_token.strip()))
        if not token_record or token_record.used_at is not None:
            raise self._invalid_link_error()

        if self.now_provider() >= as_utc(token_record.expires_at):
            raise self._invalid_link_error()
        return token_record

    @staticmethod
    def _invalid_link_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RESET_LINK_MESSAGE,
        )

    @staticmethod
    def _build_reset_email(to_address: str, raw_token: str) -> OutgoingEmail:
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        minutes = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        body = (
            "Recibimos una solicitud para restablecer la contraseña de tu cuenta de BoletoYa.\n\n"
            f"Para elegir una nueva contraseña ingresa al siguiente enlace "
            f"(vence en {minutes} minutos y solo puede usarse una vez):\n\n"
            f"{reset_link}\n\n"
            "Si no solicitaste este cambio, ignora este mensaje."
        )
        return OutgoingEmail(to_address=to_address, subject=RESET_EMAIL_SUBJECT, body=body)
