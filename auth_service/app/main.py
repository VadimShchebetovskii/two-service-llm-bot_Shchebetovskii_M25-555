import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import router
from app.db.base import Base
from app.core.config import settings
from app.db.session import engine
from app.core.exceptions import BaseHTTPException


logger = logging.getLogger("auth_service")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления X-Request-Id в каждый запрос."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


async def base_http_exception_handler(request: Request, exc: BaseHTTPException):
    """Обработчик кастомных HTTP-исключений."""

    request_id = getattr(request.state, "request_id", None)
    
    content = {"detail": exc.detail, "path": request.url.path}

    if request_id:
        content["request_id"] = request_id
    
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic."""

    request_id = getattr(request.state, "request_id", None)
    
    content = {
        "detail": "Validation error",
        "errors": exc.errors(),
        "path": request.url.path,
    }

    if request_id:
        content["request_id"] = request_id
    
    return JSONResponse(status_code=422, content=content)


async def global_exception_handler(request: Request, exc: Exception):
    """Обработчик всех непредвиденных исключений."""

    request_id = getattr(request.state, "request_id", None)
    
    logger.exception(
        "Unhandled error. path=%s request_id=%s error=%s",
        request.url.path,
        request_id,
        str(exc),
    )
    
    content = {"detail": "Internal server error", "path": request.url.path}

    if request_id:
        content["request_id"] = request_id
    
    return JSONResponse(status_code=500, content=content)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Auth service: registration + JWT issuing",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    app.add_middleware(RequestIdMiddleware)
    
    app.add_exception_handler(BaseHTTPException, base_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    app.include_router(router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "environment": settings.env}
    
    return app


app = create_app()
