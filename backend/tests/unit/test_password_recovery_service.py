import re
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from src.core.config import settings
from src.core.security import hash_password, verify_password
from src.models.password_reset_token import PasswordResetToken
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.password_recovery_schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.schemas.validators import (
    ERROR_EMAIL_REQUIRED,
    ERROR_INVALID_EMAIL,
    ERROR_INVALID_PASSWORD,
    ERROR_REQUIRED_FIELD,
)
from src.services.password_recovery_service import (
    EMAIL_NOT_REGISTERED_MESSAGE,
    INVALID_RESET_LINK_MESSAGE,
    PASSWORD_RESET_SUCCESS_MESSAGE,
    RESET_REQUEST_PROCESSED_MESSAGE,
    PasswordRecoveryService,
    hash_reset_token,
)
from tests.unit.fakes import FakeEmailSender

OLD_PASSWORD = "OldPass123"
NEW_PASSWORD = "NewPass456"
START_TIME = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)


class FakeClock:
    def __init__(self, start: datetime = START_TIME):
        self.current = start

    def __call__(self) -> datetime:
        return self.current

    def advance(self, **delta) -> None:
        self.current += timedelta(**delta)


def create_user(db, email="ana@example.com", doc="1710034065", is_active=True) -> User:
    user = User(
        document_type=DocumentType.CEDULA,
        document_number=doc,
        first_name="Ana",
        last_name="Gomez",
        email=email,
        hashed_password=hash_password(OLD_PASSWORD),
        is_active=is_active,
    )
    user.roles = [UserRole.PASAJERO]
    return UserRepository(db).create(user)


@pytest.fixture
def sender():
    return FakeEmailSender()


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(db_session, sender, clock):
    return PasswordRecoveryService(db_session, sender, now_provider=clock)


def request_and_deliver(service, email: str):
    result = service.request_reset(ForgotPasswordRequest(email=email))
    if result.email:
        service.deliver_email(result.email)
    return result


def extract_token(sender: FakeEmailSender, index: int = -1) -> str:
    body = sender.sent_messages[index]["body"]
    return re.search(r"token=(\S+)", body).group(1)


def reset(service, token, password=NEW_PASSWORD):
    return service.reset_password(ResetPasswordRequest(token=token, new_password=password))


def assert_http_error(exc_info, status_code, detail):
    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == detail


# ---------------------------------------------------------------- request_reset


def test_request_for_active_account_sends_email_with_link(db_session, service, sender):
    create_user(db_session)

    result = request_and_deliver(service, "ana@example.com")

    assert result.response.message == RESET_REQUEST_PROCESSED_MESSAGE
    assert len(sender.sent_messages) == 1
    message = sender.sent_messages[0]
    assert message["to"] == "ana@example.com"
    assert f"{settings.FRONTEND_URL}/reset-password?token=" in message["body"]
    assert str(settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES) in message["body"]


def test_request_normalizes_email_case_and_spaces(db_session, service, sender):
    create_user(db_session)

    request_and_deliver(service, "  Ana@Example.COM ")

    assert len(sender.sent_messages) == 1


@pytest.mark.parametrize("blank_email", [None, "", "   ", "\t\n"])
def test_request_with_blank_email_is_rejected(service, sender, blank_email):
    with pytest.raises(HTTPException) as exc_info:
        service.request_reset(ForgotPasswordRequest(email=blank_email))

    assert_http_error(exc_info, 422, ERROR_EMAIL_REQUIRED)
    assert sender.sent_messages == []


@pytest.mark.parametrize("bad_email", ["sin-arroba", "a@b", "a@b.c", "@dominio.com", "a b@c.com"])
def test_request_with_invalid_email_format_is_rejected(service, sender, bad_email):
    with pytest.raises(HTTPException) as exc_info:
        service.request_reset(ForgotPasswordRequest(email=bad_email))

    assert_http_error(exc_info, 422, ERROR_INVALID_EMAIL)
    assert sender.sent_messages == []


def test_request_for_unregistered_email_returns_not_found_without_sending(service, sender):
    with pytest.raises(HTTPException) as exc_info:
        service.request_reset(ForgotPasswordRequest(email="nadie@example.com"))

    assert_http_error(exc_info, 404, EMAIL_NOT_REGISTERED_MESSAGE)
    assert sender.sent_messages == []


def test_request_for_inactive_account_answers_like_success_without_email_or_token(
    db_session, service, sender
):
    create_user(db_session, is_active=False)

    result = request_and_deliver(service, "ana@example.com")

    assert result.response.message == RESET_REQUEST_PROCESSED_MESSAGE
    assert result.email is None
    assert sender.sent_messages == []
    assert db_session.query(PasswordResetToken).count() == 0


def test_token_is_stored_hashed_and_never_in_clear(db_session, service, sender):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    raw_token = extract_token(sender)

    stored = db_session.query(PasswordResetToken).one()

    assert stored.token_hash == hash_reset_token(raw_token)
    assert stored.token_hash != raw_token
    assert raw_token not in stored.token_hash


def test_token_expiration_follows_configured_validity(db_session, service, sender, clock):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")

    stored = db_session.query(PasswordResetToken).one()

    expected = START_TIME + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    assert stored.expires_at.replace(tzinfo=timezone.utc) == expected


def test_each_request_generates_a_different_token(db_session, service, sender):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    request_and_deliver(service, "ana@example.com")

    assert extract_token(sender, 0) != extract_token(sender, 1)


def test_email_delivery_failure_is_swallowed(db_session, clock):
    failing_sender = FakeEmailSender(should_fail=True)
    service = PasswordRecoveryService(db_session, failing_sender, now_provider=clock)
    create_user(db_session)

    result = service.request_reset(ForgotPasswordRequest(email="ana@example.com"))
    service.deliver_email(result.email)  # must not raise

    assert result.response.message == RESET_REQUEST_PROCESSED_MESSAGE


# --------------------------------------------------------------- reset_password


def test_reset_with_valid_token_changes_password_and_marks_token_used(
    db_session, service, sender, clock
):
    user = create_user(db_session)
    request_and_deliver(service, "ana@example.com")

    response = reset(service, extract_token(sender))

    db_session.refresh(user)
    assert response.message == PASSWORD_RESET_SUCCESS_MESSAGE
    assert verify_password(NEW_PASSWORD, user.hashed_password)
    assert not verify_password(OLD_PASSWORD, user.hashed_password)
    assert user.password_changed_at is not None
    assert db_session.query(PasswordResetToken).one().used_at is not None


def test_token_just_before_expiration_is_still_valid(db_session, service, sender, clock):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    clock.advance(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES, seconds=-1)

    response = reset(service, extract_token(sender))

    assert response.message == PASSWORD_RESET_SUCCESS_MESSAGE


def test_token_exactly_at_expiration_is_rejected(db_session, service, sender, clock):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    clock.advance(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)

    with pytest.raises(HTTPException) as exc_info:
        reset(service, extract_token(sender))

    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)


def test_expired_token_does_not_change_password(db_session, service, sender, clock):
    user = create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    clock.advance(hours=3)

    with pytest.raises(HTTPException):
        reset(service, extract_token(sender))

    db_session.refresh(user)
    assert verify_password(OLD_PASSWORD, user.hashed_password)
    assert user.password_changed_at is None


def test_reused_token_is_rejected(db_session, service, sender):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    token = extract_token(sender)
    reset(service, token)

    with pytest.raises(HTTPException) as exc_info:
        reset(service, token, password="Another789")

    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)


def test_new_request_invalidates_previous_link(db_session, service, sender):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    request_and_deliver(service, "ana@example.com")
    first_token, second_token = extract_token(sender, 0), extract_token(sender, 1)

    with pytest.raises(HTTPException) as exc_info:
        reset(service, first_token)
    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)

    assert reset(service, second_token).message == PASSWORD_RESET_SUCCESS_MESSAGE


def test_other_pending_tokens_are_invalidated_after_successful_reset(db_session, service):
    user = create_user(db_session)
    expires_at = START_TIME + timedelta(minutes=10)
    service.token_repo.create(user.id, hash_reset_token("valid-link"), expires_at)
    service.token_repo.create(user.id, hash_reset_token("other-pending"), expires_at)

    reset(service, "valid-link")

    unused_tokens = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.used_at.is_(None))
        .count()
    )
    assert unused_tokens == 0

@pytest.mark.parametrize("token", [None, "", "   ", "no-existe", "a" * 500, "token con espacios raros"])
def test_missing_unknown_or_malformed_token_gets_generic_error(service, token):
    with pytest.raises(HTTPException) as exc_info:
        reset(service, token)

    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)


def test_tampered_token_is_rejected(db_session, service, sender):
    create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    token = extract_token(sender)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(HTTPException) as exc_info:
        reset(service, tampered)

    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)


def test_token_of_account_deactivated_after_request_is_rejected(db_session, service, sender):
    user = create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    user.is_active = False
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        reset(service, extract_token(sender))

    assert_http_error(exc_info, 400, INVALID_RESET_LINK_MESSAGE)


@pytest.mark.parametrize(
    "bad_password,detail",
    [
        ("corta1A", ERROR_INVALID_PASSWORD),
        ("sinmayuscula1", ERROR_INVALID_PASSWORD),
        ("SINMINUSCULA1", ERROR_INVALID_PASSWORD),
        ("SinNumeros", ERROR_INVALID_PASSWORD),
        ("", ERROR_REQUIRED_FIELD),
        ("        ", ERROR_REQUIRED_FIELD),
        (None, ERROR_REQUIRED_FIELD),
    ],
)
def test_invalid_new_password_is_rejected_without_consuming_token(
    db_session, service, sender, bad_password, detail
):
    user = create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    token = extract_token(sender)

    with pytest.raises(HTTPException) as exc_info:
        reset(service, token, password=bad_password)

    assert_http_error(exc_info, 422, detail)
    db_session.refresh(user)
    assert verify_password(OLD_PASSWORD, user.hashed_password)
    assert db_session.query(PasswordResetToken).one().used_at is None
    assert reset(service, token).message == PASSWORD_RESET_SUCCESS_MESSAGE


def test_password_changed_at_is_set_to_reset_time(db_session, service, sender, clock):
    user = create_user(db_session)
    request_and_deliver(service, "ana@example.com")
    clock.advance(minutes=5)

    reset(service, extract_token(sender))

    db_session.refresh(user)
    assert user.password_changed_at.replace(tzinfo=timezone.utc) == clock.current
