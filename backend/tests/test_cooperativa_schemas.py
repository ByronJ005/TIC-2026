import pytest
from pydantic import ValidationError
from src.schemas.cooperativa_schemas import (
    ERROR_MAX_ADMINS_EXCEEDED,
    CooperativaAdministradoresUpdate,
    CooperativaCreate,
    CooperativaUpdate,
)
from src.schemas.validators import (
    ERROR_ADDRESS_TOO_LONG,
    ERROR_COOP_NAME_EMPTY,
    ERROR_COOP_NAME_INVALID_CHARS,
    ERROR_INVALID_EMAIL,
    ERROR_PHONE_LENGTH,
    ERROR_RUC_INVALID_ALGORITHM,
    ERROR_RUC_LENGTH_OR_FORMAT,
)


def test_cooperativa_create_valid():
    data = {
        "name": "Cooperativa Loja",
        "ruc": "1104609829001",
        "address": "Av. Terminal Terrestre",
        "phone": "0987654321",
        "email": "INFO@COOPLOJA.EC",
        "logo_url": "https://example.com/logo.png",
    }
    coop = CooperativaCreate(**data)
    assert coop.name == "Cooperativa Loja"
    assert coop.ruc == "1104609829001"
    assert coop.email == "info@cooploja.ec"  # normalized


def test_cooperativa_create_invalid_ruc():
    # Empty
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="")
    assert "El RUC es obligatorio" in str(exc.value)

    # Length
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="123")
    assert ERROR_RUC_LENGTH_OR_FORMAT in str(exc.value)

    # Algorithm
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="1104609828001")
    assert ERROR_RUC_INVALID_ALGORITHM in str(exc.value)


def test_cooperativa_create_invalid_name():
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="", ruc="1104609829001")
    assert ERROR_COOP_NAME_EMPTY in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop @ Illegal", ruc="1104609829001")
    assert ERROR_COOP_NAME_INVALID_CHARS in str(exc.value)


def test_cooperativa_create_reused_field_validations():
    # Invalid phone
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="1104609829001", phone="12345")
    assert ERROR_PHONE_LENGTH in str(exc.value)

    # Invalid address
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="1104609829001", address="A" * 151)
    assert ERROR_ADDRESS_TOO_LONG in str(exc.value)

    # Invalid email
    with pytest.raises(ValidationError) as exc:
        CooperativaCreate(name="Coop Test", ruc="1104609829001", email="invalid-email")
    assert ERROR_INVALID_EMAIL in str(exc.value)


def test_cooperativa_update_name_not_empty():
    # Empty name on update
    with pytest.raises(ValidationError) as exc:
        CooperativaUpdate(name="")
    assert ERROR_COOP_NAME_EMPTY in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        CooperativaUpdate(name="   ")
    assert ERROR_COOP_NAME_EMPTY in str(exc.value)


def test_cooperativa_update_logo_url_allows_relative_path():
    update_data = CooperativaUpdate(logo_url="/static/logos/c94fafdedb8b440eb03f4db2d0715120.png")
    assert update_data.logo_url == "/static/logos/c94fafdedb8b440eb03f4db2d0715120.png"

    update_abs = CooperativaUpdate(logo_url="https://example.com/logo.png")
    assert update_abs.logo_url == "https://example.com/logo.png"


def test_cooperativa_update_ignores_ruc():
    # CooperativaUpdate does not accept or apply ruc
    update_data = CooperativaUpdate(name="Nuevo Nombre", address="Nueva Dir")
    assert not hasattr(update_data, "ruc") or update_data.model_dump().get("ruc") is None


def test_cooperativa_administradores_max_limit():
    valid = CooperativaAdministradoresUpdate(user_ids=[1, 2, 3])
    assert valid.user_ids == [1, 2, 3]

    # Exceeding 3
    with pytest.raises(ValidationError) as exc:
        CooperativaAdministradoresUpdate(user_ids=[1, 2, 3, 4])
    assert ERROR_MAX_ADMINS_EXCEEDED in str(exc.value)

