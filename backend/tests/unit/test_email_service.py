import smtplib
from unittest.mock import patch

import pytest

from src.services.email_service import EmailDeliveryError, SmtpEmailSender


@pytest.fixture
def configured_sender(monkeypatch):
    from src.core import config

    monkeypatch.setattr(config.settings, "SMTP_HOST", "smtp.test.local")
    monkeypatch.setattr(config.settings, "SMTP_PORT", 2525)
    monkeypatch.setattr(config.settings, "SMTP_USERNAME", "user-test")
    monkeypatch.setattr(config.settings, "SMTP_PASSWORD", "secret-pass-test")
    monkeypatch.setattr(config.settings, "SMTP_USE_TLS", True)
    monkeypatch.setattr(config.settings, "MAIL_FROM_ADDRESS", "no-reply@boletoya.local")
    monkeypatch.setattr(config.settings, "MAIL_FROM_NAME", "BoletoYa")
    return SmtpEmailSender()


def test_send_uses_starttls_login_and_builds_message(configured_sender):
    with patch("src.services.email_service.smtplib.SMTP") as smtp_class:
        server = smtp_class.return_value.__enter__.return_value

        configured_sender.send("dest@example.com", "Asunto", "Cuerpo del mensaje")

    smtp_class.assert_called_once()
    assert smtp_class.call_args.args[:2] == ("smtp.test.local", 2525)
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("user-test", "secret-pass-test")
    sent_message = server.send_message.call_args.args[0]
    assert sent_message["To"] == "dest@example.com"
    assert sent_message["Subject"] == "Asunto"
    assert "no-reply@boletoya.local" in sent_message["From"]
    assert "BoletoYa" in sent_message["From"]
    assert "Cuerpo del mensaje" in sent_message.get_content()


def test_send_skips_tls_when_disabled(configured_sender):
    configured_sender.use_tls = False
    with patch("src.services.email_service.smtplib.SMTP") as smtp_class:
        server = smtp_class.return_value.__enter__.return_value

        configured_sender.send("dest@example.com", "Asunto", "Cuerpo")

    server.starttls.assert_not_called()


def test_send_skips_login_without_username(configured_sender):
    configured_sender.username = ""
    with patch("src.services.email_service.smtplib.SMTP") as smtp_class:
        server = smtp_class.return_value.__enter__.return_value

        configured_sender.send("dest@example.com", "Asunto", "Cuerpo")

    server.login.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [smtplib.SMTPAuthenticationError(535, b"bad"), smtplib.SMTPException("fail"), ConnectionRefusedError()],
)
def test_send_wraps_connection_and_smtp_errors(configured_sender, error):
    with patch("src.services.email_service.smtplib.SMTP", side_effect=error):
        with pytest.raises(EmailDeliveryError):
            configured_sender.send("dest@example.com", "Asunto", "Cuerpo")


def test_send_without_smtp_host_raises_configuration_error(configured_sender):
    configured_sender.host = ""

    with patch("src.services.email_service.smtplib.SMTP") as smtp_class:
        with pytest.raises(EmailDeliveryError):
            configured_sender.send("dest@example.com", "Asunto", "Cuerpo")

    smtp_class.assert_not_called()


def test_error_log_never_contains_credentials_or_recipient(configured_sender, caplog):
    with patch(
        "src.services.email_service.smtplib.SMTP",
        side_effect=smtplib.SMTPAuthenticationError(535, b"secret-pass-test dest@example.com"),
    ):
        with pytest.raises(EmailDeliveryError):
            configured_sender.send("dest@example.com", "Asunto", "Cuerpo con token=abc")

    assert "secret-pass-test" not in caplog.text
    assert "dest@example.com" not in caplog.text
    assert "token=abc" not in caplog.text


def test_send_closes_connection_context_even_on_send_failure(configured_sender):
    with patch("src.services.email_service.smtplib.SMTP") as smtp_class:
        server = smtp_class.return_value.__enter__.return_value
        server.send_message.side_effect = smtplib.SMTPException("boom")

        with pytest.raises(EmailDeliveryError):
            configured_sender.send("dest@example.com", "Asunto", "Cuerpo")

    smtp_class.return_value.__exit__.assert_called_once()
