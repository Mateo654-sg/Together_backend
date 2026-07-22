"""
Integration tests: /api/v1/ai/*

Cubre el Módulo 9 — IA Financiera (FR-098 a FR-108).
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


class TestAIChat:
    async def test_chat_success(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={"question": "¿Cuánto gasté este mes?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["provider"] == "mock"

    async def test_chat_empty_question_returns_422(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={"question": ""},
        )
        assert response.status_code == 422


class TestAIAnalyze:
    async def test_analyze_patterns(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/analyze",
            headers=auth_headers(token),
            json={"analysis_type": "patterns"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "patterns"
        assert isinstance(data["insights"], list)

    async def test_analyze_anomalies(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/analyze",
            headers=auth_headers(token),
            json={"analysis_type": "anomalies"},
        )
        assert response.status_code == 200
        assert response.json()["analysis_type"] == "anomalies"


class TestAIPredictions:
    async def test_predict_savings(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/predictions",
            headers=auth_headers(token),
            json={"prediction_type": "savings", "months_ahead": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prediction_type"] == "savings"
        assert isinstance(data["predictions"], list)
        assert len(data["predictions"]) > 0


class TestAIScore:
    async def test_get_score(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/score",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["score"] <= 100
        assert data["grade"] in ["Excellent", "Good", "Fair", "Poor"]
        assert isinstance(data["factors"], list)


class TestAIInsights:
    async def test_get_insights(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/ai/insights",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["insights"], list)
        assert len(data["insights"]) > 0


class TestAIRecommendations:
    async def test_get_recommendations(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/recommendations",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0


class TestAISummaries:
    async def test_monthly_summary(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/monthly-summary",
            headers=auth_headers(token),
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "Mensual"
        assert "summary" in data
        assert isinstance(data["highlights"], list)

    async def test_weekly_summary(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/weekly-summary",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["period"] == "Semanal"


class TestAIFinancialHealth:
    async def test_financial_health(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/financial-health",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["Excellent", "Good", "Fair", "Critical"]
        assert 0 <= data["score"] <= 100
        assert isinstance(data["indicators"], dict)


class TestAISimulator:
    async def test_simulate(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.post(
            "/api/v1/ai/simulate",
            headers=auth_headers(token),
            json={
                "scenario": "¿Qué pasa si ahorro 300.000 adicionales?",
                "monthly_amount": 300000,
                "months": 6,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "current_projection" in data
        assert "simulated_projection" in data
        assert "recommendation" in data


class TestAIHistory:
    async def test_get_history_empty(self, client):
        token = await register_and_login(client, "mateo@test.com")

        response = await client.get(
            "/api/v1/ai/history",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []

    async def test_history_after_chat(self, client):
        token = await register_and_login(client, "mateo@test.com")

        await client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={"question": "¿Cuánto ahorré?"},
        )

        response = await client.get(
            "/api/v1/ai/history",
            headers=auth_headers(token),
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1


class TestAIFeedback:
    async def test_send_feedback(self, client):
        token = await register_and_login(client, "mateo@test.com")

        chat_resp = await client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={"question": "Test question"},
        )
        history_id = chat_resp.json()["id"]

        response = await client.post(
            "/api/v1/ai/feedback",
            headers=auth_headers(token),
            json={"history_id": history_id, "feedback": 1},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
