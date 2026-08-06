"""
Integration tests: /api/v1/shared-incomes/*
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


async def create_couple(client, inviter_email, acceptor_email):
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


class TestSharedIncomeRequiresCouple:
    async def test_create_shared_income_without_couple_returns_409(self, client):
        token = await register_and_login(client, "maria@test.com")
        response = await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(token),
            json={
                "amount": 100000,
                "description": "Salario",
                "income_date": "2026-07-20",
            },
        )
        assert response.status_code == 409

    async def test_list_shared_incomes_without_couple_returns_409(self, client):
        token = await register_and_login(client, "maria@test.com")
        response = await client.get(
            "/api/v1/shared-incomes", headers=auth_headers(token)
        )
        assert response.status_code == 409


class TestCreateSharedIncome:
    async def test_create_shared_income_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(mateo_token),
            json={
                "amount": 200000,
                "description": "Arriendo recibido",
                "income_date": "2026-07-20",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 200000
        assert data["received_by"] == str(
            (await client.get("/api/v1/users/me", headers=auth_headers(mateo_token))).json()["id"]
        )


class TestListSharedIncomes:
    async def test_list_shared_incomes_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Ingreso 1",
                "income_date": "2026-07-20",
            },
        )
        await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(salome_token),
            json={
                "amount": 50000,
                "description": "Ingreso 2",
                "income_date": "2026-07-21",
            },
        )

        response = await client.get(
            "/api/v1/shared-incomes", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 2


class TestUpdateSharedIncome:
    async def test_update_shared_income_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Ingreso original",
                "income_date": "2026-07-20",
            },
        )
        income_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/v1/shared-incomes/{income_id}",
            headers=auth_headers(mateo_token),
            json={
                "amount": 150000,
                "description": "Ingreso actualizado",
            },
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert float(data["amount"]) == 150000
        assert data["description"] == "Ingreso actualizado"

    async def test_update_other_partner_income_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(salome_token),
            json={
                "amount": 80000,
                "description": "Ingreso de salome",
                "income_date": "2026-07-20",
            },
        )
        income_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/v1/shared-incomes/{income_id}",
            headers=auth_headers(mateo_token),
            json={"description": "Ingreso editado por la pareja"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["description"] == "Ingreso editado por la pareja"


class TestDeleteSharedIncome:
    async def test_delete_shared_income_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/shared-incomes",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Para borrar",
                "income_date": "2026-07-20",
            },
        )
        income_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/shared-incomes/{income_id}",
            headers=auth_headers(mateo_token),
        )
        assert delete_resp.status_code == 204

        list_resp = await client.get(
            "/api/v1/shared-incomes", headers=auth_headers(mateo_token)
        )
        assert list_resp.json()["pagination"]["total"] == 0

    async def test_delete_missing_income_returns_404(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        delete_resp = await client.delete(
            "/api/v1/shared-incomes/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(mateo_token),
        )
        assert delete_resp.status_code == 404
