"""
Pytest configuration and shared fixtures.

Uses an in-memory SQLite database for tests so nothing touches the dev DB.
Each test function gets a fresh database via function-scoped fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite — fast and isolated, no files left behind
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create all tables, yield a session, drop all tables after the test."""
    # Import models so SQLAlchemy registers them
    from app.models import user, club, event  # noqa: F401

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    FastAPI TestClient with the test DB injected via dependency override.
    Automatically rolls back the session between tests.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle managed by the `db` fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register a standard test user and return their credentials."""
    resp = client.post("/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
    }, follow_redirects=False)
    assert resp.status_code == 303, f"Registration failed: {resp.text}"
    return {"username": "testuser", "password": "testpass123", "email": "test@example.com"}


@pytest.fixture
def logged_in_client(client, registered_user):
    """Client with a valid login cookie already set."""
    resp = client.post("/auth/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"],
    }, follow_redirects=False)
    assert resp.status_code == 303, f"Login failed: {resp.text}"
    return client
