"""
Integration tests: /api/v1/shared-expenses/*

Cubre el Módulo 4 — Finanzas Compartidas (FR-041 a FR-054).
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


class TestSharedExpenseRequiresCouple:
    async def test_create_shared_expense_without_couple_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(token),
            json={
                "amount": 50000,
                "description": "Mercado",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 409

    async def test_list_shared_expenses_without_couple_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/shared-expenses", headers=auth_headers(token)
        )
        assert response.status_code == 409


class TestCreateSharedExpense:
    async def test_create_with_equal_split(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Mercado",
                "split_type": "equal",
                "expense_date": "2026-07-20",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 100000
        assert data["paid_by"] == str(
            (await client.get("/api/v1/users/me", headers=auth_headers(mateo_token))).json()["id"]
        )

    async def test_debt_generated_on_shared_expense(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Cena",
                "split_type": "equal",
                "expense_date": "2026-07-20",
            },
        )

        # Salome should see a pending debt
        debts_resp = await client.get(
            "/api/v1/debts", headers=auth_headers(salome_token)
        )
        assert debts_resp.status_code == 200
        debts = debts_resp.json()
        assert len(debts) == 1
        assert float(debts[0]["amount"]) == 50000  # 50% of 100000

    async def test_list_shared_expenses_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 50000,
                "description": "Gasto 1",
                "expense_date": "2026-07-20",
            },
        )

        response = await client.get(
            "/api/v1/shared-expenses", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        assert response.json()["pagination"]["total"] == 1


class TestDeleteSharedExpense:
    async def test_delete_cancels_debt(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Para borrar",
                "expense_date": "2026-07-20",
            },
        )
        expense_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/shared-expenses/{expense_id}",
            headers=auth_headers(mateo_token),
        )
        assert delete_resp.status_code == 204

        # Debt should be cancelled
        debts_resp = await client.get(
            "/api/v1/debts", headers=auth_headers(salome_token)
        )
        assert len(debts_resp.json()) == 0


class TestPayDebt:
    async def test_pay_debt_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Cena",
                "expense_date": "2026-07-20",
            },
        )

        debts_resp = await client.get(
            "/api/v1/debts", headers=auth_headers(salome_token)
        )
        debt_id = debts_resp.json()[0]["id"]

        pay_resp = await client.post(
            f"/api/v1/debts/{debt_id}/pay",
            headers=auth_headers(salome_token),
        )
        assert pay_resp.status_code == 200
        assert pay_resp.json()["status"] == "paid"

    async def test_only_debtor_can_pay(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Cena",
                "expense_date": "2026-07-20",
            },
        )

        debts_resp = await client.get(
            "/api/v1/debts", headers=auth_headers(salome_token)
        )
        debt_id = debts_resp.json()[0]["id"]

        # Creditor (mateo) tries to pay - should fail
        pay_resp = await client.post(
            f"/api/v1/debts/{debt_id}/pay",
            headers=auth_headers(mateo_token),
        )
        assert pay_resp.status_code == 422


class TestCoupleBalance:
    async def test_balance_zero_when_no_expenses(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.get(
            "/api/v1/debts/balance", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_shared_expenses"]) == 0

    async def test_balance_after_equal_expenses(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        # Mateo pays 100000
        await client.post(
            "/api/v1/shared-expenses",
            headers=auth_headers(mateo_token),
            json={
                "amount": 100000,
                "description": "Gasto 1",
                "expense_date": "2026-07-20",
            },
        )

        response = await client.get(
            "/api/v1/debts/balance", headers=auth_headers(mateo_token)
        )
        data = response.json()
        assert float(data["partner_one_paid"]) == 100000
        assert float(data["partner_two_paid"]) == 0
        assert float(data["balance"]) == 50000  # Mateo paid 100k, owed 50k
