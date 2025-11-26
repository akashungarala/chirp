from app import schemas
from app.config import settings
from fastapi import status
import jwt
import pytest

def test_login_user(test_user_1, client):
    """
    Validate successful login:
    - Returns 200 OK
    - JWT contains correct user_id
    - Token type is 'bearer'
    - JWT header uses the configured algorithm
    """
    response = client.post(
        "/login",
        data={"username": test_user_1['email'], "password": test_user_1['password']},
    )
    assert response.status_code == status.HTTP_200_OK
    # Validate token response structure
    token_data = schemas.Token(**response.json())
    assert token_data.token_type == "bearer"
    # Decode and verify JWT payload
    payload = jwt.decode(token_data.access_token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload.get("user_id") == test_user_1["id"]
    # Verify JWT header algorithm
    header = jwt.get_unverified_header(token_data.access_token)
    assert header.get("alg") == settings.algorithm

@pytest.mark.parametrize(
    "email, password",
    [
        ("incorrect_email@gmail.com", "password_1"),
        ("test_user_1@gmail.com", "incorrect_password"),
        ("incorrect_email@gmail.com", "incorrect_password"),
        (None, "password_1"),
        ("test_user_1@gmail.com", None),
    ],
)
def test_incorrect_login(test_user_1, client, email, password):
    """
    Ensure invalid login attempts are rejected:
    - Wrong email or password
    - Missing email or password
    """
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body.get("detail") == "Invalid Credentials"