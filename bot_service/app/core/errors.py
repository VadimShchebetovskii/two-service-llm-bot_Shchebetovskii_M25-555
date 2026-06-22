from typing import Any, Dict, Optional


class AppError(Exception):
    """
    Базовое исключение приложения.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class InvalidTokenError(AppError):
    """
    Исключение невалидного токена.
    
    Возникает когда JWT токен имеет неверную подпись,
    отсутствуют обязательные поля или неправильный тип.
    """
    pass


class TokenExpiredError(AppError):
    """
    Исключение истекшего токена.
    
    Возникает когда срок действия JWT токена истёк.
    """
    pass


class OpenRouterError(AppError):
    """
    Исключение ошибки OpenRouter.
    
    Возникает при таймауте, HTTP ошибке или пустом ответе от LLM.
    """
    pass


class RedisError(AppError):
    """
    Исключение ошибки Redis.
    
    Возникает при недоступности Redis или ошибке выполнения команды.
    """
    pass


class CeleryError(AppError):
    """
    Исключение ошибки Celery.
    
    Возникает при проблемах с отправкой задачи в очередь.
    """
    pass


class NotFoundError(AppError):
    """
    Исключение отсутствия объекта.
    
    Возникает когда запрашиваемый объект не найден.
    """
    pass


class ValidationError(AppError):
    """
    Исключение ошибки валидации.
    
    Возникает когда входные данные не проходят бизнес-валидацию.
    """
    pass
