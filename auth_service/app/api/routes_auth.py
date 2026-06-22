from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthService
from app.api.deps import get_auth_uc, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(data: RegisterRequest, auth_uc: AuthService = Depends(get_auth_uc)):
    result = await auth_uc.register(data.email, data.password)
    return result


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_uc: AuthService = Depends(get_auth_uc)):
    result = await auth_uc.login(form_data.username, form_data.password)
    return result


@router.get("/me", response_model=UserPublic)
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
