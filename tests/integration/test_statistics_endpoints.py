"""
Integration tests: /api/v1/statistics/* (year, category, couple).

Cubre las estadísticas anuales (FR-090), por categoría (FR-091)
y de pareja (FR-093).
"""

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


async def create_category(client, token, name, type="expense"):
    response = await client.post(
        "/api/v1/categories",
        headers=auth_headers(token),
        json={"name": name, "type": type},
    )
    return response.json()["id"]


class TestYearlyStatistics:
    async def test_yearly_statistics_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/statistics/year?year=2026", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2026
        assert float(data["total_income"]) == 0
        assert len(data["monthly_breakdown"]) == 12

    async def test_yearly_statistics_with_data(self, client):
        token = await register_and_login(client, "mateo@test.com")
        category_id = await create_category(client, token, "Alquiler", "expense")

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={"amount": 3000000, "description": "Salario", "income_date": "2026-07-05"},
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 1200000,
                "description": "Arriendo",
                "expense_date": "2026-07-01",
                "category_id": category_id,
            },
        )

        response = await client.get(
            "/api/v1/statistics/year?year=2026", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_income"]) == 3000000
        assert float(data["total_expense"]) == 1200000
        assert float(data["balance"]) == 1800000
        assert data["top_categories"][0]["category"] == "Alquiler"
        july = next(m for m in data["monthly_breakdown"] if m["month"] == 7)
        assert float(july["income"]) == 3000000
        assert float(july["expense"]) == 1200000


class TestCategoryStatistics:
    async def test_category_statistics_expense(self, client):
        token = await register_and_login(client, "mateo@test.com")
        category_id = await create_category(client, token, "Comida", "expense")

        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 100000,
                "description": "Almuerzo",
                "expense_date": "2026-07-10",
                "category_id": category_id,
            },
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={
                "amount": 200000,
                "description": "Cena",
                "expense_date": "2026-07-12",
                "category_id": category_id,
            },
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={"amount": 50000, "description": "Pasaje", "expense_date": "2026-07-13"},
        )

        response = await client.get(
            "/api/v1/statistics/category?month=7&year=2026&type=expense",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        comida = next(item for item in data if item["category_name"] == "Comida")
        assert float(comida["total_amount"]) == 300000
        assert comida["transaction_count"] == 2
        assert comida["percentage_of_total"] == 85.71

    async def test_category_statistics_income(self, client):
        token = await register_and_login(client, "mateo@test.com")
        category_id = await create_category(client, token, "Ingreso Extra", "income")

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={
                "amount": 2500000,
                "description": "Ingreso extra",
                "income_date": "2026-07-01",
                "category_id": category_id,
            },
        )

        response = await client.get(
            "/api/v1/statistics/category?month=7&year=2026&type=income",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category_name"] == "Ingreso Extra"
        assert float(data[0]["total_amount"]) == 2500000

    async def test_category_statistics_invalid_type(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/statistics/category?type=transfer",
            headers=auth_headers(token),
        )
        assert response.status_code == 422


class TestCoupleStatistics:
    async def test_couple_statistics_requires_couple(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/statistics/couple", headers=auth_headers(token)
        )
        assert response.status_code == 409

    async def test_couple_statistics_with_data(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]
        await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(mateo_token),
            json={"amount": 3000000, "description": "Salario Mateo", "income_date": "2026-07-05"},
        )
        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(salome_token),
            json={"amount": 2000000, "description": "Salario Salomé", "income_date": "2026-07-05"},
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(mateo_token),
            json={"amount": 1000000, "description": "Gasto Mateo", "expense_date": "2026-07-06"},
        )

        response = await client.get(
            "/api/v1/statistics/couple", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["personal_income"]) == 3000000
        assert float(data["personal_expense"]) == 1000000
        assert float(data["shared_income"]) == 0
        assert float(data["total_income"]) == 3000000
        assert len(data["partner_contribution"]) == 2
