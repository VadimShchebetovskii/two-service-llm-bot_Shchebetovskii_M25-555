import time
import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.exceptions import InvalidTokenError


class TestPasswordHashing:
    """Юнит-тесты для хеширования паролей."""

    def test_hash_password_returns_different_string(self):
        password = "password"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_verify_password_correct(self):
        password = "password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    """Юнит-тесты для JWT."""

    def test_create_and_decode_token(self):
        payload = {"sub": "1", "role": "user"}

        token = create_access_token(payload)
        decoded = decode_access_token(token)

        assert decoded["sub"] == "1"
        assert decoded["role"] == "user"
        assert "iat" in decoded
        assert "exp" in decoded

    def test_create_token_missing_sub_raises_error(self):
        with pytest.raises(ValueError, match="Missing required field: sub"):
            create_access_token({"role": "user"})

    def test_create_token_missing_role_raises_error(self):
        with pytest.raises(ValueError, match="Missing required field: role"):
            create_access_token({"sub": "1"})

    def test_decode_invalid_token_raises_error(self):
        with pytest.raises(InvalidTokenError):
            decode_access_token("invalid.token")

    def test_decode_token_missing_sub_raises_error(self):
        payload = {"role": "user", "iat": int(time.time()), "exp": int(time.time()) + 60}
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

        with pytest.raises(InvalidTokenError, match="Missing sub in token"):
            decode_access_token(token)

    def test_decode_token_missing_role_raises_error(self):
        payload = {"sub": "1", "iat": int(time.time()), "exp": int(time.time()) + 60}
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

        with pytest.raises(InvalidTokenError, match="Missing role in token"):
            decode_access_token(token)

    def test_decode_token_invalid_type_raises_error(self):
        payload = {"sub": "1", "role": "user", "type": "refresh", "iat": int(time.time()), "exp": int(time.time()) + 60}
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

        with pytest.raises(InvalidTokenError, match="Invalid token type"):
            decode_access_token(token)
