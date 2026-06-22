from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthService
from app.core.security import decode_access_token
from app.core.exceptions import InvalidTokenError
from app.schemas.user import UserPublic

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


async def get_auth_uc(user_repo: UserRepository = Depends(get_users_repo)) -> AuthService:
    return AuthService(user_repo)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError(detail="Missing user ID in token")
    
    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise InvalidTokenError(detail="Invalid user ID format")


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_uc: AuthService = Depends(get_auth_uc),
) -> UserPublic:
    return await auth_uc.me(user_id)
