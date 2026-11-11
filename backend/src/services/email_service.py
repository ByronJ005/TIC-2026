"""Outgoing email: a port (EmailSender) and its SMTP adapter.

Setup with Mailtrap Email Sandbox (free, emails are trapped and never delivered):
1. Create an account at mailtrap.io and open Email Testing > Inboxes > "My Inbox".
2. Open the "SMTP Settings" tab of the inbox and copy host, port, username and password.
3. Put them in backend/.env as SMTP_HOST, SMTP_PORT, SMTP_USERNAME and SMTP_PASSWORD
   (see backend/.env.example for the full list of variables).
4. Sent emails appear inside the Mailtrap inbox. Switching provider only requires
   changing these environment variables.
"""
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import Protocol

from src.core.config import settings

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 15


class EmailDeliveryError(Exception):
    """Raised when an email cannot be delivered (never includes secrets)."""


class EmailSender(Protocol):
    def send(self, to_address: str, subject: str, body: str) -> None: ...


class SmtpEmailSender:
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.from_address = settings.MAIL_FROM_ADDRESS
        self.from_name = settings.MAIL_FROM_NAME

    def send(self, to_address: str, subject: str, body: str) -> None:
        if not self.host:
            raise EmailDeliveryError("SMTP no está configurado")

        message = EmailMessage()
        message["From"] = formataddr((self.from_name, self.from_address))
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(self.host, self.port, timeout=SMTP_TIMEOUT_SECONDS) as server:
                if self.use_tls:
                    server.starttls()
                if self.username:
                    server.login(self.username, self.password)
                server.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            # Only the exception type is logged: messages may echo credentials or addresses
            logger.error("Fallo al enviar correo: %s", type(exc).__name__)
            raise EmailDeliveryError("No se pudo enviar el correo") from exc


def get_email_sender() -> EmailSender:
    return SmtpEmailSender()

