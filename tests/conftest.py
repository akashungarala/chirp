from app import models
from app.database import Base, get_db, SQLALCHEMY_DATABASE_URL
from app.main import app
from app.oauth2 import create_access_token
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Dedicated test database URL to avoid polluting production/dev data
TEST_SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL}_test"

# SQLAlchemy engine and session factory for isolated test DB
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def test_posts_data():
    """Static post data used for seeding test database."""
    return [
        {"title": "1st title", "content": "1st content", "published": False},
        {"title": "2nd title", "content": "2nd content", "published": True},
        {"title": "3rd title", "content": "3rd content", "published": False},
        {"title": "4th title", "content": "4th content", "published": True},
    ]

@pytest.fixture()
def session():
    """
    Provides a fresh database session for each test.
    Drops and recreates all tables to ensure test isolation.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    """
    Returns a TestClient with DB dependency overridden to use the test session.
    Ensures API tests are run against the test database.
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_1(client):
    """Creates User 1 for authentication and authorization tests."""
    user_data = {"email": "test_user_1@gmail.com", "password": "password_1"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    new_user = res.json()
    new_user['password'] = user_data['password']  # Preserve raw password for login
    return new_user

@pytest.fixture
def test_user_2(client):
    """Creates User 2 for ownership and access-control test cases."""
    user_data = {"email": "test_user_2@gmail.com", "password": "password_2"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user_1):
    """Generate a valid JWT for User 1 to support authorized requests."""
    return create_access_token({"user_id": test_user_1['id']})

@pytest.fixture
def authorized_client(client, token):
    """Returns a TestClient pre-configured with Authorization header."""
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def test_post_ids(session, test_user_1, test_user_2, test_posts_data):
    """
    Seeds the database with posts for User 1 and User 2.
    Returns a list of post IDs for use in tests.
    """
    post_models = [
        models.Post(
            title=post["title"],
            content=post["content"],
            published=post["published"],
            owner_id=test_user_1["id"],
        )
        for post in test_posts_data[:3]
    ]
    # Add one post for User 2
    post_models.append(
        models.Post(
            title=test_posts_data[3]["title"],
            content=test_posts_data[3]["content"],
            published=test_posts_data[3]["published"],
            owner_id=test_user_2["id"],
        )
    )
    session.add_all(post_models)
    session.commit()
    return [post.id for post in post_models]