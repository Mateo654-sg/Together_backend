"""
Integration tests: /api/v1/auth/*

Flujo completo Flutter -> FastAPI -> PostgreSQL, sin mocks
(Documento 13 — Testing Strategy).
"""
import pytest

VALID_PASSWORD = "SuperSegura123!"


async def register_user(client, email="mateo@test.com", password=VALID_PASSWORD):
    return await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Mateo",
            "last_name": "Rico",
            "email": email,
            "password": password,
        },
    )


class TestRegister:
    async def test_register_success(self, client):
        response = await register_user(client)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "mateo@test.com"
        assert data["is_verified"] is False
        assert "password" not in data
        assert "password_hash" not in data

    async def test_register_duplicate_email_returns_409(self, client):
        await register_user(client)
        response = await register_user(client)
        assert response.status_code == 409
        assert response.json()["success"] is False

    async def test_register_weak_password_returns_422(self, client):
        response = await register_user(client, password="123456")
        assert response.status_code == 422

    async def test_register_email_is_normalized_to_lowercase(self, client):
        response = await register_user(client, email="Mateo@TEST.com")
        assert response.status_code == 201
        assert response.json()["email"] == "mateo@test.com"


class TestLogin:
    async def test_login_success_returns_tokens(self, client):
        await register_user(client)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "mateo@test.com", "password": VALID_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client):
        await register_user(client)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "mateo@test.com", "password": "incorrecta"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user_returns_401(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "noexiste@test.com", "password": VALID_PASSWORD},
        )
        assert response.status_code == 401

    async def test_account_locks_after_max_failed_attempts(self, client):
        await register_user(client)
        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                json={"email": "mateo@test.com", "password": "incorrecta"},
            )
        # El sexto intento, incluso con la contraseña correcta, debe fallar por bloqueo.
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "mateo@test.com", "password": VALID_PASSWORD},
        )
        assert response.status_code == 429


class TestRefreshAndLogout:
    async def _get_tokens(self, client):
        await register_user(client)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "mateo@test.com", "password": VALID_PASSWORD},
        )
        return login_response.json()

    async def test_refresh_returns_new_tokens(self, client):
        tokens = await self._get_tokens(client)
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 200
        new_tokens = response.json()
        assert new_tokens["refresh_token"] != tokens["refresh_token"]
        assert new_tokens["access_token"] != tokens["access_token"]

    async def test_reusing_rotated_refresh_token_fails(self, client):
        tokens = await self._get_tokens(client)
        await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        # Reutilizar el token ya rotado debe fallar.
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 401

    async def test_invalid_refresh_token_returns_401(self, client):
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "token.invalido.aqui"}
        )
        assert response.status_code == 401

    async def test_logout_revokes_session(self, client):
        tokens = await self._get_tokens(client)
        logout_response = await client.post(
            "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
        )
        assert logout_response.status_code == 204

        # El refresh token ya no debe poder usarse tras logout.
        refresh_response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 401

    async def test_logout_is_idempotent(self, client):
        """Logout con un token inválido nunca debe fallar (Documento 05 — UX)."""
        response = await client.post(
            "/api/v1/auth/logout", json={"refresh_token": "token.invalido"}
        )
        assert response.status_code == 204
