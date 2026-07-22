"""
Integration tests: /api/v1/incomes/*

Cubre el Módulo 3 — Finanzas Personales: CRUD de ingresos (FR-019).
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


class TestListIncomes:
    async def test_empty_list_when_no_incomes(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/incomes", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/incomes")
        assert response.status_code == 401


class TestCreateIncome:
    async def test_create_income_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 3500000,
                "description": "Salario mensual",
                "income_date": "2026-07-01",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 3500000
        assert data["description"] == "Salario mensual"
        assert data["income_date"] == "2026-07-01"

    async def test_create_income_with_category(self, client):
        token = await register_and_login(client, "mateo@test.com")
        # Create category
        cat_resp = await client.post(
            "/api/v1/categories",
            headers=auth_headers(token),
            json={"name": "Salario"},
        )
        category_id = cat_resp.json()["id"]

        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "category_id": category_id,
                "amount": 3500000,
                "description": "Salario mensual",
                "income_date": "2026-07-01",
            },
        )
        assert response.status_code == 201
        assert response.json()["category_id"] == category_id

    async def test_create_income_with_notes(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 500000,
                "description": "Freelance",
                "income_date": "2026-07-15",
                "notes": "Proyecto de consultoría",
            },
        )
        assert response.status_code == 201
        assert response.json()["notes"] == "Proyecto de consultoría"

    async def test_zero_amount_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 0,
                "description": "Test",
                "income_date": "2026-07-01",
            },
        )
        assert response.status_code == 422

    async def test_negative_amount_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": -100000,
                "description": "Test",
                "income_date": "2026-07-01",
            },
        )
        assert response.status_code == 422

    async def test_empty_description_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 100000,
                "description": "",
                "income_date": "2026-07-01",
            },
        )
        assert response.status_code == 422

    async def test_requires_authentication(self, client):
        response = await client.post(
            "/api/v1/incomes",
            json={"amount": 100000, "description": "Test", "income_date": "2026-07-01"},
        )
        assert response.status_code == 401


class TestUpdateIncome:
    async def test_update_amount(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 3000000,
                "description": "Salario",
                "income_date": "2026-07-01",
            },
        )
        income_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/incomes/{income_id}",
            headers=auth_headers(token),
            json={"amount": 3500000},
        )
        assert response.status_code == 200
        assert float(response.json()["amount"]) == 3500000

    async def test_update_description(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 100000,
                "description": "Freelance",
                "income_date": "2026-07-10",
            },
        )
        income_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/incomes/{income_id}",
            headers=auth_headers(token),
            json={"description": "Proyecto freelance web"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Proyecto freelance web"

    async def test_update_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/incomes/{fake_id}",
            headers=auth_headers(token),
            json={"amount": 100000},
        )
        assert response.status_code == 404

    async def test_cannot_access_other_users_income(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        create_resp = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(mateo_token),
            json={
                "amount": 3000000,
                "description": "Privado",
                "income_date": "2026-07-01",
            },
        )
        income_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/incomes/{income_id}",
            headers=auth_headers(salome_token),
            json={"amount": 999999},
        )
        assert response.status_code == 404


class TestDeleteIncome:
    async def test_delete_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 200000,
                "description": "Para borrar",
                "income_date": "2026-07-10",
            },
        )
        income_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/incomes/{income_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        # Verify it's gone from list
        list_resp = await client.get("/api/v1/incomes", headers=auth_headers(token))
        assert list_resp.json()["pagination"]["total"] == 0

    async def test_delete_nonexistent_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/v1/incomes/{fake_id}", headers=auth_headers(token)
        )
        assert response.status_code == 404
