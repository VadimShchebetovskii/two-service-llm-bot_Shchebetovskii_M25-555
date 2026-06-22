import time
from typing import Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError


ACCESS_TOKEN_EXPIRE_SECONDS = settings.access_token_expire_minutes * 60


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль"""

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль на соответствие хешу"""

    return pwd_context.verify(password, hashed_password)


def _now() -> int:
    """Текущая временная метка в секундах"""

    return int(time.time())


def create_access_token(data: dict[str, Any]) -> str:
    """
    Создаёт JWT токен доступа

    Raises:
        ValueError: Если отсутствуют обязательные поля sub (user_id), role
    """

    if "sub" not in data:
        raise ValueError("Missing required field: sub")
    if "role" not in data:
        raise ValueError("Missing required field: role")

    to_encode = data.copy()
    to_encode.update({
        "type": "access",
        "iat": _now(),
        "exp": _now() + ACCESS_TOKEN_EXPIRE_SECONDS,
    })
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)


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
        raise TokenExpiredError()
    except JWTError as e:
        raise InvalidTokenError(detail=f"Invalid token: {str(e)}")
    
    if "sub" not in payload:
        raise InvalidTokenError(detail="Missing sub in token")
    if "role" not in payload:
        raise InvalidTokenError(detail="Missing role in token")
    if payload.get("type") != "access":
        raise InvalidTokenError(detail="Invalid token type")
    
    return payload
