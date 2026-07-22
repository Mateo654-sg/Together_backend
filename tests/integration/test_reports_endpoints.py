"""
Integration tests: /api/v1/reports/* y /api/v1/statistics/*

Cubre el Módulo 8 — Reportes y Estadísticas (FR-089 a FR-098).
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


class TestListReports:
    async def test_list_reports_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/reports", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0


class TestGenerateReport:
    async def test_generate_monthly_report(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/reports",
            headers=auth_headers(token),
            json={
                "report_type": "monthly",
                "format": "pdf",
                "month": 7,
                "year": 2026,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["report_type"] == "monthly"
        assert data["format"] == "pdf"
        assert data["status"] == "completed"

    async def test_generate_invalid_type_returns_422(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/reports",
            headers=auth_headers(token),
            json={"report_type": "invalid_type", "format": "pdf"},
        )
        assert response.status_code == 422


class TestDownloadReport:
    async def test_download_report_success(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/reports",
            headers=auth_headers(token),
            json={"report_type": "monthly", "format": "pdf"},
        )
        report_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/reports/{report_id}", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["id"] == report_id

    async def test_download_report_not_found_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")

        import uuid
        response = await client.get(
            f"/api/v1/reports/{uuid.uuid4()}", headers=auth_headers(token)
        )
        assert response.status_code == 404


class TestDeleteReport:
    async def test_delete_report_success(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/reports",
            headers=auth_headers(token),
            json={"report_type": "yearly", "format": "excel"},
        )
        report_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/reports/{report_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        list_resp = await client.get(
            "/api/v1/reports", headers=auth_headers(token)
        )
        assert list_resp.json()["pagination"]["total"] == 0


class TestMonthlyStatistics:
    async def test_monthly_statistics_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/statistics/month", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_income"]) == 0
        assert float(data["total_expense"]) == 0

    async def test_monthly_statistics_with_data(self, client):
        token = await register_and_login(client, "mateo@test.com")

        await client.post(
            "/api/v1/incomes",
            headers=auth_headers(token),
            json={"amount": 500000, "description": "Salario", "income_date": "2026-07-20"},
        )
        await client.post(
            "/api/v1/expenses",
            headers=auth_headers(token),
            json={"amount": 150000, "description": "Almuerzo", "expense_date": "2026-07-20"},
        )

        response = await client.get(
            "/api/v1/statistics/month?month=7&year=2026",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_income"]) == 500000
        assert float(data["total_expense"]) == 150000
        assert float(data["balance"]) == 350000


class TestPersonalStatistics:
    async def test_personal_statistics_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/statistics/personal", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_income"]) == 0
        assert float(data["total_expense"]) == 0
        assert data["top_expense_categories"] == []
