import pytest
import respx
from httpx import Response

from app.services.openrouter_client import OpenRouterClient, OpenRouterError
from app.core.config import settings


@pytest.mark.anyio
class TestOpenRouterClient:
    """Интеграционные тесты для OpenRouter клиента."""

    async def test_call_openrouter_success(self):
        """OpenRouter успешно возвращает ответ."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Привет! Это тестовый ответ."
                    }
                }
            ]
        }

        async with respx.mock(
            base_url=settings.openrouter_base_url,
            assert_all_called=False
        ) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(200, json=mock_response)
            )

            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Test"}]
            response = await client.chat_completion(messages)

            assert response == "Привет! Это тестовый ответ."

    async def test_call_openrouter_http_error(self):
        """HTTP ошибка вызывает OpenRouterError."""
        async with respx.mock(
            base_url=settings.openrouter_base_url,
            assert_all_called=False
        ) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(429, text="Too many requests")
            )

            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(OpenRouterError, match="429"):
                await client.chat_completion(messages)

    async def test_call_openrouter_empty_response(self):
        """пустой ответ вызывает OpenRouterError."""
        mock_response = {"choices": []}

        async with respx.mock(
            base_url=settings.openrouter_base_url,
            assert_all_called=False
        ) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(200, json=mock_response)
            )

            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(OpenRouterError, match="Unexpected response"):
                await client.chat_completion(messages)
