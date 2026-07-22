"""
Integration tests: /api/v1/users/*
"""
VALID_PASSWORD = "SuperSegura123!"


async def register_and_login(client, email="mateo@test.com"):
    await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Mateo",
            "last_name": "Rico",
            "email": email,
            "password": VALID_PASSWORD,
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    return login_response.json()["access_token"]


class TestGetMe:
    async def test_get_me_with_valid_token(self, client):
        token = await register_and_login(client)
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "mateo@test.com"

    async def test_get_me_without_token_returns_401(self, client):
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_get_me_with_invalid_token_returns_401(self, client):
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_get_me_with_access_token_used_as_refresh_fails(self, client):
        """Un access token nunca debe funcionar como refresh token."""
        token = await register_and_login(client)
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": token}
        )
        assert response.status_code == 401


class TestUpdateMe:
    async def test_update_profile_success(self, client):
        token = await register_and_login(client)
        response = await client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+573001234567", "currency": "USD"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+573001234567"
        assert data["currency"] == "USD"

    async def test_update_profile_partial_does_not_erase_other_fields(self, client):
        token = await register_and_login(client)
        await client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+573001234567"},
        )
        response = await client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"currency": "EUR"},
        )
        data = response.json()
        assert data["phone"] == "+573001234567"
        assert data["currency"] == "EUR"


class TestDeleteMe:
    async def test_delete_account_requires_correct_password(self, client):
        token = await register_and_login(client)
        response = await client.request(
            "DELETE",
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            params={"password": "incorrecta"},
        )
        assert response.status_code == 401

    async def test_delete_account_success_then_login_fails(self, client):
        token = await register_and_login(client)
        response = await client.request(
            "DELETE",
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            params={"password": VALID_PASSWORD},
        )
        assert response.status_code == 204

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "mateo@test.com", "password": VALID_PASSWORD},
        )
        # Soft delete: el usuario ya no debe poder autenticarse.
        assert login_response.status_code == 401


class TestGetSettings:
    async def test_get_settings_returns_defaults(self, client):
        token = await register_and_login(client)
        response = await client.get(
            "/api/v1/users/settings",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"
        assert data["notifications_enabled"] is True
        assert data["ai_enabled"] is True

    async def test_get_settings_requires_authentication(self, client):
        response = await client.get("/api/v1/users/settings")
        assert response.status_code == 401


class TestUpdateSettings:
    async def test_update_theme(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.put(
            "/api/v1/users/settings",
            headers=headers,
            json={"theme": "light"},
        )
        assert response.status_code == 200
        assert response.json()["theme"] == "light"

    async def test_update_notifications(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.put(
            "/api/v1/users/settings",
            headers=headers,
            json={"notifications_enabled": False},
        )
        assert response.status_code == 200
        assert response.json()["notifications_enabled"] is False

    async def test_partial_update_preserves_other_fields(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        # First update
        await client.put(
            "/api/v1/users/settings",
            headers=headers,
            json={"theme": "light"},
        )
        # Second update - only change one field
        response = await client.put(
            "/api/v1/users/settings",
            headers=headers,
            json={"ai_enabled": False},
        )
        data = response.json()
        assert data["theme"] == "light"  # Preserved
        assert data["ai_enabled"] is False  # Changed

    async def test_update_settings_requires_authentication(self, client):
        response = await client.put(
            "/api/v1/users/settings", json={"theme": "light"}
        )
        assert response.status_code == 401


class TestUpdateAvatar:
    async def test_update_avatar_success(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/users/avatar",
            headers=headers,
            json={"avatar_url": "https://example.com/avatar.jpg"},
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.jpg"

    async def test_update_avatar_requires_authentication(self, client):
        response = await client.patch(
            "/api/v1/users/avatar",
            json={"avatar_url": "https://example.com/avatar.jpg"},
        )
        assert response.status_code == 401

    async def test_update_avatar_invalid_url_rejected(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/users/avatar",
            headers=headers,
            json={"avatar_url": ""},
        )
        assert response.status_code == 422


class TestGetStatistics:
    async def test_statistics_empty_when_no_data(self, client):
        token = await register_and_login(client)
        response = await client.get(
            "/api/v1/users/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == 0
        assert data["total_expenses"] == 0
        assert data["balance"] == 0

    async def test_statistics_with_income_and_expenses(self, client):
        token = await register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create income
        await client.post(
            "/api/v1/incomes",
            headers=headers,
            json={
                "amount": 3000000,
                "description": "Salario",
                "income_date": "2026-07-01",
            },
        )
        # Create expense
        await client.post(
            "/api/v1/expenses",
            headers=headers,
            json={
                "amount": 500000,
                "description": "Arriendo",
                "expense_date": "2026-07-05",
            },
        )

        response = await client.get(
            "/api/v1/users/statistics",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == 3000000
        assert data["total_expenses_count"] == 1
        assert data["total_incomes_count"] == 1

    async def test_statistics_requires_authentication(self, client):
        response = await client.get("/api/v1/users/statistics")
        assert response.status_code == 401
