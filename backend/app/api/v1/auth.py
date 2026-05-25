from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.schemas.auth import LoginIn, RefreshIn, RegisterIn, TelegramAuthIn, TokenPair
from app.schemas.user import UserOut
from app.services import auth as auth_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
async def register(payload: RegisterIn, session: SessionDep) -> TokenPair:
    _, access, refresh = await auth_svc.register_email(
        session, payload.email, payload.password, payload.role
    )
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, session: SessionDep) -> TokenPair:
    _, access, refresh = await auth_svc.login_email(session, payload.email, payload.password)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/telegram", response_model=TokenPair)
async def telegram_login(payload: TelegramAuthIn, session: SessionDep) -> TokenPair:
    _, access, refresh = await auth_svc.login_telegram(
        session, payload.init_data, payload.bot, payload.role
    )
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshIn, session: SessionDep) -> TokenPair:
    access, refresh = await auth_svc.refresh_session(session, payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=204)
async def logout(payload: RefreshIn, session: SessionDep) -> None:
    await auth_svc.logout(session, payload.refresh_token)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
