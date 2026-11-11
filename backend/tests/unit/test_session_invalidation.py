from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from src.core.dependencies import (
    get_current_user,
    get_token_payload,
    token_was_issued_before_password_change,
)
from src.core.security import create_access_token, decode_access_token, hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository

CHANGED_AT = datetime(2026, 11, 10, 12, 0, 30, 500000, tzinfo=timezone.utc)
CHANGED_AT_SECONDS = int(CHANGED_AT.timestamp())


def make_user(password_changed_at=None) -> User:
    user = User(
        document_type=DocumentType.CEDULA,
        document_number="1710034065",
        first_name="Ana",
        last_name="Gomez",
        email="ana@example.com",
        hashed_password=hash_password("Pass1234"),
        is_active=True,
        password_changed_at=password_changed_at,
    )
    return user


def test_token_issued_before_change_is_rejected():
    user = make_user(CHANGED_AT)

    assert token_was_issued_before_password_change({"iat": CHANGED_AT_SECONDS - 1}, user) is True


def test_token_issued_in_same_second_as_change_is_accepted():
    user = make_user(CHANGED_AT)

    assert token_was_issued_before_password_change({"iat": CHANGED_AT_SECONDS}, user) is False


def test_token_issued_after_change_is_accepted():
    user = make_user(CHANGED_AT)

    assert token_was_issued_before_password_change({"iat": CHANGED_AT_SECONDS + 3600}, user) is False


def test_user_that_never_changed_password_is_not_affected():
    user = make_user(None)

    assert token_was_issued_before_password_change({"iat": 0}, user) is False
    assert token_was_issued_before_password_change({}, user) is False


def test_token_without_iat_is_rejected_when_password_was_changed():
    user = make_user(CHANGED_AT)

    assert token_was_issued_before_password_change({}, user) is True


def test_naive_stored_datetime_is_treated_as_utc():
    naive_changed_at = CHANGED_AT.replace(tzinfo=None)
    user = make_user(naive_changed_at)

    assert token_was_issued_before_password_change({"iat": CHANGED_AT_SECONDS - 1}, user) is True
    assert token_was_issued_before_password_change({"iat": CHANGED_AT_SECONDS}, user) is False


def persist_user(db_session, password_changed_at) -> User:
    user = make_user(password_changed_at)
    user.roles = [UserRole.PASAJERO]
    return UserRepository(db_session).create(user)


def resolve_current_user(db_session, user: User) -> User:
    token = create_access_token(subject=user.id)
    payload = decode_access_token(token)
    return get_current_user(payload=payload, db=db_session)


def test_get_current_user_rejects_session_older_than_password_change(db_session):
    # A change dated in the future makes any token issued now older than the change
    user = persist_user(db_session, datetime.now(timezone.utc) + timedelta(hours=1))

    with pytest.raises(HTTPException) as exc_info:
        resolve_current_user(db_session, user)

    assert exc_info.value.status_code == 401


def test_get_current_user_accepts_session_issued_after_password_change(db_session):
    user = persist_user(db_session, datetime.now(timezone.utc) - timedelta(hours=1))

    assert resolve_current_user(db_session, user).id == user.id


def test_get_current_user_accepts_user_without_password_change(db_session):
    user = persist_user(db_session, None)

    assert resolve_current_user(db_session, user).id == user.id


def test_get_token_payload_is_unchanged_for_valid_tokens(db_session):
    token = create_access_token(subject=7)

    payload = get_token_payload(token=token, db=db_session)

    assert payload["sub"] == "7"

