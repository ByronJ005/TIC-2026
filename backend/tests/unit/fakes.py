from typing import List

from src.services.email_service import EmailDeliveryError


class FakeEmailSender:
    """In-memory EmailSender used by unit tests so no real SMTP traffic happens."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.sent_messages: List[dict] = []

    def send(self, to_address: str, subject: str, body: str) -> None:
        if self.should_fail:
            raise EmailDeliveryError("fallo simulado")
        self.sent_messages.append(
            {"to": to_address, "subject": subject, "body": body}
        )

