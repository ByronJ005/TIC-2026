from datetime import date

import pytest

from src.schemas.validators import (
    ERROR_PHONE_LENGTH,
    ERROR_PHONE_NOT_NUMERIC,
    get_phone_error,
    validate_address_length,
    validate_birth_date,
    validate_phone_format,
)


@pytest.mark.parametrize("phone", ["0991234567", "0000000000"])
def test_phone_with_exactly_ten_digits_is_valid(phone):
    assert validate_phone_format(phone) is True
    assert get_phone_error(phone) is None


@pytest.mark.parametrize("phone", [None, "", "   "])
def test_blank_phone_is_valid_because_it_is_optional(phone):
    assert validate_phone_format(phone) is True


@pytest.mark.parametrize("phone", ["099123456", "09912345678", "1", "0" * 30])
def test_phone_with_wrong_length_reports_length_error(phone):
    assert get_phone_error(phone) == ERROR_PHONE_LENGTH
    assert validate_phone_format(phone) is False


@pytest.mark.parametrize(
    "phone",
    [
        "09912345ab",
        "099-123-456",
        "099 123 4567",
        " 0991234567",
        "0991234567 ",
        "+593991234",
        "099123456\n",
        "٠٩٩١٢٣٤٥٦٧",  # Arabic-Indic digits are not ASCII digits
    ],
)
def test_phone_with_non_numeric_characters_reports_numeric_error(phone):
    assert get_phone_error(phone) == ERROR_PHONE_NOT_NUMERIC


def test_non_numeric_error_takes_precedence_over_length_error():
    assert get_phone_error("abc") == ERROR_PHONE_NOT_NUMERIC


@pytest.mark.parametrize("length,is_valid", [(1, True), (149, True), (150, True), (151, False)])
def test_address_length_boundaries(length, is_valid):
    assert validate_address_length("a" * length) is is_valid


@pytest.mark.parametrize("address", [None, "", "    "])
def test_blank_address_is_valid(address):
    assert validate_address_length(address) is True


def test_address_length_is_measured_without_surrounding_spaces():
    assert validate_address_length("  " + "a" * 150 + "  ") is True


TODAY = date(2026, 11, 10)


@pytest.mark.parametrize(
    "birth_date,is_valid",
    [
        (date(1899, 12, 31), False),
        (date(1900, 1, 1), True),
        (date(1985, 6, 15), True),
        (date(2026, 11, 9), True),
        (TODAY, True),
        (date(2026, 11, 11), False),
        (date(2026, 12, 31), False),
        (date(2027, 1, 1), False),
    ],
)
def test_birth_date_range_boundaries(birth_date, is_valid):
    assert validate_birth_date(birth_date, today=TODAY) is is_valid


def test_birth_date_is_optional():
    assert validate_birth_date(None, today=TODAY) is True


def test_birth_date_upper_bound_follows_reference_day_not_a_fixed_year():
    future_in_2030 = date(2030, 3, 1)

    assert validate_birth_date(future_in_2030, today=TODAY) is False
    assert validate_birth_date(future_in_2030, today=date(2030, 3, 1)) is True


def test_birth_date_without_reference_uses_current_date():
    assert validate_birth_date(date.today()) is True
    assert validate_birth_date(date(date.today().year + 1, 1, 1)) is False

