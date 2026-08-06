"""
Integration tests: /api/v1/tags/*

Cubre el módulo de etiquetas de gastos (FR-026) y su integración
con los gastos personales (FR-020, FR-022).
"""
import uuid

VALID_PASSWORD = "SuperSegura123!"


async def register_and_login(client, email):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Usuario",
            "last_name": "Test",
            "email": email,
            "password": VALID_PASSWORD,
        },
    )
    verification_token = response.json().get("verification_token")
    if verification_token:
        await client.post(
            "/api/v1/auth/verify-email", json={"token": verification_token}
        )
    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestTagAuthentication:
    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/tags")
        assert response.status_code == 401

    async def test_create_requires_authentication(self, client):
        response = await client.post("/api/v1/tags", json={"name": "Vacaciones"})
        assert response.status_code == 401


class TestCreateTag:
    async def test_create_tag_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/tags",
            headers=auth_headers(token),
            json={"name": "Vacaciones", "color": "#FF5733"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Vacaciones"
        assert data["color"] == "#FF5733"

    async def test_create_tag_duplicate_name(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Trabajo"}
        )
        response = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Trabajo"}
        )
        assert response.status_code == 409

    async def test_create_tag_invalid_name(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": ""}
        )
        assert response.status_code == 422


class TestListTags:
    async def test_empty_list(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/tags", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_list_with_tags(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Vacaciones"}
        )
        await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Trabajo"}
        )
        response = await client.get("/api/v1/tags", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 2
        assert {tag["name"] for tag in data["data"]} == {"Vacaciones", "Trabajo"}

    async def test_tags_are_isolated_between_users(self, client):
        token_a = await register_and_login(client, "user_a@test.com")
        token_b = await register_and_login(client, "user_b@test.com")
        await client.post(
            "/api/v1/tags", headers=auth_headers(token_a), json={"name": "Privado"}
        )
        response = await client.get("/api/v1/tags", headers=auth_headers(token_b))
        assert response.json()["data"] == []


class TestUpdateTag:
    async def test_update_tag_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Viaje"}
        )
        tag_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/tags/{tag_id}",
            headers=auth_headers(token),
            json={"name": "Vacaciones", "color": "#00FF00"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Vacaciones"
        assert data["color"] == "#00FF00"

    async def test_update_tag_duplicate_name(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_a = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Casa"}
        )
        tag_b = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Trabajo"}
        )
        response = await client.put(
            f"/api/v1/tags/{tag_b.json()['id']}",
            headers=auth_headers(token),
            json={"name": "Casa"},
        )
        assert response.status_code == 409
        assert tag_a.status_code == 201

    async def test_update_nonexistent_tag(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.put(
            f"/api/v1/tags/{uuid.uuid4()}",
            headers=auth_headers(token),
            json={"name": "X"},
        )
        assert response.status_code == 404


class TestDeleteTag:
    async def test_delete_tag_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Urgente"}
        )
        tag_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/tags/{tag_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        list_resp = await client.get("/api/v1/tags", headers=auth_headers(token))
        assert list_resp.json()["data"] == []


class TestTagsOnExpenses:
    async def test_create_expense_with_tags(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Mercado"}
        )
        tag_id = tag_resp.json()["id"]

        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 250000,
                "description": "Mercado semanal",
                "expense_date": "2026-07-10",
                "tag_ids": [tag_id],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "Mercado"

    async def test_create_expense_with_nonexistent_tag(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 250000,
                "description": "Mercado",
                "expense_date": "2026-07-10",
                "tag_ids": [str(uuid.uuid4())],
            },
        )
        assert response.status_code == 422

    async def test_get_expense_includes_tags(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Casa"}
        )
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 1200000,
                "description": "Arriendo",
                "expense_date": "2026-07-01",
                "tag_ids": [tag_resp.json()["id"]],
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert len(response.json()["tags"]) == 1

    async def test_list_expenses_includes_tags(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Servicios"}
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 100000,
                "description": "Luz",
                "expense_date": "2026-07-05",
                "tag_ids": [tag_resp.json()["id"]],
            },
        )
        response = await client.get("/api/v1/expenses", headers=auth_headers(token))
        assert response.status_code == 200
        assert len(response.json()["data"][0]["tags"]) == 1

    async def test_update_expense_replaces_tags(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_a = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Oficina"}
        )
        tag_b = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Personal"}
        )
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 30000,
                "description": "Pasaje",
                "expense_date": "2026-07-02",
                "tag_ids": [tag_a.json()["id"]],
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers(token),
            json={"tag_ids": [tag_b.json()["id"]]},
        )
        assert response.status_code == 200
        assert [t["name"] for t in response.json()["tags"]] == ["Personal"]

    async def test_delete_tag_removes_from_expense(self, client):
        token = await register_and_login(client, "mateo@test.com")
        tag_resp = await client.post(
            "/api/v1/tags", headers=auth_headers(token), json={"name": "Temp"}
        )
        tag_id = tag_resp.json()["id"]
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 5000,
                "description": "Café",
                "expense_date": "2026-07-03",
                "tag_ids": [tag_id],
            },
        )
        expense_id = create_resp.json()["id"]

        await client.delete(f"/api/v1/tags/{tag_id}", headers=auth_headers(token))

        response = await client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(token)
        )
        assert response.json()["tags"] == []
