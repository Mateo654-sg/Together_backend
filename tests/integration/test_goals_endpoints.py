"""
Integration tests: /api/v1/goals/*

Cubre el Módulo 5 — Metas (FR-061 a FR-072).
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


class TestGoalRequiresCouple:
    async def test_create_goal_without_couple_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post(
            "/api/v1/goals",
            headers=auth_headers(token),
            json={
                "title": "Viaje a Europa",
                "target_amount": 5000000,
            },
        )
        assert response.status_code == 409

    async def test_list_goals_without_couple_returns_409(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get(
            "/api/v1/goals", headers=auth_headers(token)
        )
        assert response.status_code == 409


class TestCreateGoal:
    async def test_create_goal_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={
                "title": "Viaje a Europa",
                "description": "Vacaciones de verano",
                "target_amount": 5000000,
                "target_date": "2026-12-31",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Viaje a Europa"
        assert float(data["target_amount"]) == 5000000
        assert float(data["current_amount"]) == 0
        assert data["status"] == "active"

    async def test_create_goal_with_image(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={
                "title": "Nuevo auto",
                "target_amount": 30000000,
                "image": "https://example.com/car.jpg",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["image"] == "https://example.com/car.jpg"


class TestListGoals:
    async def test_list_goals_empty(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.get(
            "/api/v1/goals", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_list_goals_with_data(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta 1", "target_amount": 1000000},
        )
        await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta 2", "target_amount": 2000000},
        )

        response = await client.get(
            "/api/v1/goals", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 2


class TestUpdateGoal:
    async def test_update_goal_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta Original", "target_amount": 1000000},
        )
        goal_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/goals/{goal_id}",
            headers=auth_headers(mateo_token),
            json={"title": "Meta Actualizada", "target_amount": 2000000},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Meta Actualizada"
        assert float(data["target_amount"]) == 2000000

    async def test_update_goal_not_found_returns_404(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        import uuid

        response = await client.put(
            f"/api/v1/goals/{uuid.uuid4()}",
            headers=auth_headers(mateo_token),
            json={"title": "No existe"},
        )
        assert response.status_code == 404


class TestDeleteGoal:
    async def test_delete_goal_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta a eliminar", "target_amount": 500000},
        )
        goal_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/goals/{goal_id}", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 204

        list_resp = await client.get(
            "/api/v1/goals", headers=auth_headers(mateo_token)
        )
        assert list_resp.json()["pagination"]["total"] == 0


class TestContributeToGoal:
    async def test_contribute_success(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Fondo de emergencia", "target_amount": 1000000},
        )
        goal_id = create_resp.json()["id"]

        response = await client.post(
            "/api/v1/goals/contribute",
            headers=auth_headers(mateo_token),
            json={"goal_id": goal_id, "amount": 250000},
        )
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 250000
        assert data["goal_id"] == goal_id

        goal_resp = await client.get(
            "/api/v1/goals", headers=auth_headers(mateo_token)
        )
        goal = goal_resp.json()["data"][0]
        assert float(goal["current_amount"]) == 250000

    async def test_contribute_completes_goal(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Laptop", "target_amount": 500000},
        )
        goal_id = create_resp.json()["id"]

        await client.post(
            "/api/v1/goals/contribute",
            headers=auth_headers(mateo_token),
            json={"goal_id": goal_id, "amount": 500000},
        )

        goal_resp = await client.get(
            "/api/v1/goals", headers=auth_headers(mateo_token)
        )
        goal = goal_resp.json()["data"][0]
        assert goal["status"] == "completed"

    async def test_contribute_to_nonexistent_goal_returns_404(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        import uuid

        response = await client.post(
            "/api/v1/goals/contribute",
            headers=auth_headers(mateo_token),
            json={"goal_id": str(uuid.uuid4()), "amount": 100000},
        )
        assert response.status_code == 404


class TestGoalHistory:
    async def test_history_empty(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.get(
            "/api/v1/goals/history", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_history_with_contributions(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        create_resp = await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Vacaciones", "target_amount": 2000000},
        )
        goal_id = create_resp.json()["id"]

        await client.post(
            "/api/v1/goals/contribute",
            headers=auth_headers(mateo_token),
            json={"goal_id": goal_id, "amount": 500000},
        )
        await client.post(
            "/api/v1/goals/contribute",
            headers=auth_headers(salome_token),
            json={"goal_id": goal_id, "amount": 300000},
        )

        response = await client.get(
            "/api/v1/goals/history", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2


class TestGoalStatistics:
    async def test_statistics_empty(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        response = await client.get(
            "/api/v1/goals/statistics", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_goals"] == 0
        assert data["active_goals"] == 0

    async def test_statistics_with_goals(self, client):
        mateo_token, salome_token = await create_couple(
            client, "mateo@test.com", "salome@test.com"
        )

        await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta 1", "target_amount": 1000000},
        )
        await client.post(
            "/api/v1/goals",
            headers=auth_headers(mateo_token),
            json={"title": "Meta 2", "target_amount": 2000000},
        )

        response = await client.get(
            "/api/v1/goals/statistics", headers=auth_headers(mateo_token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_goals"] == 2
        assert data["active_goals"] == 2
        assert float(data["total_target"]) == 3000000
