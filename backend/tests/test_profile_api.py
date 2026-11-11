import pytest

from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository

PROFILE_URL = "/api/v1/perfil"


def make_user(db) -> User:
    user = User(
        document_type=DocumentType.CEDULA,
        document_number="1710034065",
        first_name="Ana",
        last_name="Gomez",
        email="ana@example.com",
        hashed_password=hash_password("OldPass123"),
        is_active=True,
    )
    user.roles = [UserRole.PASAJERO]
    return UserRepository(db).create(user)


def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {create_access_token(subject=user.id)}"}


def valid_payload(**overrides) -> dict:
    payload = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "phone": "0991234567",
        "address": "Calle Falsa 123",
        "birth_date": "1990-05-20",
    }
    payload.update(overrides)
    return payload


def test_profile_requires_authentication(client):
    assert client.get(PROFILE_URL).status_code == 401
    assert client.put(PROFILE_URL, json=valid_payload()).status_code == 401


def test_get_profile_returns_own_data(client, db_session):
    user = make_user(db_session)

    res = client.get(PROFILE_URL, headers=auth_headers(user))

    assert res.status_code == 200
    assert res.json()["email"] == "ana@example.com"
    assert "hashed_password" not in res.json()


def test_cp37_update_profile_with_valid_data(client, db_session):
    user = make_user(db_session)

    res = client.put(PROFILE_URL, json=valid_payload(first_name="Anita"), headers=auth_headers(user))

    assert res.status_code == 200
    body = res.json()
    assert body["message"] == "Perfil actualizado exitosamente"
    assert body["user"]["first_name"] == "Anita"
    assert body["access_token"] is None


@pytest.mark.parametrize(
    "overrides,expected_detail",
    [
        ({"phone": "123"}, "El número de celular debe tener exactamente 10 dígitos"),
        ({"phone": "09912a4567"}, "El celular solo debe contener números"),
        ({"address": "a" * 151}, "La dirección no puede exceder los 150 caracteres"),
        ({"birth_date": "1899-12-31"}, "La fecha de nacimiento debe estar entre 1900 y la fecha actual"),
        ({"birth_date": "9999-01-01"}, "La fecha de nacimiento debe estar entre 1900 y la fecha actual"),
        ({"first_name": "   "}, "Los campos obligatorios no pueden quedar vacíos"),
        ({"last_name": ""}, "Los campos obligatorios no pueden quedar vacíos"),
        ({"first_name": "Ana1"}, "Los nombres/apellidos proporcionados contienen caracteres inválidos"),
    ],
)
def test_cp38_to_cp42_validation_errors(client, db_session, overrides, expected_detail):
    user = make_user(db_session)

    res = client.put(PROFILE_URL, json=valid_payload(**overrides), headers=auth_headers(user))

    assert res.status_code == 422
    assert res.json()["detail"] == expected_detail


def test_password_change_returns_new_token_that_keeps_session_alive(client, db_session):
    user = make_user(db_session)
    payload = valid_payload(
        current_password="OldPass123", new_password="NewPass456", confirm_password="NewPass456"
    )

    res = client.put(PROFILE_URL, json=payload, headers=auth_headers(user))

    assert res.status_code == 200
    body = res.json()
    assert body["message"] == "Contraseña actualizada exitosamente"
    new_headers = {"Authorization": f"Bearer {body['access_token']}"}
    assert client.get(PROFILE_URL, headers=new_headers).status_code == 200
    db_session.refresh(user)
    assert verify_password("NewPass456", user.hashed_password)


def test_wrong_current_password_returns_400_not_401(client, db_session):
    user = make_user(db_session)
    payload = valid_payload(
        current_password="Wrong12345", new_password="NewPass456", confirm_password="NewPass456"
    )

    res = client.put(PROFILE_URL, json=payload, headers=auth_headers(user))

    # 401 would make the client close the session; this is a validation error
    assert res.status_code == 400
    assert res.json()["detail"] == "La contraseña actual es incorrecta"


def test_new_password_without_current_is_rejected(client, db_session):
    user = make_user(db_session)

    res = client.put(
        PROFILE_URL,
        json=valid_payload(new_password="NewPass456", confirm_password="NewPass456"),
        headers=auth_headers(user),
    )

    assert res.status_code == 422
    assert res.json()["detail"] == "Debe ingresar su contraseña actual para cambiarla"


def test_new_password_equal_to_current_is_rejected(client, db_session):
    user = make_user(db_session)
    payload = valid_payload(
        current_password="OldPass123", new_password="OldPass123", confirm_password="OldPass123"
    )

    res = client.put(PROFILE_URL, json=payload, headers=auth_headers(user))

    assert res.status_code == 422
    assert res.json()["detail"] == "La nueva contraseña debe ser diferente de la actual"


def test_email_and_document_in_payload_are_ignored(client, db_session):
    user = make_user(db_session)
    payload = valid_payload(email="hacker@example.com", document_number="0000000000")

    res = client.put(PROFILE_URL, json=payload, headers=auth_headers(user))

    assert res.status_code == 200
    assert res.json()["user"]["email"] == "ana@example.com"
    assert res.json()["user"]["document_number"] == "1710034065"


def test_user_can_only_update_own_profile(client, db_session):
    first = make_user(db_session)
    other = User(
        document_type=DocumentType.CEDULA,
        document_number="0926691452",
        first_name="Otro",
        last_name="Usuario",
        email="otro@example.com",
        hashed_password=hash_password("Pass1234"),
        is_active=True,
    )
    other.roles = [UserRole.PASAJERO]
    other = UserRepository(db_session).create(other)

    client.put(PROFILE_URL, json=valid_payload(first_name="Cambiada"), headers=auth_headers(first))

    db_session.refresh(other)
    assert other.first_name == "Otro"

