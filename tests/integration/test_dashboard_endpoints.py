"""
Integration tests: /api/v1/dashboard/*

Cubre el Módulo 7 — Dashboard (FR-079 a FR-088).
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


async def create_couple(client, inviter_email, acceptor_email):
    """Helper: crea una pareja activa y retorna tokens de ambos."""
    inviter_token = await register_and_login(client, inviter_email)
    acceptor_token = await register_and_login(client, acceptor_email)

    invite_resp = await client.post(
        "/api/v1/couples/invite", headers=auth_headers(inviter_token)
    )
    code = invite_resp.json()["invitation_code"]

    await client.post(
        "/api/v1/couples/accept",
        headers=auth_headers(acceptor_token),
        json={"invitation_code": code},
    )

    return inviter_token, acceptor_token


class TestDashboard:
    async def test_dashboard_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/dashboard", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["balance"]) == 0
        assert float(data["income"]) == 0
        assert float(data["expense"]) == 0
        assert data["goals"] == []
        assert isinstance(data["statistics"], dict)
        assert isinstance(data["ai_recommendations"], list)

    async def test_dashboard_with_data(self, client):
        token = await register_and_login(client, "mateo@test.com")

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={"amount": 500000, "description": "Salario", "income_date": "2026-07-20"},
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={"amount": 100000, "description": "Almuerzo", "expense_date": "2026-07-20"},
        )

        response = await client.get(
            "/api/v1/dashboard", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["income"]) == 500000
        assert float(data["expense"]) == 100000
        assert float(data["balance"]) == 400000

    async def test_dashboard_with_goals(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Vacaciones", "target_amount": 2000000},
        )

        response = await client.get(
            "/api/v1/dashboard", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["title"] == "Vacaciones"


class TestCoupleDashboard:
    async def test_couple_dashboard_without_couple_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/dashboard/couple", headers=auth_headers(token)
        )
        assert response.status_code == 409

    async def test_couple_dashboard_empty(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.get(
            "/api/v1/dashboard/couple", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["personal_balance"]) == 0
        assert float(data["shared_balance"]) == 0
        assert data["goals"] == []

    async def test_couple_dashboard_with_data(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(mateo_token),
            json={"amount": 300000, "description": "Salario Mateo", "income_date": "2026-07-20"},
        )
        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={"amount": 50000, "description": "Mercado", "expense_date": "2026-07-20"},
        )

        response = await client.get(
            "/api/v1/dashboard/couple", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["personal_income"]) == 300000
        assert float(data["shared_expense"]) == 50000
