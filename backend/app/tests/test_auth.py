"""Tests for authentication API endpoints."""

import pytest


class TestRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "Secure@Pass1",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "user"

    def test_register_duplicate_email(self, client):
        """Test registration with existing email."""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "full_name": "User One",
            "password": "Secure@Pass1",
        }
        client.post("/api/v1/auth/register", json=user_data)

        user_data["username"] = "user2"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 409

    def test_register_weak_password(self, client):
        """Test registration with weak password is allowed."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "full_name": "Weak User",
                "password": "weak",
            },
        )
        assert response.status_code == 201

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "badmail",
                "full_name": "Bad Mail",
                "password": "Secure@Pass1",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Test user login endpoint."""

    def test_login_success(self, client):
        """Test successful login."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "full_name": "Login User",
                "password": "Secure@Pass1",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "Secure@Pass1",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client):
        """Test login with incorrect password."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "username": "wrongpass",
                "full_name": "Wrong Pass",
                "password": "Secure@Pass1",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword@1",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "ghost@example.com",
                "password": "Secure@Pass1",
            },
        )
        assert response.status_code == 401


class TestProfile:
    """Test user profile endpoints."""

    def test_get_profile(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        response = client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name", "phone": "1234567890"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_unauthorized_access(self, client):
        """Test accessing profile without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403
