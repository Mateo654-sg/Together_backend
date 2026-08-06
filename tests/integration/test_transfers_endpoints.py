"""
Integration tests: /api/v1/transfers/*

Cubre el módulo de transferencias entre métodos de pago (FR-021).
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


def transfer_payload(**overrides):
    payload = {
        "from_method": "Bancolombia",
        "to_method": "Nequi",
        "amount": 150000,
        "description": "Traslado para el mercado",
        "transfer_date": "2026-07-15",
    }
    payload.update(overrides)
    return payload


class TestTransfersAuthentication:
    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/transfers")
        assert response.status_code == 401

    async def test_create_requires_authentication(self, client):
        response = await client.post("/api/v1/transfers", json=transfer_payload())
        assert response.status_code == 401


class TestCreateTransfer:
    async def test_create_transfer_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        assert response.status_code == 201
        data = response.json()
        assert data["from_method"] == "Bancolombia"
        assert data["to_method"] == "Nequi"
        assert float(data["amount"]) == 150000
        assert data["transfer_date"] == "2026-07-15"

    async def test_create_transfer_same_method_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/transfers",
            headers=auth_headers(token),
            json=transfer_payload(from_method="Nequi", to_method="Nequi"),
        )
        assert response.status_code == 422

    async def test_create_transfer_invalid_method_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/transfers",
            headers=auth_headers(token),
            json=transfer_payload(from_method="Bitcoin"),
        )
        assert response.status_code == 422

    async def test_create_transfer_zero_amount_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/transfers",
            headers=auth_headers(token),
            json=transfer_payload(amount=0),
        )
        assert response.status_code == 422


class TestListTransfers:
    async def test_empty_list(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/transfers", headers=auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_list_with_transfers(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        await client.post(
            "/api/v1/transfers",
            headers=auth_headers(token),
            json=transfer_payload(
                from_method="Efectivo",
                to_method="Bancolombia",
                amount=50000,
                transfer_date="2026-07-01",
            ),
        )
        response = await client.get("/api/v1/transfers", headers=auth_headers(token))
        assert response.status_code == 200
        assert response.json()["pagination"]["total"] == 2

    async def test_list_filter_by_method(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        response = await client.get(
            "/api/v1/transfers",
            headers=auth_headers(token),
            params={"method": "Nequi"},
        )
        assert response.status_code == 200
        assert response.json()["pagination"]["total"] == 1

    async def test_list_filter_by_date_range(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        await client.post(
            "/api/v1/transfers",
            headers=auth_headers(token),
            json=transfer_payload(
                from_method="Efectivo",
                to_method="Bancolombia",
                amount=50000,
                transfer_date="2026-06-01",
            ),
        )
        response = await client.get(
            "/api/v1/transfers",
            headers=auth_headers(token),
            params={"date_from": "2026-07-01", "date_to": "2026-07-31"},
        )
        assert response.status_code == 200
        assert response.json()["pagination"]["total"] == 1

    async def test_transfers_are_isolated_between_users(self, client):
        token_a = await register_and_login(client, "user_a@test.com")
        token_b = await register_and_login(client, "user_b@test.com")
        await client.post(
            "/api/v1/transfers", headers=auth_headers(token_a), json=transfer_payload()
        )
        response = await client.get("/api/v1/transfers", headers=auth_headers(token_b))
        assert response.json()["data"] == []


class TestGetTransfer:
    async def test_get_transfer_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        transfer_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/transfers/{transfer_id}", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Traslado para el mercado"

    async def test_cannot_access_other_users_transfer(self, client):
        token_a = await register_and_login(client, "user_a@test.com")
        token_b = await register_and_login(client, "user_b@test.com")
        create_resp = await client.post(
            "/api/v1/transfers", headers=auth_headers(token_a), json=transfer_payload()
        )
        transfer_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/transfers/{transfer_id}", headers=auth_headers(token_b)
        )
        assert response.status_code == 404


class TestUpdateTransfer:
    async def test_update_transfer_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        transfer_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/transfers/{transfer_id}",
            headers=auth_headers(token),
            json={"amount": 200000},
        )
        assert response.status_code == 200
        assert float(response.json()["amount"]) == 200000

    async def test_update_transfer_to_same_method_rejected(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        transfer_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/transfers/{transfer_id}",
            headers=auth_headers(token),
            json={"to_method": "Bancolombia"},
        )
        assert response.status_code == 422

    async def test_update_nonexistent_transfer(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.put(
            f"/api/v1/transfers/{uuid.uuid4()}",
            headers=auth_headers(token),
            json={"amount": 1000},
        )
        assert response.status_code == 404


class TestDeleteTransfer:
    async def test_delete_transfer_success(self, client):
        token = await register_and_login(client, "mateo@test.com")
        create_resp = await client.post(
            "/api/v1/transfers", headers=auth_headers(token), json=transfer_payload()
        )
        transfer_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/transfers/{transfer_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

        list_resp = await client.get("/api/v1/transfers", headers=auth_headers(token))
        assert list_resp.json()["data"] == []

    async def test_delete_nonexistent_transfer(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.delete(
            f"/api/v1/transfers/{uuid.uuid4()}", headers=auth_headers(token)
        )
        assert response.status_code == 404
