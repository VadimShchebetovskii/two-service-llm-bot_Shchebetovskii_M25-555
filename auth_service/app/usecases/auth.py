from app.repositories.users import UserRepository
from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError
from app.core.security import hash_password, create_access_token, verify_password
from app.schemas.auth import TokenResponse
from app.schemas.user import UserPublic


class AuthService:
    """Бизнес-логика аутентификации."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def register(self, email: str, password: str) -> UserPublic:
        """
        Регистрация нового пользователя.

        Raises:
            UserAlreadyExistsError: Если email уже занят.
        """
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()

        created_user = await self._user_repository.create(
            email=email,
            password_hash=hash_password(password),
            role="user"
        )
        return UserPublic.model_validate(created_user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Аутентификация пользователя и выдача JWT.

        Raises:
            InvalidCredentialsError: Если email не найден или пароль неверный.
        """
        user = await self._user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token({"sub": str(user.id), "role": user.role})
        return TokenResponse(access_token=token)

    async def me(self, user_id: int) -> UserPublic:
        """
        Получение профиля текущего пользователя по ID.

        Raises:
            UserNotFoundError: Если пользователь не найден.
        """
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)
