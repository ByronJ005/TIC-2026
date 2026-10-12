import re
from typing import Tuple

# Error message constants matching specification exactly
ERROR_INVALID_DOCUMENT = "El número de documento proporcionado es inválido"
ERROR_INVALID_NAME = "Los nombres/apellidos proporcionados contienen caracteres inválidos"
ERROR_INVALID_EMAIL = "Correo electrónico inválido"
ERROR_INVALID_PASSWORD = (
    "La contraseña debe incluir al menos una mayúscula, minúscula, número "
    "y carácter especial opcional"
)
ERROR_REQUIRED_FIELD = "Este campo es requerido"

NAME_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]{1,50}$")
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)
PASSPORT_REGEX = re.compile(r"^[a-zA-Z0-9]{6,20}$")


def validate_ecuadorian_cedula(cedula: str) -> bool:
    """
    Validates Ecuadorian national identity card (Cédula de Identidad)
    using the modulo 10 verification algorithm.
    """
    if not isinstance(cedula, str) or not cedula.isdigit() or len(cedula) != 10:
        return False

    province = int(cedula[:2])
    if province < 1 or (province > 24 and province != 30):
        return False

    third_digit = int(cedula[2])
    if third_digit >= 6:
        return False

    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total_sum = 0

    for digit_char, coeff in zip(cedula[:9], coefficients):
        product = int(digit_char) * coeff
        if product >= 10:
            product -= 9
        total_sum += product

    check_digit = (10 - (total_sum % 10)) % 10
    return int(cedula[9]) == check_digit


def validate_passport(passport: str) -> bool:
    """Validates passport format (alphanumeric, 6-20 characters)."""
    if not isinstance(passport, str):
        return False
    return bool(PASSPORT_REGEX.match(passport.strip()))


def validate_name_format(name: str) -> bool:
    """Validates that name/surname contains only allowed characters and max 50 chars."""
    if not isinstance(name, str):
        return False
    trimmed = name.strip()
    if not trimmed or len(trimmed) > 50:
        return False
    return bool(NAME_REGEX.match(trimmed))


def validate_email_format(email: str) -> bool:
    """Validates email format with @ and valid domain."""
    if not isinstance(email, str):
        return False
    trimmed = email.strip()
    if not trimmed:
        return False
    # Check general structure and top-level domain
    if not EMAIL_REGEX.match(trimmed):
        return False
    parts = trimmed.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    if "." not in domain or domain.endswith(".") or domain.startswith("."):
        return False
    tld = domain.split(".")[-1]
    if len(tld) < 2:
        return False
    return True


def validate_password_format(password: str) -> bool:
    """
    Validates password has at least 8 chars, 1 uppercase, 1 lowercase, 1 digit.
    Special characters are optional.
    """
    if not isinstance(password, str) or len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


def normalize_email(email: str) -> str:
    """Normalizes email by trimming whitespace and converting to lowercase."""
    if not email:
        return ""
    return email.strip().lower()
