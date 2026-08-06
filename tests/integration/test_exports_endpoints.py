"""
Integration tests: /api/v1/exports/*

Cubre la exportación de datos financieros en PDF/Excel/CSV
(FR-095, FR-096, FR-097) y el historial de exportaciones (FR-130).
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


async def seed_movements(client, token):
    await client.post(
        "/api/v1/expenses",
        headers=auth_headers(token),
        json={
            "amount": 1200000,
            "description": "Arriendo",
            "expense_date": "2026-07-01",
        },
    )
    await client.post(
        "/api/v1/incomes",
        headers=auth_headers(token),
        json={
            "amount": 3500000,
            "description": "Salario mensual",
            "income_date": "2026-07-05",
        },
    )


class TestExportsAuthentication:
    async def test_list_requires_authentication(self, client):
        response = await client.get("/api/v1/exports")
        assert response.status_code == 401

    async def test_pdf_requires_authentication(self, client):
        response = await client.post("/api/v1/exports/pdf", json={})
        assert response.status_code == 401


class TestExportCSV:
    async def test_export_csv_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await seed_movements(client, token)

        response = await client.post(
            "/api/v1/exports/csv",
            headers=auth_headers(token),
            json={"date_from": "2026-07-01", "date_to": "2026-07-31"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert "attachment" in response.headers["content-disposition"]
        assert response.content.startswith(b"\xef\xbb\xbf")
        text = response.content.decode("utf-8-sig")
        assert "Fecha" in text
        assert "Arriendo" in text
        assert "Salario mensual" in text


class TestExportPDF:
    async def test_export_pdf_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await seed_movements(client, token)

        response = await client.post(
            "/api/v1/exports/pdf", headers=auth_headers(token), json={}
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/pdf")
        assert "attachment" in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")


class TestExportExcel:
    async def test_export_excel_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await seed_movements(client, token)

        response = await client.post(
            "/api/v1/exports/excel", headers=auth_headers(token), json={}
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "application/vnd.openxmlformats"
        )
        assert "attachment" in response.headers["content-disposition"]
        assert response.content.startswith(b"PK")


class TestExportValidation:
    async def test_export_invalid_date_range(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/exports/csv",
            headers=auth_headers(token),
            json={"date_from": "2026-08-01", "date_to": "2026-07-01"},
        )
        assert response.status_code == 422


class TestExportHistory:
    async def test_export_history_records_exports(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await seed_movements(client, token)

        await client.post("/api/v1/exports/csv", headers=auth_headers(token), json={})
        await client.post("/api/v1/exports/pdf", headers=auth_headers(token), json={})
        await client.post("/api/v1/exports/excel", headers=auth_headers(token), json={})

        response = await client.get("/api/v1/exports", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 3
        formats = {item["format"] for item in data["data"]}
        assert formats == {"csv", "pdf", "excel"}
        assert all(item["file_size"] > 0 for item in data["data"])

    async def test_export_history_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/exports", headers=auth_headers(token))
        assert response.json()["data"] == []
