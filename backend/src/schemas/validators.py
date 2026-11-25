import re
from datetime import date
from typing import Any, Optional

MIN_BIRTH_YEAR = 1900
PHONE_LENGTH = 10
ADDRESS_MAX_LENGTH = 150

# Error message constants matching specification exactly
ERROR_INVALID_DOCUMENT = "El número de documento proporcionado es inválido"
ERROR_INVALID_NAME = "Los nombres/apellidos proporcionados contienen caracteres inválidos"
ERROR_INVALID_EMAIL = "Correo electrónico inválido"
ERROR_INVALID_PASSWORD = (
    "La contraseña debe contener al menos 8 caracteres e incluir una mayúscula, "
    "minúscula, número y carácter especial opcional"
)
ERROR_REQUIRED_FIELD = "Este campo es requerido"
ERROR_EMAIL_REQUIRED = "Se requiere el correo electrónico"
ERROR_MANDATORY_FIELDS_EMPTY = "Los campos obligatorios no pueden quedar vacíos"
ERROR_PHONE_LENGTH = "El número de celular debe tener exactamente 10 dígitos"
ERROR_PHONE_NOT_NUMERIC = "El celular solo debe contener números"
ERROR_ADDRESS_TOO_LONG = "La dirección no puede exceder los 150 caracteres"
ERROR_INVALID_BIRTH_DATE = "La fecha de nacimiento debe estar entre 1900 y la fecha actual"
ERROR_CURRENT_PASSWORD_REQUIRED = "Debe ingresar su contraseña actual para cambiarla"
ERROR_CURRENT_PASSWORD_WRONG = "La contraseña actual es incorrecta"
ERROR_NEW_PASSWORD_SAME_AS_CURRENT = "La nueva contraseña debe ser diferente de la actual"
ERROR_PASSWORD_CONFIRMATION_MISMATCH = "La confirmación no coincide con la nueva contraseña"

# Submodule 04 - Cooperativas
ERROR_RUC_REQUIRED = "El RUC es obligatorio"
ERROR_RUC_LENGTH_OR_FORMAT = "El RUC debe tener exactamente 13 dígitos numéricos"
ERROR_RUC_INVALID_ALGORITHM = "El RUC ingresado no es válido según el estándar ecuatoriano"
ERROR_COOP_NAME_EMPTY = "El nombre de la cooperativa no puede quedar vacío"
ERROR_COOP_NAME_INVALID_CHARS = (
    "El nombre solo puede contener letras, números, espacios, guiones medios y apóstrofes"
)
ERROR_COOP_NAME_TOO_LONG = "El nombre de la cooperativa no puede exceder los 100 caracteres"

NAME_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]{1,50}$")
COOPERATIVA_NAME_MAX_LENGTH = 100
COOPERATIVA_NAME_REGEX = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\s'-]+$")
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)
PHONE_DIGITS_REGEX = re.compile(r"[0-9]+")
PASSPORT_REGEX = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]{6,20}$")


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
    """Validates passport format (strictly alphanumeric with letters and digits, 6-20 characters)."""
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


def is_blank(value: Optional[str]) -> bool:
    """True when the value is missing, empty or only whitespace."""
    return value is None or not value.strip()


def get_phone_error(phone: Optional[str]) -> Optional[str]:
    """
    Returns the error message for an invalid phone, or None when valid.
    Blank values are valid because the phone is optional.
    Non-numeric characters (including spaces) take precedence over length errors.
    """
    if is_blank(phone):
        return None
    # fullmatch: a "$" anchor would accept a trailing newline
    if not PHONE_DIGITS_REGEX.fullmatch(phone):
        return ERROR_PHONE_NOT_NUMERIC
    if len(phone) != PHONE_LENGTH:
        return ERROR_PHONE_LENGTH
    return None


def validate_phone_format(phone: Optional[str]) -> bool:
    """Validates that an optional phone has exactly 10 ASCII digits."""
    return get_phone_error(phone) is None


def validate_address_length(address: Optional[str]) -> bool:
    """Validates an optional address has at most 150 characters (trimmed)."""
    if is_blank(address):
        return True
    return len(address.strip()) <= ADDRESS_MAX_LENGTH


def validate_birth_date(value: Optional[date], today: Optional[date] = None) -> bool:
    """
    Validates an optional birth date is between 1900-01-01 and today (inclusive).
    The upper bound is computed at validation time, never hardcoded to a year.
    """
    if value is None:
        return True
    reference_day = today or date.today()
    return date(MIN_BIRTH_YEAR, 1, 1) <= value <= reference_day


def normalize_email(email: str) -> str:
    """Normalizes email by trimming whitespace and converting to lowercase."""
    if not email:
        return ""
    return email.strip().lower()


def get_ruc_error(ruc: Optional[str]) -> Optional[str]:
    """
    Validates an Ecuadorian RUC and returns the appropriate error message,
    or None when valid.
    """
    if is_blank(ruc):
        return ERROR_RUC_REQUIRED

    cleaned = ruc.strip()
    if not cleaned.isdigit() or len(cleaned) != 13:
        return ERROR_RUC_LENGTH_OR_FORMAT

    province = int(cleaned[:2])
    if province < 1 or (province > 24 and province != 30):
        return ERROR_RUC_INVALID_ALGORITHM

    third_digit = int(cleaned[2])

    # Case 1: Persona Natural (0 <= third_digit <= 5)
    if third_digit < 6:
        # First 10 digits must be valid cédula
        if not validate_ecuadorian_cedula(cleaned[:10]):
            return ERROR_RUC_INVALID_ALGORITHM
        # Establishment code must be >= 001
        establishment = int(cleaned[10:])
        if establishment < 1:
            return ERROR_RUC_INVALID_ALGORITHM
        return None

    # Case 2: Sociedades Públicas (third_digit == 6)
    elif third_digit == 6:
        coefficients = [3, 2, 7, 6, 5, 4, 3, 2]
        total_sum = sum(int(d) * c for d, c in zip(cleaned[:8], coefficients))
        remainder = total_sum % 11
        verifier = 0 if remainder == 0 else (11 - remainder)
        if int(cleaned[8]) != verifier:
            return ERROR_RUC_INVALID_ALGORITHM
        # Establishment code (last 4 digits) must be >= 0001
        establishment = int(cleaned[9:])
        if establishment < 1:
            return ERROR_RUC_INVALID_ALGORITHM
        return None

    # Case 3: Sociedades Privadas / Jurídicas (third_digit == 9)
    elif third_digit == 9:
        coefficients = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        total_sum = sum(int(d) * c for d, c in zip(cleaned[:9], coefficients))
        remainder = total_sum % 11
        verifier = 0 if remainder == 0 else (11 - remainder)
        if int(cleaned[9]) != verifier:
            return ERROR_RUC_INVALID_ALGORITHM
        # Establishment code (last 3 digits) must be >= 001
        establishment = int(cleaned[10:])
        if establishment < 1:
            return ERROR_RUC_INVALID_ALGORITHM
        return None

    else:
        # third_digit in (7, 8) is invalid
        return ERROR_RUC_INVALID_ALGORITHM


def validate_ruc(ruc: str) -> bool:
    """Returns True if the RUC is valid according to Ecuadorian rules."""
    return get_ruc_error(ruc) is None


def get_cooperativa_name_error(name: Optional[str]) -> Optional[str]:
    """
    Validates a cooperative name according to format and length constraints.
    Returns the error message or None if valid.
    """
    if is_blank(name):
        return ERROR_COOP_NAME_EMPTY
    trimmed = name.strip()
    if len(trimmed) > COOPERATIVA_NAME_MAX_LENGTH:
        return ERROR_COOP_NAME_TOO_LONG
    if not COOPERATIVA_NAME_REGEX.fullmatch(trimmed):
        return ERROR_COOP_NAME_INVALID_CHARS
    return None


def validate_cooperativa_name(name: str) -> bool:
    """Returns True if the cooperative name complies with length and character rules."""
    return get_cooperativa_name_error(name) is None


# Submodule 05 - Rutas, Localidades y Notificaciones
ERROR_LOCALITY_NAME_EMPTY = "El nombre de la localidad no puede quedar vacío"
ERROR_LOCALITY_NAME_TOO_LONG = "El nombre de la localidad no puede exceder los 100 caracteres"
ERROR_ROUTE_NAME_SUFFIX_TOO_LONG = "El texto adicional del nombre no puede exceder los 30 caracteres"
ERROR_ROUTE_DESCRIPTION_TOO_LONG = "La descripción no puede exceder los 100 caracteres"
ERROR_ROUTE_DISTANCE_INVALID = "La distancia debe ser un número mayor a 0"
ERROR_ROUTE_TIME_INVALID = (
    "Ingrese un tiempo estimado válido. El tiempo total debe ser mayor a cero y los minutos deben estar entre 0 y 59"
)
ERROR_ROUTE_ORIGIN_DESTINATION_SAME = "El origen y el destino deben ser diferentes"
ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION = "Una parada intermedia no puede ser igual al origen o al destino"
ERROR_ROUTE_STOP_DUPLICATED = "La localidad ya fue agregada como parada de esta ruta"
ERROR_ROUTE_STOPS_EMPTY = "Debe agregar al menos una parada intermedia o marcar la opción 'Solo las de origen y destino'"
ERROR_ROUTE_DUPLICATED = "Ya existe una ruta general con el mismo origen, destino y distancia"
ERROR_COOP_ROUTE_DUPLICATED = "Ya existe una ruta de su cooperativa con el mismo origen, destino y distancia"
ERROR_ROUTE_GENERAL_INACTIVE = "La ruta general se encuentra desactivada por la administración del terminal"
ERROR_ROUTE_ALREADY_ADOPTED = "La ruta general ya está asociada a la cooperativa"
ERROR_ROUTE_ORIGIN_DEST_MUTATION_RESTRICTED = (
    "El origen y el destino no pueden modificarse porque la ruta tiene asociaciones"
)
ERROR_COOP_DEACTIVATED_ROUTES = "Por el momento, su cooperativa se encuentra desactivada"

LOCALITY_NAME_MAX_LENGTH = 100
ROUTE_NAME_SUFFIX_MAX_LENGTH = 30
ROUTE_DESCRIPTION_MAX_LENGTH = 100


def normalize_locality_name(name: Optional[str]) -> str:
    """Trims and collapses internal whitespaces of a locality name."""
    if not name:
        return ""
    return " ".join(name.strip().split())


def get_locality_name_error(name: Optional[str]) -> Optional[str]:
    """Validates locality name. Must not be empty or exceed max length."""
    normalized = normalize_locality_name(name)
    if not normalized:
        return ERROR_LOCALITY_NAME_EMPTY
    if len(normalized) > LOCALITY_NAME_MAX_LENGTH:
        return ERROR_LOCALITY_NAME_TOO_LONG
    return None


def get_route_name_suffix_error(suffix: Optional[str]) -> Optional[str]:
    """Validates optional route name suffix."""
    if suffix is None:
        return None
    trimmed = suffix.strip()
    if len(trimmed) > ROUTE_NAME_SUFFIX_MAX_LENGTH:
        return ERROR_ROUTE_NAME_SUFFIX_TOO_LONG
    return None


def get_route_description_error(desc: Optional[str]) -> Optional[str]:
    """Validates optional route description."""
    if desc is None:
        return None
    trimmed = desc.strip()
    if len(trimmed) > ROUTE_DESCRIPTION_MAX_LENGTH:
        return ERROR_ROUTE_DESCRIPTION_TOO_LONG
    return None


def get_route_distance_error(distance: Any) -> Optional[str]:
    """Validates distance. Must be numeric and strictly > 0."""
    if distance is None:
        return ERROR_ROUTE_DISTANCE_INVALID
    try:
        val = float(distance)
        if val <= 0:
            return ERROR_ROUTE_DISTANCE_INVALID
    except (TypeError, ValueError):
        return ERROR_ROUTE_DISTANCE_INVALID
    return None


def get_route_time_error(estimated_minutes: Any) -> Optional[str]:
    """
    Validates estimated time in minutes.
    Must be strictly > 0 and <= 5999 minutes (up to 99h 59m).
    """
    if estimated_minutes is None:
        return ERROR_ROUTE_TIME_INVALID
    try:
        val = int(estimated_minutes)
        if val <= 0 or val > 5999:
            return ERROR_ROUTE_TIME_INVALID
    except (TypeError, ValueError):
        return ERROR_ROUTE_TIME_INVALID
    return None

