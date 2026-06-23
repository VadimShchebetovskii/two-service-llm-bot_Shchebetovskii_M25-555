import json
import asyncio
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_access_token
from app.core.errors import InvalidTokenError, TokenExpiredError
from app.infra.redis import get_redis


logger = logging.getLogger(__name__)
router = Router()

TOKEN_TTL = 86400          # 24 часа
CHECK_ATTEMPTS = 30        # количество попыток
CHECK_INTERVAL = 1         # секунда между попытками


def _token_key(user_id: int) -> str:
    return f"token:{user_id}"


def _result_key(chat_id: int, task_id: str) -> str:
    return f"result:{chat_id}:{task_id}"


@router.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Отправь /token (jwt) для авторизации, затем текст для LLM.")


@router.message(Command("token"))
async def token_handler(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /token (jwt)")
        return

    token = parts[1]

    try:
        decode_access_token(token)
    except TokenExpiredError:
        await message.answer("Токен истёк")
        return
    except InvalidTokenError as e:
        await message.answer(f"Невалидный токен: {e}")
        return

    try:
        redis = get_redis()
        await redis.set(_token_key(message.from_user.id), token, ex=TOKEN_TTL)
        await message.answer("Токен сохранён!")
    except Exception as e:
        logger.error(f"Redis error: {e}")
        await message.answer("Ошибка сохранения токена")


@router.message()
async def message_handler(message: Message) -> None:
    redis = get_redis()
    user_key = _token_key(message.from_user.id)

    # 1. Получаем токен
    try:
        token = await redis.get(user_key)
    except Exception as e:
        logger.error(f"Redis get error: {e}")
        await message.answer("Ошибка проверки токена")
        return

    if not token:
        await message.answer("Токен не найден. Отправь /token (jwt)")
        return

    # 2. Валидируем токен
    try:
        decode_access_token(token)
    except TokenExpiredError:
        await message.answer("Токен истёк")
        await redis.delete(user_key)
        return
    except InvalidTokenError as e:
        await message.answer(f"Невалидный токен: {e}")
        await redis.delete(user_key)
        return

    # 3. Отправляем задачу в Celery
    try:
        from app.tasks.llm_tasks import llm_request
        task = llm_request.delay(message.chat.id, message.text)
        await message.answer("Запрос принят")

        # 4. Ждём результат
        result_key = _result_key(message.chat.id, task.id)
        for _ in range(CHECK_ATTEMPTS):
            await asyncio.sleep(CHECK_INTERVAL)
            result_data = await redis.get(result_key)
            if result_data:
                await redis.delete(result_key)
                result = json.loads(result_data)
                if result.get("status") == "success":
                    await message.answer(result["response"])
                else:
                    await message.answer(result["error"])
                return

        await message.answer("Таймаут ожидания ответа")

    except Exception as e:
        logger.error(f"Celery error: {e}")
        await message.answer("Ошибка отправки запроса")
