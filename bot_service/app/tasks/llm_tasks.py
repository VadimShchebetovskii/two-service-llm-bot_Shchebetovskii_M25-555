import asyncio
import json
import logging
from celery import shared_task

from app.services.openrouter_client import OpenRouterClient
from app.infra.redis import get_redis


DEFAULT_TTL = 3600

logger = logging.getLogger(__name__)


@shared_task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> dict:
    """
    Celery задача для обработки LLM запроса.
    
    Результат сохраняется в Redis под ключом:
        result:{tg_chat_id}:{task_id}
    """
    task_id = llm_request.request.id
    result_key = f"result:{tg_chat_id}:{task_id}"
    
    try:
        response = asyncio.run(_process_llm_request(prompt))
        
        asyncio.run(_save_result_to_redis(result_key, {
            "status": "success",
            "response": response,
            "task_id": task_id,
        }))
        
        return {"status": "success", "response": response, "task_id": task_id}
        
    except Exception as e:
        logger.error(f"Error in llm_request: {e}")

        asyncio.run(_save_result_to_redis(result_key, {
            "status": "error",
            "error": str(e),
            "task_id": task_id,
        }))
        
        raise


async def _process_llm_request(prompt: str) -> str:
    """Обработка LLM запроса."""

    client = OpenRouterClient()
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat_completion(messages)
    return response


async def _save_result_to_redis(key: str, data: dict, ttl: int = DEFAULT_TTL) -> None:
    """Сохраняет результат в Redis."""
    
    try:
        redis = get_redis()
        await redis.set(key, json.dumps(data), ex=ttl)
        logger.debug(f"Saved result to Redis: {key}")
    except Exception as e:
        logger.error(f"Failed to save result to Redis: {e}")
