from src.schemas.validators import (
    normalize_email,
    validate_ecuadorian_cedula,
    validate_email_format,
    validate_name_format,
    validate_passport,
    validate_password_format,
)


def test_cedula_validation():
    """13.6: Test Ecuadorian cédula modulo-10 algorithm for valid and invalid numbers."""
    # Valid Ecuadorian cédulas (examples from Pichincha, Guayas, Loja, Azuay)
    valid_cedulas = [
        "1710034065",
        "0926691452",
        "1104609829",
        "0102555547",
    ]
    for cedula in valid_cedulas:
        assert validate_ecuadorian_cedula(cedula) is True, f"Failed on valid {cedula}"

    # Invalid cédulas
    invalid_cedulas = [
        "1710034066",  # wrong check digit
        "1234567890",  # invalid checksum
        "9910034065",  # province 99 invalid
        "1780034065",  # 3rd digit 8 >= 6
        "171003406",   # 9 digits
        "17100340651", # 11 digits
        "abcdefghij",  # non-numeric
        "",            # empty
    ]
    for cedula in invalid_cedulas:
        assert validate_ecuadorian_cedula(cedula) is False, f"Failed on invalid {cedula}"


def test_passport_validation():
    """13.7: Test passport alphanumeric validation (6-20 chars)."""
    valid_passports = [
        "A1234567",
        "PASS123456",
        "EC987654321",
        "12345678",
    ]
    for p in valid_passports:
        assert validate_passport(p) is True, f"Failed on valid passport {p}"

    invalid_passports = [
        "A1234",          # too short (<6)
        "A" * 21,         # too long (>20)
        "PASS-1234",      # hyphen not allowed in passport
        "PASS@123",       # special char
        "PASS 123",       # space
        "",
    ]
    for p in invalid_passports:
        assert validate_passport(p) is False, f"Failed on invalid passport {p}"


def test_email_normalization():
    """13.8: Test trim and lowercase email normalization."""
    raw_email = "  J.Perez@Email.Com  "
    normalized = normalize_email(raw_email)
    assert normalized == "j.perez@email.com"


def test_name_validation():
    """Validate allowed Unicode characters in names and length constraints."""
    valid_names = [
        "Juan Carlos",
        "María-José",
        "O'Connor",
        "Ángel René",
    ]
    for n in valid_names:
        assert validate_name_format(n) is True, f"Failed on valid name {n}"

    invalid_names = [
        "Juan123",
        "Maria_Jose",
        "Carlos@home",
        "A" * 51,
        "",
    ]
    for n in invalid_names:
        assert validate_name_format(n) is False, f"Failed on invalid name {n}"


def test_password_format_validation():
    """Validate password rules (min 8 chars, uppercase, lowercase, digit)."""
    assert validate_password_format("Valid123") is True
    assert validate_password_format("Val1d!@#$") is True
    assert validate_password_format("short1A") is False  # < 8 chars
    assert validate_password_format("alllowercase1") is False
    assert validate_password_format("ALLUPPERCASE1") is False
    assert validate_password_format("NoDigitsHere") is False
