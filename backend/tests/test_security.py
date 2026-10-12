from datetime import datetime, timedelta, timezone
from src.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from src.models.user import DocumentType, User, UserRole
from src.repositories.token_repository import TokenRepository
from src.repositories.user_repository import UserRepository


def test_password_hashing():
    """13.2: Verify password hashing with bcrypt."""
    plain = "Password123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_jwt_token_creation():
    """13.3: Verify create_access_token includes subject, role, jti, exp."""
    user_id = 42
    role = "PASAJERO"
    token = create_access_token(subject=user_id, role=role)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "PASAJERO"
    assert "jti" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]


def test_jwt_token_expired():
    """13.4: Verify expired token is rejected by decode_access_token."""
    expired_delta = timedelta(minutes=-10)
    token = create_access_token(
        subject=1, role="PASAJERO", expires_delta=expired_delta
    )

    payload = decode_access_token(token)
    assert payload is None


def test_blacklist_blocks_token(client, db_session):
    """13.5: Verify that blacklisted token is rejected with 401."""
    # Create test user in db
    user_repo = UserRepository(db_session)
    user = User(
        document_type=DocumentType.CEDULA,
        document_number="1104609829",
        first_name="Carlos",
        last_name="Mora",
        email="carlos.mora@example.com",
        hashed_password=hash_password("Pass1234"),
        role=UserRole.PASAJERO,
        is_active=True,
    )
    user_repo.create(user)

    token_jti = "test-jti-uuid-12345"
    token = create_access_token(
        subject=user.id, role="PASAJERO", jti=token_jti
    )

    # Valid token works
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Add to blacklist
    token_repo = TokenRepository(db_session)
    token_repo.add_to_blacklist(
        jti=token_jti,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    # Now request is rejected
    response_blocked = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_blocked.status_code == 401
    assert "revocada" in response_blocked.json()["detail"].lower()
