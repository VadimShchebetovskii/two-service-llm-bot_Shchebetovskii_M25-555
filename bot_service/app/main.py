import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.bot.dispatcher import start_polling, stop_polling
from app.infra.redis import close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_polling())
    yield

    task.cancel()
    await stop_polling()
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Telegram bot service with JWT auth, Celery, RabbitMQ, Redis, OpenRouter",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "environment": settings.env}

    return app


app = create_app()
