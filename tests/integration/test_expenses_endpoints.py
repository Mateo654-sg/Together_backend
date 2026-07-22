"""
Integration tests: /api/v1/expenses/*

Cubre el Módulo 3 — Finanzas Personales: CRUD de gastos (FR-020 a FR-040).
"""
import uuid

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


async def create_category(client, token, name="Comida"):
    resp = await client.post(
        "/api/v1/categories",
        headers=auth_headers(token),
        json={"name": name},
    )
    return resp.json()["id"]


class TestListExpenses:
    async def test_empty_list_when_no_expenses(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/expenses", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/expenses")
        assert response.status_code == 401


class TestCreateExpense:
    async def test_create_expense_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        category_id = await create_category(client, token, "Comida")

        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "category_id": category_id,
                "amount": 45000.50,
                "description": "Almuerzo restaurante",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 45000.50
        assert data["description"] == "Almuerzo restaurante"
        assert data["expense_date"] == "2026-07-20"
        assert data["is_favorite"] is False

    async def test_create_expense_without_category(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 10000,
                "description": "Compra sin categoría",
                "expense_date": "2026-07-21",
            },
        )
        assert response.status_code == 201
        assert response.json()["category_id"] is None

    async def test_create_expense_with_optional_fields(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 25000,
                "description": "Taxi",
                "expense_date": "2026-07-20",
                "payment_method": "Nequi",
                "location": "Bogotá",
                "notes": "Viaje al trabajo",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["payment_method"] == "Nequi"
        assert data["location"] == "Bogotá"
        assert data["notes"] == "Viaje al trabajo"

    async def test_zero_amount_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 0,
                "description": "Test",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 422

    async def test_negative_amount_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": -5000,
                "description": "Test",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 422

    async def test_invalid_category_returns_422(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "category_id": fake_id,
                "amount": 10000,
                "description": "Test",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 222

    async def test_requires_authentication(self, client):
        response = await client.post(
            "/api/v1/expenses",
            json={"amount": 10000, "description": "Test", "expense_date": "2026-07-20"},
        )
        assert response.status_code == 401


class TestGetExpense:
    async def test_get_expense_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 30000,
                "description": "Cena",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Cena"

    async def test_get_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/v1/expenses/{fake_id}", headers=auth_headers(token)
        )
        assert response.status_code == 404

    async def test_cannot_access_other_users_expense(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 30000,
                "description": "Privado",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(salome_token)
        )
        assert response.status_code == 404


class TestUpdateExpense:
    async def test_update_amount_and_description(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 20000,
                "description": "Café",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers(token),
            json={"amount": 25000, "description": "Café y postre"},
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 25000
        assert data["description"] == "Café y postre"

    async def test_toggle_favorite(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 10000,
                "description": "Favorito",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers(token),
            json={"is_favorite": True},
        )
        assert response.status_code == 200
        assert response.json()["is_favorite"] is True

    async def test_update_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/expenses/{fake_id}",
            headers=auth_headers(token),
            json={"amount": 10000},
        )
        assert response.status_code == 404


class TestDeleteExpense:
    async def test_delete_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 15000,
                "description": "Para borrar",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        # Verify it's gone
        get_resp = await client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers(token)
        )
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/v1/expenses/{fake_id}", headers=auth_headers(token)
        )
        assert response.status_code == 404


class TestDuplicateExpense:
    async def test_duplicate_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 35000,
                "description": "Original",
                "expense_date": "2026-07-15",
            },
        )
        expense_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/expenses/duplicate?expense_id={expense_id}",
            headers=auth_headers(token),
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 35000
        assert data["description"] == "Original"
        assert data["expense_date"] != "2026-07-15"  # Should be today
        assert data["id"] != expense_id

    async def test_duplicate_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/api/v1/expenses/duplicate?expense_id={fake_id}",
            headers=auth_headers(token),
        )
        assert response.status_code == 404


class TestExpenseBalance:
    async def test_balance_zero_when_no_data(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/expenses/balance", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["balance"] == 0

    async def test_balance_positive_when_more_income(self, client):
        token = await register_and_login(client, "mateo@test.com")

        # Create income
        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 500000,
                "description": "Salario",
                "income_date": "2026-07-01",
            },
        )
        # Create expense
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 200000,
                "description": "Arriendo",
                "expense_date": "2026-07-01",
            },
        )

        response = await client.get(
            "/api/v1/expenses/balance", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert float(response.json()["balance"]) == 300000
