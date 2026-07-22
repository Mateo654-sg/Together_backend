"""
Integration tests: /api/v1/categories/*

Cubre el Módulo 3 — Finanzas Personales: CRUD de categorías (FR-024).
"""
VALID_PASSWORD = "SuperSegura123!"


async def register_and_login(client, email):
    await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Usuario",
            "last_name": "Test",
            "email": email,
            "password": VALID_PASSWORD,
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestListCategories:
    async def test_empty_list_when_no_categories(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/categories", headers=auth_headers(token))
        assert response.status_code == 200
        assert response.json() == []

    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/categories")
        assert response.status_code == 401


class TestCreateCategory:
    async def test_create_category_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": "Comida", "icon": "utensils", "color": "#FF5733"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Comida"
        assert data["icon"] == "utensils"
        assert data["color"] == "#FF5733"
        assert "id" in data

    async def test_create_category_minimal(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": "Transporte"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Transporte"
        assert data["icon"] is None
        assert data["color"] is None

    async def test_cannot_create_duplicate_name(self, client):
        token = await register_and_login(client, "mateo@test.com")
        headers = auth_headers(token)
        await client.post(
            "/api/v1/categories",
            headers=headers,
            json={"name": "Comida"},
        )
        response = await client.post(
            "/api/v1/categories",
            headers=headers,
            json={"name": "Comida"},
        )
        assert response.status_code == 409

    async def test_empty_name_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_requires_authentication(self, client):
        response = await client.post(
            "/api/v1/categories", json={"name": "Test"}
        )
        assert response.status_code == 401


class TestUpdateCategory:
    async def test_update_name_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        headers = auth_headers(token)
        create_resp = await client.post(
            "/api/v1/categories",
            headers=headers,
            json={"name": "Comida"},
        )
        cat_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/categories/{cat_id}",
            headers=headers,
            json={"name": "Restaurantes"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Restaurantes"

    async def test_update_color_and_icon(self, client):
        token = await register_and_login(client, "mateo@test.com")
        headers = auth_headers(token)
        create_resp = await client.post(
            "/api/v1/categories",
            headers=headers,
            json={"name": "Salud"},
        )
        cat_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/categories/{cat_id}",
            headers=headers,
            json={"icon": "heart", "color": "#E74C3C"},
        )
        assert response.status_code == 200
        assert response.json()["icon"] == "heart"
        assert response.json()["color"] == "#E74C3C"

    async def test_update_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/categories/{fake_id}",
            headers=auth_headers(token),
            json={"name": "Test"},
        )
        assert response.status_code == 404

    async def test_cannot_rename_to_existing_name(self, client):
        token = await register_and_login(client, "mateo@test.com")
        headers = auth_headers(token)
        await client.post(
            "/api/v1/categories", headers=headers, json={"name": "Comida"}
        )
        create_resp = await client.post(
            "/api/v1/categories", headers=headers, json={"name": "Salud"}
        )
        cat_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/categories/{cat_id}",
            headers=headers,
            json={"name": "Comida"},
        )
        assert response.status_code == 409


class TestDeleteCategory:
    async def test_delete_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        headers = auth_headers(token)
        create_resp = await client.post(
            "/api/v1/categories", headers=headers, json={"name": "Comida"}
        )
        cat_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/categories/{cat_id}", headers=headers
        )
        assert response.status_code == 204

        # Verify it's gone from list
        list_resp = await client.get("/api/v1/categories", headers=headers)
        assert len(list_resp.json()) == 0

    async def test_delete_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/v1/categories/{fake_id}", headers=auth_headers(token)
        )
        assert response.status_code == 404
