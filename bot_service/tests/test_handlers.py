import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, User, Chat

from app.bot.handlers import _token_key, start_handler, message_handler, token_handler, TOKEN_TTL


@pytest.mark.anyio
class TestHandlers:
    """Мок-тесты для Telegram обработчиков."""

    async def test_start_handler(self, fake_message):
        """Тест команды /start."""

        fake_message.text = "/start"

        await start_handler(fake_message)

        fake_message.answer.assert_called_once()
        assert "Отправь /token" in fake_message.answer.call_args[0][0]

    async def test_token_handler_saves_token_to_redis(self, fake_redis, mock_decode_token):
        """Тест команды /token — сохраняет токен в Redis."""

        message = AsyncMock(spec=Message)
        message.text = "/token valid.jwt.token"
        message.from_user = User(id=1, is_bot=False, first_name="Test")
        message.chat = Chat(id=1, type="private")
        message.answer = AsyncMock()

        await token_handler(message)

        key = _token_key(1)
        token = await fake_redis.get(key)
        assert token == "valid.jwt.token"

    async def test_message_handler_no_token(self, fake_redis, mock_celery, monkeypatch):
        """Тест: без токена бот НЕ вызывает Celery."""

        message = AsyncMock(spec=Message)
        message.text = "Hello"
        message.from_user = User(id=1, is_bot=False, first_name="Test")
        message.chat = Chat(id=1, type="private")
        message.answer = AsyncMock()

        await message_handler(message)

        mock_celery.assert_not_called()
        message.answer.assert_called()

    async def test_message_handler_with_token_calls_celery(self, fake_redis, mock_celery, mock_decode_token, monkeypatch):
        """Тест: с токеном бот вызывает Celery."""

        message = AsyncMock(spec=Message)
        message.text = "Hello"
        message.from_user = User(id=1, is_bot=False, first_name="Test")
        message.chat = Chat(id=1, type="private")
        message.answer = AsyncMock()

        key = _token_key(1)
        await fake_redis.set(key, "valid.jwt.token", ex=TOKEN_TTL)

        await message_handler(message)

        mock_celery.assert_called_once_with(1, "Hello")
