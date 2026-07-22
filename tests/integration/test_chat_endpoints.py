"""
Integration tests: /api/v1/chat/*

Cubre Módulo 12 — Chat de Pareja (FR-118 a FR-122).
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


class TestChat:
    async def test_list_messages_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/chat",
            headers=auth_headers(token),
            params={"partner_id": str("00000000-0000-0000-0000-000000000001")},
        )
        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_send_message(self, client):
        token_sender = await register_and_login(client, "sender@test.com")
        token_receiver = await register_and_login(client, "receiver@test.com")

        # Get receiver_id from profile
        profile_resp = await client.get(
            "/api/v1/users/profile", headers=auth_headers(token_receiver)
        )
        receiver_id = profile_resp.json()["id"]

        response = await client.post(
            "/api/v1/chat",
            headers=auth_headers(token_sender),
            json={
                "receiver_id": receiver_id,
                "content": "Hola, ¿cómo estás?",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hola, ¿cómo estás?"
        assert data["message_type"] == "text"

    async def test_send_emoji_message(self, client):
        token_sender = await register_and_login(client, "sender@test.com")
        token_receiver = await register_and_login(client, "receiver@test.com")

        profile_resp = await client.get(
            "/api/v1/users/profile", headers=auth_headers(token_receiver)
        )
        receiver_id = profile_resp.json()["id"]

        response = await client.post(
            "/api/v1/chat",
            headers=auth_headers(token_sender),
            json={
                "receiver_id": receiver_id,
                "message_type": "emoji",
                "content": "😊",
            },
        )
        assert response.status_code == 201
        assert response.json()["message_type"] == "emoji"

    async def test_delete_message(self, client):
        token_sender = await register_and_login(client, "sender@test.com")
        token_receiver = await register_and_login(client, "receiver@test.com")

        profile_resp = await client.get(
            "/api/v1/users/profile", headers=auth_headers(token_receiver)
        )
        receiver_id = profile_resp.json()["id"]

        create_resp = await client.post(
            "/api/v1/chat",
            headers=auth_headers(token_sender),
            json={"receiver_id": receiver_id, "content": "Mensaje a eliminar"},
        )
        message_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/chat/{message_id}", headers=auth_headers(token_sender)
        )
        assert response.status_code == 204

    async def test_delete_message_not_sender(self, client):
        token_sender = await register_and_login(client, "sender@test.com")
        token_receiver = await register_and_login(client, "receiver@test.com")

        profile_resp = await client.get(
            "/api/v1/users/profile", headers=auth_headers(token_receiver)
        )
        receiver_id = profile_resp.json()["id"]

        create_resp = await client.post(
            "/api/v1/chat",
            headers=auth_headers(token_sender),
            json={"receiver_id": receiver_id, "content": "No me borres"},
        )
        message_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/chat/{message_id}", headers=auth_headers(token_receiver)
        )
        assert response.status_code == 404
