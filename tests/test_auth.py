"""
Tests for user registration and authentication.

Coverage:
  - Successful registration
  - Duplicate username/email rejection
  - Password validation
  - Successful login
  - Wrong password rejection
  - Logout clears cookie
  - Protected routes redirect to login when unauthenticated
"""
import pytest


class TestRegistration:

    def test_register_success(self, client):
        resp = client.post("/auth/register", data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        # Should redirect to login after success
        assert resp.status_code == 303
        assert "/auth/login" in resp.headers["location"]

    def test_register_duplicate_username(self, client):
        data = {
            "username": "bob",
            "email": "bob@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        client.post("/auth/register", data=data, follow_redirects=False)
        # Try again with same username, different email
        resp = client.post("/auth/register", data={
            **data,
            "email": "bob2@example.com",
        }, follow_redirects=False)
        assert resp.status_code == 422
        assert b"username is already taken" in resp.content.lower()

    def test_register_duplicate_email(self, client):
        data = {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        client.post("/auth/register", data=data, follow_redirects=False)
        resp = client.post("/auth/register", data={
            **data,
            "username": "charlie2",
        }, follow_redirects=False)
        assert resp.status_code == 422
        assert b"email already exists" in resp.content.lower()

    def test_register_passwords_mismatch(self, client):
        resp = client.post("/auth/register", data={
            "username": "dave",
            "email": "dave@example.com",
            "password": "password123",
            "confirm_password": "different123",
        }, follow_redirects=False)
        assert resp.status_code == 422
        assert b"do not match" in resp.content.lower()

    def test_register_password_too_short(self, client):
        resp = client.post("/auth/register", data={
            "username": "eve",
            "email": "eve@example.com",
            "password": "short",
            "confirm_password": "short",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_register_invalid_username_chars(self, client):
        resp = client.post("/auth/register", data={
            "username": "bad username!",
            "email": "bad@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_register_missing_password_fields_shows_form_error(self, client):
        resp = client.post("/auth/register", data={
            "username": "missingpw",
            "email": "missingpw@example.com",
        }, follow_redirects=False)
        assert resp.status_code == 422
        assert b"password is required" in resp.content.lower()
        assert b"confirm password is required" in resp.content.lower()

    def test_register_creates_default_settings(self, client, db):
        client.post("/auth/register", data={
            "username": "frank",
            "email": "frank@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        from app.models.user import User, UserSettings
        user = db.query(User).filter(User.username == "frank").first()
        assert user is not None
        settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        assert settings is not None
        assert settings.language == "en"
        assert settings.theme == "light"


class TestLogin:

    def test_login_success(self, client, registered_user):
        resp = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "access_token" in resp.cookies

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": "wrongpassword",
        }, follow_redirects=False)
        assert resp.status_code == 401
        assert "access_token" not in resp.cookies

    def test_login_with_symbol_heavy_password_does_not_crash(self, client, registered_user):
        resp = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": "🔥" * 30,
        }, follow_redirects=False)
        assert resp.status_code == 401
        assert b"invalid username or password" in resp.content.lower()

    def test_login_unknown_user(self, client):
        resp = client.post("/auth/login", data={
            "username": "nobody",
            "password": "password123",
        }, follow_redirects=False)
        assert resp.status_code == 401

    def test_register_rejects_overlong_special_character_password(self, client):
        resp = client.post("/auth/register", data={
            "username": "symboluser",
            "email": "symbol@example.com",
            "password": "🔥" * 30,
            "confirm_password": "🔥" * 30,
        }, follow_redirects=False)
        assert resp.status_code == 422
        assert b"password is too long" in resp.content.lower()

    def test_login_redirects_to_dashboard(self, client, registered_user):
        resp = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        }, follow_redirects=True)
        # After following redirect, should land on the dashboard
        assert resp.status_code == 200

    def test_logout_clears_cookie(self, logged_in_client):
        resp = logged_in_client.post("/auth/logout", follow_redirects=False)
        assert resp.status_code == 303
        # Cookie should be cleared (set to empty/expired)
        assert resp.cookies.get("access_token", "") == ""


class TestProtectedRoutes:

    def test_dashboard_requires_auth(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["location"]

    def test_clubs_requires_auth(self, client):
        resp = client.get("/clubs", follow_redirects=False)
        assert resp.status_code == 302

    def test_events_requires_auth(self, client):
        resp = client.get("/events", follow_redirects=False)
        assert resp.status_code == 302

    def test_settings_requires_auth(self, client):
        resp = client.get("/settings", follow_redirects=False)
        assert resp.status_code == 302

    def test_authenticated_can_access_dashboard(self, logged_in_client):
        resp = logged_in_client.get("/", follow_redirects=False)
        assert resp.status_code == 200
