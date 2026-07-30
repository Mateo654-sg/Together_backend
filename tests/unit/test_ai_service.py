"""
Tests unitarios para AIService.

Mockea el proveedor de IA y el constructor de contexto para aislar
las pruebas de lógica del servicio.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.service import AIService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.name = "mock"
    provider.model = "mock-v1"
    provider.generate.return_value = {
        "answer": "Respuesta de prueba",
        "tokens_input": 10,
        "tokens_output": 5,
    }
    return provider


@pytest.fixture
def mock_context_builder():
    builder = AsyncMock()
    builder.build_context.return_value = "Contexto financiero de prueba"
    return builder


@pytest.fixture
def mock_history_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def service(mock_session, mock_provider, mock_context_builder, mock_history_repo):
    svc = AIService(mock_session, provider=mock_provider)
    svc.context_builder = mock_context_builder
    svc.history_repository = mock_history_repo
    return svc


class TestAIServiceChat:
    """Pruebas para el método chat de AIService."""

    @pytest.mark.asyncio
    async def test_chat_returns_expected_format(self, service, mock_provider, mock_context_builder):
        user_id = uuid.uuid4()
        result = await service.chat(user_id, "¿Cuánto gasté este mes?")

        mock_context_builder.build_context.assert_awaited_once_with(user_id)
        mock_provider.generate.assert_awaited_once()

        assert "answer" in result
        assert "tokens_used" in result
        assert "provider" in result
        assert result["answer"] == "Respuesta de prueba"
        assert result["tokens_used"] == 15
        assert result["provider"] == "mock"

    @pytest.mark.asyncio
    async def test_chat_creates_history_entry(
        self, service, mock_history_repo, mock_session
    ):
        user_id = uuid.uuid4()
        await service.chat(user_id, "¿Cuál es mi saldo?")

        mock_history_repo.create.assert_awaited_once()
        created = mock_history_repo.create.await_args.args[0]
        assert created.user_id == user_id
        assert created.question == "¿Cuál es mi saldo?"
        assert created.answer == "Respuesta de prueba"
        assert created.provider == "mock"
        assert created.model == "mock-v1"

        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_chat_without_openai_key_uses_mock_provider(self, mock_session):
        with patch("app.services.ai.service.settings") as mock_settings:
            mock_settings.openai_api_key = None
            svc = AIService(mock_session)
            assert svc.provider.name == "mock"
            assert svc.provider.model == "mock-v1"

    @pytest.mark.asyncio
    async def test_chat_with_openai_key_uses_openai_provider(self, mock_session):
        with (
            patch("app.services.ai.service.settings") as mock_settings,
            patch("app.services.ai.service.OpenAIProvider") as mock_openai_cls,
        ):
            mock_settings.openai_api_key = "sk-test"
            mock_openai_provider = AsyncMock()
            mock_openai_provider.name = "openai"
            mock_openai_cls.return_value = mock_openai_provider

            svc = AIService(mock_session)
            assert svc.provider.name == "openai"
            mock_openai_cls.assert_called_once_with("sk-test")


class TestAIServiceAddFeedback:
    """Pruebas para el método add_feedback de AIService."""

    @pytest.mark.asyncio
    async def test_add_feedback_updates_history(self, service, mock_history_repo, mock_session):
        user_id = uuid.uuid4()
        history_id = uuid.uuid4()
        mock_history = MagicMock()
        mock_history.feedback = None
        mock_history_repo.get_by_user_and_id.return_value = mock_history

        await service.add_feedback(user_id, history_id, 1)

        mock_history_repo.get_by_user_and_id.assert_awaited_once_with(user_id, history_id)
        assert mock_history.feedback == 1
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_feedback_when_history_not_found(
        self, service, mock_history_repo, mock_session
    ):
        mock_history_repo.get_by_user_and_id.return_value = None

        await service.add_feedback(uuid.uuid4(), uuid.uuid4(), -1)

        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_feedback_sets_negative(self, service, mock_history_repo, mock_session):
        user_id = uuid.uuid4()
        history_id = uuid.uuid4()
        mock_history = MagicMock()
        mock_history.feedback = None
        mock_history_repo.get_by_user_and_id.return_value = mock_history

        await service.add_feedback(user_id, history_id, -1)

        assert mock_history.feedback == -1
        mock_session.commit.assert_awaited_once()
