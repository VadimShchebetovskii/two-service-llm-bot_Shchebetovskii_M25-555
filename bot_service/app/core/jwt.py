from typing import Any
from jose import jwt, JWTError
from app.core.config import settings
from app.core.errors import InvalidTokenError, TokenExpiredError


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Декодирует и валидирует JWT токен.
    
    Raises:
        InvalidTokenError: Если токен невалидный (неверная подпись, отсутствуют обязательные поля, неправильный тип)
        TokenExpiredError: Если срок действия токена истёк
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    if "sub" not in payload:
        raise InvalidTokenError("Missing sub in token")
    if "role" not in payload:
        raise InvalidTokenError("Missing role in token")
    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")
    
    return payload
