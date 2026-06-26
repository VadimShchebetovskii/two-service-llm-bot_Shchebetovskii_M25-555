import pytest
from unittest.mock import AsyncMock
import fakeredis.aioredis
from aiogram.types import Message, User, Chat


@pytest.fixture
def fake_redis(monkeypatch):
    """Создаёт fake Redis для тестов."""

    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    def mock_get_redis():
        return redis

    monkeypatch.setattr("app.bot.handlers.get_redis", mock_get_redis)

    return redis


@pytest.fixture
def mock_celery(mocker):
    """Мокает Celery task."""

    mock = mocker.patch("app.bot.handlers.llm_request.delay")
    return mock


@pytest.fixture
def mock_decode_token(mocker):
    """Мокает decode_and_validate для успешной валидации."""

    mock = mocker.patch("app.bot.handlers.decode_and_validate")
    mock.return_value = {"sub": "1", "role": "user"}
    return mock


@pytest.fixture
def fake_message():
    """Создаёт fake Telegram сообщение."""

    message = AsyncMock(spec=Message)
    message.from_user = User(id=1, is_bot=False, first_name="Test")
    message.chat = Chat(id=1, type="private")
    message.answer = AsyncMock()
    return message