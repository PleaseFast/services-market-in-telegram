from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.deps import CurrentUser, SessionDep
from app.repositories.specialists import get_profile_by_user, search_specialists
from app.schemas.common import Page
from app.schemas.profile import SpecialistProfileIn, SpecialistProfileOut
from app.services.profiles import upsert_specialist_profile

router = APIRouter(prefix="/specialists", tags=["specialists"])


@router.get("", response_model=Page[SpecialistProfileOut])
async def list_specialists(
    session: SessionDep,
    category: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[SpecialistProfileOut]:
    items, total = await search_specialists(session, category=category, limit=limit, offset=offset)
    return Page(
        items=[SpecialistProfileOut.model_validate(s) for s in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=SpecialistProfileOut)
async def get_my_profile(user: CurrentUser, session: SessionDep) -> SpecialistProfileOut:
    p = await get_profile_by_user(session, user.id)
    if p is None:
        raise HTTPException(404, "Profile not found")
    return SpecialistProfileOut.model_validate(p)


@router.put("/me", response_model=SpecialistProfileOut)
async def put_my_profile(
    payload: SpecialistProfileIn, user: CurrentUser, session: SessionDep
) -> SpecialistProfileOut:
    p = await upsert_specialist_profile(session, user, payload)
    return SpecialistProfileOut.model_validate(p)


@router.get("/{user_id}", response_model=SpecialistProfileOut)
async def get_profile(user_id: UUID, session: SessionDep) -> SpecialistProfileOut:
    p = await get_profile_by_user(session, user_id)
    if p is None:
        raise HTTPException(404, "Profile not found")
    return SpecialistProfileOut.model_validate(p)
