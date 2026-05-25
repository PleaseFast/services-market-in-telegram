from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.schemas.user import UserOut
from app.services.profiles import delete_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.delete("/me", status_code=204)
async def delete_me(user: CurrentUser, session: SessionDep) -> None:
    await delete_user(session, user)
