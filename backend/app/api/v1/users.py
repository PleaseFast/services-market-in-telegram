from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.core.i18n import SUPPORTED, normalize
from app.schemas.user import LanguageIn, LanguageOut, UserOut
from app.services.errors import DomainError
from app.services.profiles import delete_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.delete("/me", status_code=204)
async def delete_me(user: CurrentUser, session: SessionDep) -> None:
    await delete_user(session, user)


@router.get("/me/language", response_model=LanguageOut)
async def get_language(user: CurrentUser) -> LanguageOut:
    return LanguageOut(language=user.language or "ru")


@router.patch("/me/language", response_model=LanguageOut)
async def set_language(
    payload: LanguageIn, user: CurrentUser, session: SessionDep
) -> LanguageOut:
    requested = (payload.language or "").strip().lower()
    if requested not in SUPPORTED:
        raise DomainError(
            "users.language_unsupported",
            params={"language": requested, "supported": list(SUPPORTED)},
            message=f"Unsupported language '{requested}'",
        )
    user.language = normalize(requested)
    await session.commit()
    return LanguageOut(language=user.language)
