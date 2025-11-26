from app import schemas
from fastapi import status

# POST /users
def test_create_user(client):
    """Successfully create a user and validate response schema."""
    payload = {"email": "test_user_123@gmail.com", "password": "password_123"}
    response = client.post("/users/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    user = schemas.UserOut(**response.json())
    assert user.email == payload["email"]
    assert isinstance(user.id, int) and user.id > 0
    assert user.created_at is not None

def test_create_user_duplicate_email(client):
    """Creating a user with an existing email should return 409."""
    payload = {"email": "duplicate_user@gmail.com", "password": "strongpass"}
    # First creation succeeds
    res1 = client.post("/users/", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED
    # Second creation fails
    res2 = client.post("/users/", json=payload)
    assert res2.status_code == status.HTTP_409_CONFLICT
    assert res2.json().get("detail") == "Email already registered"

def test_create_user_invalid_email(client):
    """Creating a user with invalid email format returns 422."""
    payload = {"email": "not-an-email", "password": "password_123"}
    response = client.post("/users/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_password(client):
    """Creating a user without a password returns 422."""
    payload = {"email": "valid@gmail.com"}
    response = client.post("/users/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY