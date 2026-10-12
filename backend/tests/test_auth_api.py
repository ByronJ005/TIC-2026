def test_register_and_assign_pasajero(client):
    """13.11: Registering a user successfully creates account with PASAJERO role."""
    payload = {
        "document_type": "CEDULA",
        "document_number": "1710034065",
        "first_name": "Andrés",
        "last_name": "Mendoza",
        "email": "andres.mendoza@example.com",
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "andres.mendoza@example.com"
    assert data["role"] == "PASAJERO"
    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_email_rejected(client):
    """13.9: Registering with an existing email returns 400."""
    payload1 = {
        "document_type": "CEDULA",
        "document_number": "1710034065",
        "first_name": "Pedro",
        "last_name": "Armijos",
        "email": "dup.email@example.com",
        "password": "Password123",
    }
    res1 = client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "document_type": "CEDULA",
        "document_number": "0926691452",
        "first_name": "Luis",
        "last_name": "Armijos",
        "email": "DUP.EMAIL@example.com",  # Normalized should match
        "password": "Password123",
    }
    res2 = client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == 400
    assert "correo electrónico ya se encuentra registrado" in res2.json()["detail"]


def test_duplicate_document_rejected(client):
    """13.10: Registering with an existing document number and type returns 400."""
    payload1 = {
        "document_type": "CEDULA",
        "document_number": "0102555547",
        "first_name": "Lucía",
        "last_name": "Gómez",
        "email": "lucia1@example.com",
        "password": "Password123",
    }
    res1 = client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "document_type": "CEDULA",
        "document_number": "0102555547",  # Same document
        "first_name": "Lucía",
        "last_name": "Gómez",
        "email": "lucia2@example.com",
        "password": "Password123",
    }
    res2 = client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == 400
    assert "número de documento ya se encuentra registrado" in res2.json()["detail"]


def test_login_returns_token_and_supports_normalization(client):
    """13.12 & CP-11: Login with correct credentials returns JWT; email normalized."""
    register_payload = {
        "document_type": "PASAPORTE",
        "document_number": "PASS987654",
        "first_name": "Jorge",
        "last_name": "Pérez",
        "email": "j.perez@email.com",
        "password": "Password123",
    }
    res_reg = client.post("/api/v1/auth/register", json=register_payload)
    assert res_reg.status_code == 201

    # Login with case variation and whitespace
    login_payload = {
        "email": "  J.Perez@Email.com  ",
        "password": "Password123",
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"].lower() == "bearer"


def test_login_wrong_password_returns_generic_error(client):
    """13.13: Login with invalid password returns generic 'Credenciales incorrectas'."""
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Credenciales incorrectas"


def test_protected_endpoint_without_token(client):
    """13.14: Accessing protected /me without Authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_logout_invalidates_token(client):
    """Full login -> access /me -> logout -> access /me returns 401."""
    register_payload = {
        "document_type": "PASAPORTE",
        "document_number": "EC11223344",
        "first_name": "Sofia",
        "last_name": "Castro",
        "email": "sofia.castro@example.com",
        "password": "Password123",
    }
    client.post("/api/v1/auth/register", json=register_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "sofia.castro@example.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # /me succeeds
    me_res = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "sofia.castro@example.com"

    # Logout
    logout_res = client.post("/api/v1/auth/logout", headers=auth_header)
    assert logout_res.status_code == 200

    # /me now fails with 401
    me_after_logout = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_after_logout.status_code == 401
