from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение"""
    
    def __init__(self, status_code: int, detail: str, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь с таким email уже существует (409)."""
    
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InvalidCredentialsError(BaseHTTPException):
    """Неверный email или пароль (401)."""
    
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidTokenError(BaseHTTPException):
    """Невалидный токен (401)."""
    
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class TokenExpiredError(BaseHTTPException):
    """Токен истёк (401)."""
    
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден (404)."""
    
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDeniedError(BaseHTTPException):
    """Недостаточно прав (403)."""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
