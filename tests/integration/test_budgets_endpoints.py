"""
Integration tests: /api/v1/budgets/*

Cubre el Módulo 6 — Presupuestos (FR-073 a FR-078).
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


class TestListBudgetsEmpty:
    async def test_list_budgets_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/budgets", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0


class TestCreateBudget:
    async def test_create_monthly_budget(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={
                "amount": 500000,
                "month": 7,
                "year": 2026,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 500000
        assert data["month"] == 7
        assert data["year"] == 2026

    async def test_create_category_budget(self, client):
        token = await register_and_login(client, "mateo@test.com")

        cat_resp = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": "Alimentación", "type": "expense"},
        )
        category_id = cat_resp.json()["id"]

        response = await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={
                "category_id": category_id,
                "amount": 300000,
                "month": 7,
                "year": 2026,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["category_id"] == category_id

    async def test_create_duplicate_budget_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")

        cat_resp = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": "Transporte", "type": "expense"},
        )
        category_id = cat_resp.json()["id"]

        await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={
                "category_id": category_id,
                "amount": 200000,
                "month": 7,
                "year": 2026,
            },
        )

        response = await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={
                "category_id": category_id,
                "amount": 150000,
                "month": 7,
                "year": 2026,
            },
        )
        assert response.status_code == 409


class TestUpdateBudget:
    async def test_update_budget_success(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={"amount": 400000, "month": 7, "year": 2026},
        )
        budget_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/budgets/{budget_id}",
            headers=auth_headers(token),
            json={"amount": 500000},
        )
        assert response.status_code == 200
        assert float(response.json()["amount"]) == 500000

    async def test_update_budget_not_found_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")

        import uuid

        response = await client.put(
            f"/api/v1/budgets/{uuid.uuid4()}",
            headers=auth_headers(token),
            json={"amount": 100000},
        )
        assert response.status_code == 404


class TestDeleteBudget:
    async def test_delete_budget_success(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/budgets",
            headers=auth_headers(token),
            json={"amount": 300000, "month": 7, "year": 2026},
        )
        budget_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/budgets/{budget_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        list_resp = await client.get(
            "/api/v1/budgets", headers=auth_headers(token)
        )
        assert list_resp.json()["pagination"]["total"] == 0


class TestBudgetAlerts:
    async def test_alerts_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/budgets/alerts", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["data"] == []
