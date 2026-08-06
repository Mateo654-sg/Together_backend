"""
Integration tests: /api/v1/recurring/*

Cubre el módulo de Movimientos Recurrentes (FR-033): CRUD y procesamiento
automático de recurrencias vencidas.
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


class TestListRecurring:
    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/recurring")
        assert response.status_code == 401

    async def test_empty_list_when_no_recurring(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/recurring", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0


class TestCreateRecurring:
    async def test_create_recurring_expense_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Suscripción Netflix",
                "next_execution": "2026-08-10",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "expense"
        assert data["frequency"] == "monthly"
        assert float(data["amount"]) == 50000
        assert data["next_execution"] == "2026-08-10"
        assert data["active"] is True

    async def test_create_recurring_income_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "income",
                "frequency": "monthly",
                "amount": 3000000,
                "description": "Salario",
            },
        )
        assert response.status_code == 201
        assert response.json()["type"] == "income"

    async def test_create_recurring_invalid_frequency(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "hourly",
                "amount": 50000,
                "description": "Invalida",
            },
        )
        assert response.status_code == 422

    async def test_create_recurring_invalid_type(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "transfer",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Invalida",
            },
        )
        assert response.status_code == 422

    async def test_create_recurring_with_nonexistent_category(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "weekly",
                "amount": 20000,
                "description": "Mercado",
                "category_id": str(uuid.uuid4()),
            },
        )
        assert response.status_code == 422


class TestUpdateRecurring:
    async def test_update_recurring_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Netflix",
            },
        )
        recurring_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/recurring/{recurring_id}",
            headers=auth_headers(token),
            json={"amount": 60000, "active": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 60000
        assert data["active"] is False

    async def test_update_nonexistent_recurring(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.put(
            f"/api/v1/recurring/{uuid.uuid4()}",
            headers=auth_headers(token),
            json={"amount": 60000},
        )
        assert response.status_code == 404


class TestDeleteRecurring:
    async def test_delete_recurring_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "daily",
                "amount": 10000,
                "description": "Transporte",
            },
        )
        recurring_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/recurring/{recurring_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        list_resp = await client.get("/api/v1/recurring", headers=auth_headers(token))
        assert list_resp.json()["data"] == []


class TestProcessRecurring:
    async def test_process_due_materializes_expense(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Netflix",
                "next_execution": "2026-07-10",
            },
        )

        response = await client.post(
            "/api/v1/recurring/process",
            headers=auth_headers(token),
            params={"on_date": "2026-08-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["executed"] == 1
        assert data["details"][0]["type"] == "expense"
        assert data["details"][0]["executed_on"] == "2026-07-10"
        assert data["details"][0]["next_execution"] == "2026-08-10"

        expenses_resp = await client.get(
            "/api/v1/expenses", headers=auth_headers(token)
        )
        expenses = expenses_resp.json()["data"]
        assert len(expenses) == 1
        assert float(expenses[0]["amount"]) == 50000
        assert expenses[0]["description"] == "Netflix"

    async def test_process_due_materializes_income(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "income",
                "frequency": "monthly",
                "amount": 3000000,
                "description": "Salario",
                "next_execution": "2026-07-01",
            },
        )

        response = await client.post(
            "/api/v1/recurring/process",
            headers=auth_headers(token),
            params={"on_date": "2026-08-05"},
        )
        assert response.json()["executed"] == 1

        incomes_resp = await client.get(
            "/api/v1/incomes", headers=auth_headers(token)
        )
        incomes = incomes_resp.json()["data"]
        assert len(incomes) == 1
        assert float(incomes[0]["amount"]) == 3000000

    async def test_process_no_due_returns_zero(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Netflix",
                "next_execution": "2026-09-10",
            },
        )

        response = await client.post(
            "/api/v1/recurring/process",
            headers=auth_headers(token),
            params={"on_date": "2026-08-05"},
        )
        assert response.status_code == 200
        assert response.json()["executed"] == 0

    async def test_process_inactive_ignored(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/recurring",
            headers=auth_headers(token),
            json={
                "type": "expense",
                "frequency": "monthly",
                "amount": 50000,
                "description": "Netflix",
                "next_execution": "2026-07-10",
            },
        )
        recurring_id = create_resp.json()["id"]
        await client.put(
            f"/api/v1/recurring/{recurring_id}",
            headers=auth_headers(token),
            json={"active": False},
        )

        response = await client.post(
            "/api/v1/recurring/process",
            headers=auth_headers(token),
            params={"on_date": "2026-08-05"},
        )
        assert response.json()["executed"] == 0
