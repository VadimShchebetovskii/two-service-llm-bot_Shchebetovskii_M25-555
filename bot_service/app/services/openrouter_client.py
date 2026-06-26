import httpx
from app.core.errors import OpenRouterError
from app.core.config import settings


DEFAULT_TIMEOUT = 30.0
DEFAULT_TEMPERATURE = 0.7


class OpenRouterClient:
    """Клиент для взаимодействия с OpenRouter API (LLM)"""

    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.referer = settings.openrouter_site_url
        self.title = settings.openrouter_app_name

    async def chat_completion(self, messages: list[dict[str, str]], temperature: float = DEFAULT_TEMPERATURE) -> str:
        """Отправляет запрос к LLM и возвращает текст ответа"""

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, verify=False) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.referer,
                    "X-Title": self.title,
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature
                }
            )

            if response.status_code != 200:
                raise OpenRouterError(f"OpenRouter error: {response.status_code} - {response.text}")

            result = response.json()
            
            choices = result.get("choices", [])
            if not choices:
                raise OpenRouterError("Unexpected response: empty choices")
            
            message = choices[0].get("message", {})
            content = message.get("content")
            
            if not content:
                raise OpenRouterError("Unexpected response: empty content")
            
            return content
