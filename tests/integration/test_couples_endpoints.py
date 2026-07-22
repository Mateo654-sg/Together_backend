"""
Integration tests: /api/v1/couples/*

Cubre el flujo completo del Módulo 2 — Pareja (FR-011 a FR-018).
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


class TestCoupleStatus:
    async def test_status_none_when_no_couple(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.get("/api/v1/couples", headers=auth_headers(token))
        assert response.status_code == 200
        assert response.json()["status"] == "none"
        assert response.json()["partner"] is None


class TestInvite:
    async def test_invite_creates_pending_couple_with_code(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.post("/api/v1/couples/invite", headers=auth_headers(token))
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert len(data["invitation_code"]) == 8
        assert data["partner_two_id"] is None

    async def test_status_pending_after_invite(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post("/api/v1/couples/invite", headers=auth_headers(token))
        response = await client.get("/api/v1/couples", headers=auth_headers(token))
        assert response.json()["status"] == "pending"

    async def test_cannot_invite_twice(self, client):
        token = await register_and_login(client, "mateo@test.com")
        await client.post("/api/v1/couples/invite", headers=auth_headers(token))
        response = await client.post("/api/v1/couples/invite", headers=auth_headers(token))
        assert response.status_code == 409

    async def test_invite_requires_authentication(self, client):
        response = await client.post("/api/v1/couples/invite")
        assert response.status_code == 401


class TestAccept:
    async def test_accept_success_links_couple(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]

        accept_response = await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )
        assert accept_response.status_code == 200
        data = accept_response.json()
        assert data["status"] == "accepted"
        assert data["partner_two_id"] is not None

    async def test_both_partners_see_accepted_status_with_partner_info(self, client):
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

        mateo_status = await client.get("/api/v1/couples", headers=auth_headers(mateo_token))
        salome_status = await client.get("/api/v1/couples", headers=auth_headers(salome_token))

        assert mateo_status.json()["status"] == "accepted"
        assert mateo_status.json()["partner"]["email"] == "salome@test.com"
        assert salome_status.json()["partner"]["email"] == "mateo@test.com"

    async def test_cannot_accept_own_invitation(self, client):
        token = await register_and_login(client, "mateo@test.com")
        invite_response = await client.post("/api/v1/couples/invite", headers=auth_headers(token))
        code = invite_response.json()["invitation_code"]

        response = await client.post(
            "/api/v1/couples/accept", headers=auth_headers(token), json={"invitation_code": code}
        )
        assert response.status_code == 422

    async def test_accept_invalid_code_returns_404(self, client):
        token = await register_and_login(client, "salome@test.com")
        response = await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(token),
            json={"invitation_code": "NOEXIST1"},
        )
        assert response.status_code == 404

    async def test_cannot_accept_already_accepted_invitation(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")
        ana_token = await register_and_login(client, "ana@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]
        await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )

        response = await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(ana_token),
            json={"invitation_code": code},
        )
        assert response.status_code == 409

    async def test_cannot_accept_if_already_in_active_couple(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")
        pedro_token = await register_and_login(client, "pedro@test.com")

        # Mateo + Salome ya vinculados
        invite1 = await client.post("/api/v1/couples/invite", headers=auth_headers(mateo_token))
        await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": invite1.json()["invitation_code"]},
        )

        # Pedro invita a Salome, quien ya tiene pareja activa
        invite2 = await client.post("/api/v1/couples/invite", headers=auth_headers(pedro_token))
        response = await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": invite2.json()["invitation_code"]},
        )
        assert response.status_code == 409


class TestReject:
    async def test_reject_success(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]

        response = await client.post(
            "/api/v1/couples/reject",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"

    async def test_after_reject_inviter_can_invite_again(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]
        await client.post(
            "/api/v1/couples/reject",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )

        new_invite = await client.post("/api/v1/couples/invite", headers=auth_headers(mateo_token))
        assert new_invite.status_code == 201


class TestUnlink:
    async def test_unlink_success_and_status_returns_none(self, client):
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

        unlink_response = await client.delete(
            "/api/v1/couples/unlink", headers=auth_headers(mateo_token)
        )
        assert unlink_response.status_code == 204

        status_response = await client.get("/api/v1/couples", headers=auth_headers(salome_token))
        assert status_response.json()["status"] == "none"

    async def test_unlink_without_couple_returns_404(self, client):
        token = await register_and_login(client, "mateo@test.com")
        response = await client.delete("/api/v1/couples/unlink", headers=auth_headers(token))
        assert response.status_code == 404

    async def test_after_unlink_both_can_form_new_couples(self, client):
        mateo_token = await register_and_login(client, "mateo@test.com")
        salome_token = await register_and_login(client, "salome@test.com")
        ana_token = await register_and_login(client, "ana@test.com")

        invite_response = await client.post(
            "/api/v1/couples/invite", headers=auth_headers(mateo_token)
        )
        code = invite_response.json()["invitation_code"]
        await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(salome_token),
            json={"invitation_code": code},
        )
        await client.delete("/api/v1/couples/unlink", headers=auth_headers(mateo_token))

        new_invite = await client.post("/api/v1/couples/invite", headers=auth_headers(mateo_token))
        assert new_invite.status_code == 201

        accept_new = await client.post(
            "/api/v1/couples/accept",
            headers=auth_headers(ana_token),
            json={"invitation_code": new_invite.json()["invitation_code"]},
        )
        assert accept_new.status_code == 200
