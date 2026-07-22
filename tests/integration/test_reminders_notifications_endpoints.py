"""
Integration tests: /api/v1/reminders/* y /api/v1/notifications/*

Cubre Módulo 10 — Recordatorios (FR-109 a FR-113) y Módulo 15 — Notificaciones (FR-132 a FR-135).
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


class TestReminders:
    async def test_list_reminders_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/reminders", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_create_reminder(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/reminders",
            headers=auth_headers(token),
            json={
                "title": "Pagar tarjeta",
                "description": "Fecha límite de pago",
                "due_date": "2026-07-25T10:00:00Z",
                "amount": "500000",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Pagar tarjeta"
        assert data["is_completed"] is False

    async def test_update_reminder(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/reminders",
            headers=auth_headers(token),
            json={"title": "Original", "due_date": "2026-07-25T10:00:00Z"},
        )
        reminder_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/reminders/{reminder_id}",
            headers=auth_headers(token),
            json={"title": "Actualizado"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Actualizado"

    async def test_delete_reminder(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/reminders",
            headers=auth_headers(token),
            json={"title": "A eliminar", "due_date": "2026-07-25T10:00:00Z"},
        )
        reminder_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/reminders/{reminder_id}", headers=auth_headers(token)
        )
        assert response.status_code == 204

    async def test_complete_reminder(self, client):
        token = await register_and_login(client, "mateo@test.com")

        create_resp = await client.post(
            "/api/v1/reminders",
            headers=auth_headers(token),
            json={"title": "Para completar", "due_date": "2026-07-25T10:00:00Z"},
        )
        reminder_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/reminders/{reminder_id}/complete",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["is_completed"] is True


class TestNotifications:
    async def test_list_notifications_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/notifications", headers=auth_headers(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["unread_count"] == 0

    async def test_mark_all_read(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.patch(
            "/api/v1/notifications/read", headers=auth_headers(token)
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
