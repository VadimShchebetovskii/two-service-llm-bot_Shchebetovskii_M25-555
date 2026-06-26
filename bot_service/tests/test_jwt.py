import time
import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate
from app.core.errors import InvalidTokenError, TokenExpiredError


def create_test_token(payload: dict, exp_seconds: int = 3600) -> str:
    """Создаёт тестовый JWT токен."""

    payload_copy = payload.copy()
    payload_copy["iat"] = int(time.time())
    payload_copy["exp"] = int(time.time()) + exp_seconds
    payload_copy["type"] = "access"
    return jwt.encode(payload_copy, settings.jwt_secret, algorithm=settings.jwt_alg)


@pytest.mark.anyio
class TestJWTValidation:
    """Юнит-тесты для JWT валидации."""

    def test_decode_valid_token(self):
        token = create_test_token({"sub": "1", "role": "user"})
        payload = decode_and_validate(token)

        assert payload["sub"] == "1"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload

    def test_decode_invalid_token_raises_error(self):
        with pytest.raises(InvalidTokenError):
            decode_and_validate("invalid.token")

    def test_decode_expired_token_raises_error(self):
        token = create_test_token({"sub": "1", "role": "user"}, exp_seconds=-1)

        with pytest.raises(TokenExpiredError):
            decode_and_validate(token)

    def test_token_without_sub_raises_error(self):
        token = create_test_token({"role": "user"})

        with pytest.raises(InvalidTokenError, match="Missing sub in token"):
            decode_and_validate(token)

    def test_token_without_role_raises_error(self):
        token = create_test_token({"sub": "1"})

        with pytest.raises(InvalidTokenError, match="Missing role in token"):
            decode_and_validate(token)
