import redis.asyncio as redis
from app.core.config import settings


_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """
    Возвращает клиент Redis (синглтон).
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Закрывает соединение с Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
