from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from src.core.security import decode_access_token, hash_password, verify_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.profile_schemas import ProfileUpdate
from src.schemas.validators import (
    ERROR_ADDRESS_TOO_LONG,
    ERROR_CURRENT_PASSWORD_REQUIRED,
    ERROR_CURRENT_PASSWORD_WRONG,
    ERROR_INVALID_BIRTH_DATE,
    ERROR_INVALID_NAME,
    ERROR_INVALID_PASSWORD,
    ERROR_MANDATORY_FIELDS_EMPTY,
    ERROR_NEW_PASSWORD_SAME_AS_CURRENT,
    ERROR_PASSWORD_CONFIRMATION_MISMATCH,
    ERROR_PHONE_LENGTH,
    ERROR_PHONE_NOT_NUMERIC,
    ERROR_REQUIRED_FIELD,
)
from src.services.profile_service import (
    PASSWORD_UPDATED_MESSAGE,
    PROFILE_UPDATED_MESSAGE,
    ProfileService,
)

CURRENT_PASSWORD = "OldPass123"
NEW_PASSWORD = "NewPass456"
TODAY = date(2026, 11, 10)
NOW = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)


def create_user(db) -> User:
    user = User(
        document_type=DocumentType.CEDULA,
        document_number="1710034065",
        first_name="Ana",
        last_name="Gomez",
        email="ana@example.com",
        hashed_password=hash_password(CURRENT_PASSWORD),
        is_active=True,
        phone="0991234567",
        address="Calle Falsa 123",
        birth_date=date(1990, 5, 20),
    )
    user.roles = [UserRole.PASAJERO]
    return UserRepository(db).create(user)


@pytest.fixture
def user(db_session):
    return create_user(db_session)


@pytest.fixture
def service(db_session):
    return ProfileService(db_session, today_provider=lambda: TODAY, now_provider=lambda: NOW)


def build_update(**overrides) -> ProfileUpdate:
    values = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "phone": "0991234567",
        "address": "Calle Falsa 123",
        "birth_date": "1990-05-20",
    }
    values.update(overrides)
    return ProfileUpdate(**values)


def assert_rejected(service, user, update, status_code, detail):
    with pytest.raises(HTTPException) as exc_info:
        service.update_profile(user, update)
    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == detail


def assert_user_unchanged(db_session, user):
    db_session.refresh(user)
    assert user.first_name == "Ana"
    assert user.last_name == "Gomez"
    assert user.phone == "0991234567"
    assert user.address == "Calle Falsa 123"
    assert user.birth_date == date(1990, 5, 20)
    assert verify_password(CURRENT_PASSWORD, user.hashed_password)
    assert user.password_changed_at is None


# ----------------------------------------------------------- personal data


def test_update_personal_data_without_password_keeps_password(db_session, service, user):
    result = service.update_profile(
        user,
        build_update(first_name="María José", last_name="Pérez", phone="0987654321",
                     address="Av. Siempre Viva 742", birth_date="1985-01-31"),
    )

    db_session.refresh(user)
    assert result.message == PROFILE_UPDATED_MESSAGE
    assert result.access_token is None
    assert (user.first_name, user.last_name) == ("María José", "Pérez")
    assert user.phone == "0987654321"
    assert user.birth_date == date(1985, 1, 31)
    assert verify_password(CURRENT_PASSWORD, user.hashed_password)
    assert user.password_changed_at is None


def test_update_without_changes_succeeds(db_session, service, user):
    result = service.update_profile(user, build_update())

    assert result.message == PROFILE_UPDATED_MESSAGE
    assert_user_unchanged(db_session, user)


def test_names_are_trimmed(db_session, service, user):
    service.update_profile(user, build_update(first_name="  Ana  ", last_name=" Gomez "))

    db_session.refresh(user)
    assert (user.first_name, user.last_name) == ("Ana", "Gomez")


@pytest.mark.parametrize("field", ["first_name", "last_name"])
@pytest.mark.parametrize("blank_value", [None, "", "   ", "\t"])
def test_blank_required_names_are_rejected(db_session, service, user, field, blank_value):
    assert_rejected(
        service, user, build_update(**{field: blank_value}), 422, ERROR_MANDATORY_FIELDS_EMPTY
    )
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("field", ["first_name", "last_name"])
@pytest.mark.parametrize("invalid_value", ["Ana123", "Ana@", "J0hn", "a" * 51, "Ana_Gomez", "Ana!"])
def test_names_with_invalid_characters_or_length_are_rejected(
    db_session, service, user, field, invalid_value
):
    assert_rejected(
        service, user, build_update(**{field: invalid_value}), 422, ERROR_INVALID_NAME
    )
    assert_user_unchanged(db_session, user)


def test_name_of_exactly_fifty_characters_is_accepted(service, user):
    result = service.update_profile(user, build_update(first_name="a" * 50))

    assert result.user.first_name == "a" * 50


def test_blank_optional_fields_are_stored_as_null(db_session, service, user):
    service.update_profile(user, build_update(phone="  ", address="", birth_date=None))

    db_session.refresh(user)
    assert user.phone is None
    assert user.address is None
    assert user.birth_date is None


@pytest.mark.parametrize("phone", ["099123456", "09912345678"])
def test_phone_with_wrong_length_is_rejected(db_session, service, user, phone):
    assert_rejected(service, user, build_update(phone=phone), 422, ERROR_PHONE_LENGTH)
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("phone", ["09912345ab", "099-123-456", "099 123 4567", "+593991234"])
def test_phone_with_non_numeric_characters_is_rejected(db_session, service, user, phone):
    assert_rejected(service, user, build_update(phone=phone), 422, ERROR_PHONE_NOT_NUMERIC)
    assert_user_unchanged(db_session, user)


def test_address_over_limit_is_rejected_and_limit_is_accepted(service, user):
    assert_rejected(service, user, build_update(address="a" * 151), 422, ERROR_ADDRESS_TOO_LONG)

    result = service.update_profile(user, build_update(address="a" * 150))
    assert result.user.address == "a" * 150


@pytest.mark.parametrize(
    "birth_date",
    ["1899-12-31", "2026-11-11", "2026-12-31", "2027-01-01", "no-es-fecha", "2025-02-30", "31/12/1990"],
)
def test_invalid_birth_dates_are_rejected(db_session, service, user, birth_date):
    assert_rejected(
        service, user, build_update(birth_date=birth_date), 422, ERROR_INVALID_BIRTH_DATE
    )
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("birth_date", ["1900-01-01", "2026-11-10"])
def test_birth_date_limits_are_accepted(service, user, birth_date):
    result = service.update_profile(user, build_update(birth_date=birth_date))

    assert result.user.birth_date == date.fromisoformat(birth_date)


def test_email_and_document_cannot_be_changed_through_profile_update(db_session, service, user):
    update = ProfileUpdate(
        first_name="Ana", last_name="Gomez", email="otro@example.com", document_number="0000000000"
    )
    assert not hasattr(update, "email")
    assert not hasattr(update, "document_number")

    service.update_profile(user, update)

    db_session.refresh(user)
    assert user.email == "ana@example.com"
    assert user.document_number == "1710034065"


# ----------------------------------------------------------- password change


def password_update(**overrides) -> ProfileUpdate:
    values = {
        "current_password": CURRENT_PASSWORD,
        "new_password": NEW_PASSWORD,
        "confirm_password": NEW_PASSWORD,
    }
    values.update(overrides)
    return build_update(**values)


def test_password_change_succeeds_and_returns_fresh_token(db_session, service, user):
    result = service.update_profile(user, password_update(first_name="Anita"))

    db_session.refresh(user)
    assert result.message == PASSWORD_UPDATED_MESSAGE
    assert verify_password(NEW_PASSWORD, user.hashed_password)
    assert user.first_name == "Anita"
    assert user.password_changed_at.replace(tzinfo=timezone.utc) == NOW
    payload = decode_access_token(result.access_token)
    assert payload["sub"] == str(user.id)
    assert result.token_type == "bearer"


@pytest.mark.parametrize("blank", ["", "   ", None])
def test_all_blank_password_fields_mean_no_password_change(db_session, service, user, blank):
    result = service.update_profile(
        user,
        build_update(current_password=blank, new_password=blank, confirm_password=blank),
    )

    assert result.access_token is None
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("blank_current", ["", "   ", None])
def test_new_password_without_current_is_rejected(db_session, service, user, blank_current):
    assert_rejected(
        service, user, password_update(current_password=blank_current),
        422, ERROR_CURRENT_PASSWORD_REQUIRED,
    )
    assert_user_unchanged(db_session, user)


def test_only_confirmation_filled_requires_current_password(db_session, service, user):
    update = build_update(confirm_password=NEW_PASSWORD)

    assert_rejected(service, user, update, 422, ERROR_CURRENT_PASSWORD_REQUIRED)
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("missing_field", ["new_password", "confirm_password"])
@pytest.mark.parametrize("blank", ["", "  ", None])
def test_current_password_without_new_or_confirmation_is_rejected(
    db_session, service, user, missing_field, blank
):
    assert_rejected(
        service, user, password_update(**{missing_field: blank}), 422, ERROR_REQUIRED_FIELD
    )
    assert_user_unchanged(db_session, user)


def test_wrong_current_password_is_rejected(db_session, service, user):
    assert_rejected(
        service, user, password_update(current_password="WrongPass999"),
        400, ERROR_CURRENT_PASSWORD_WRONG,
    )
    assert_user_unchanged(db_session, user)


def test_new_password_equal_to_current_is_rejected(db_session, service, user):
    assert_rejected(
        service,
        user,
        password_update(new_password=CURRENT_PASSWORD, confirm_password=CURRENT_PASSWORD),
        422,
        ERROR_NEW_PASSWORD_SAME_AS_CURRENT,
    )
    assert_user_unchanged(db_session, user)


@pytest.mark.parametrize("weak", ["corta1A", "sinmayuscula1", "SINMINUSCULA1", "SinNumeros"])
def test_new_password_with_invalid_format_is_rejected(db_session, service, user, weak):
    assert_rejected(
        service, user, password_update(new_password=weak, confirm_password=weak),
        422, ERROR_INVALID_PASSWORD,
    )
    assert_user_unchanged(db_session, user)


def test_confirmation_mismatch_is_rejected(db_session, service, user):
    assert_rejected(
        service, user, password_update(confirm_password="Different789"),
        422, ERROR_PASSWORD_CONFIRMATION_MISMATCH,
    )
    assert_user_unchanged(db_session, user)


def test_password_failure_does_not_persist_other_changes(db_session, service, user):
    update = password_update(
        first_name="Cambiado", phone="0911111111", current_password="WrongPass999"
    )

    with pytest.raises(HTTPException):
        service.update_profile(user, update)

    assert_user_unchanged(db_session, user)


def test_new_token_is_not_older_than_password_change(db_session, user):
    real_clock_service = ProfileService(db_session, today_provider=lambda: TODAY)

    result = real_clock_service.update_profile(user, password_update())

    db_session.refresh(user)
    payload = decode_access_token(result.access_token)
    changed_at = user.password_changed_at.replace(tzinfo=timezone.utc)
    assert payload["iat"] >= int(changed_at.timestamp())


def test_get_profile_returns_current_data(service, user):
    profile = service.get_profile(user)

    assert profile.email == "ana@example.com"
    assert profile.phone == "0991234567"
    assert profile.birth_date == date(1990, 5, 20)

