from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.deps import CurrentUser, SessionDep
from app.models.profile import SpecialistProfile
from app.models.profile_timeline_item import TimelineKind
from app.repositories.services import list_for_profile, list_for_profiles
from app.repositories.specialists import get_profile_by_user, search_specialists
from app.schemas.common import Page
from app.schemas.profile import (
    SpecialistProfileIn,
    SpecialistProfileOut,
    SpecialistProfileTimeline,
)
from app.schemas.project import CategoryLiteral
from app.schemas.services import SpecialistServiceOut
from app.schemas.timeline import TimelineItemOut
from app.services.profiles import upsert_specialist_profile

router = APIRouter(prefix="/specialists", tags=["specialists"])


def _group_timeline(profile: SpecialistProfile) -> SpecialistProfileTimeline:
    """Split the flat timeline_items relationship into work/education/achievement."""
    grouped: dict[TimelineKind, list[TimelineItemOut]] = {
        TimelineKind.WORK: [],
        TimelineKind.EDUCATION: [],
        TimelineKind.ACHIEVEMENT: [],
    }
    items = sorted(
        profile.timeline_items or [],
        key=lambda i: (i.kind.value, i.position, i.created_at),
    )
    for item in items:
        grouped[item.kind].append(TimelineItemOut.model_validate(item))
    return SpecialistProfileTimeline(
        work=grouped[TimelineKind.WORK],
        education=grouped[TimelineKind.EDUCATION],
        achievement=grouped[TimelineKind.ACHIEVEMENT],
    )


def _hydrate(
    profile: SpecialistProfile, services: list[SpecialistServiceOut]
) -> SpecialistProfileOut:
    # Build by-field to avoid touching `profile.services` — that's an unloaded
    # SQLAlchemy relationship in async land, and Pydantic's model_validate would
    # trigger a lazy load (MissingGreenlet). The hydrated `services` list is
    # passed in by the caller; `timeline_items` is selectinload-ed elsewhere.
    return SpecialistProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        categories=profile.categories,
        years_experience=profile.years_experience,
        bio=profile.bio,
        avatar_id=profile.avatar_id,
        rating_avg=profile.rating_avg,
        rating_count=profile.rating_count,
        timeline=_group_timeline(profile),
        services=services,
    )


@router.get("", response_model=Page[SpecialistProfileOut])
async def list_specialists(
    session: SessionDep,
    category: CategoryLiteral | None = Query(default=None),
    min_rating: Decimal | None = Query(default=None, ge=0, le=5),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[SpecialistProfileOut]:
    items, total = await search_specialists(
        session,
        category=category,
        min_rating=min_rating,
        limit=limit,
        offset=offset,
    )
    services_map = await list_for_profiles(session, [p.id for p in items])
    return Page(
        items=[_hydrate(p, services_map.get(p.id, [])) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=SpecialistProfileOut)
async def get_my_profile(user: CurrentUser, session: SessionDep) -> SpecialistProfileOut:
    p = await get_profile_by_user(session, user.id)
    if p is None:
        raise HTTPException(404, "Profile not found")
    services = await list_for_profile(session, p.id)
    return _hydrate(p, services)


@router.put("/me", response_model=SpecialistProfileOut)
async def put_my_profile(
    payload: SpecialistProfileIn, user: CurrentUser, session: SessionDep
) -> SpecialistProfileOut:
    p = await upsert_specialist_profile(session, user, payload)
    services = await list_for_profile(session, p.id)
    return _hydrate(p, services)


@router.get("/{user_id}", response_model=SpecialistProfileOut)
async def get_profile(user_id: UUID, session: SessionDep) -> SpecialistProfileOut:
    p = await get_profile_by_user(session, user_id)
    if p is None:
        raise HTTPException(404, "Profile not found")
    services = await list_for_profile(session, p.id)
    return _hydrate(p, services)
