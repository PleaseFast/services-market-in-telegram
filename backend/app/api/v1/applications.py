from uuid import UUID

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.models.application import Application
from app.repositories.specialists import get_profiles_by_user_ids
from app.schemas.application import (
    ApplicationIn,
    ApplicationOut,
    DirectOfferIn,
    DirectOfferOut,
    SpecialistPreview,
)
from app.services import applications as svc

router = APIRouter(tags=["applications"])


def _preview(profile) -> SpecialistPreview | None:
    if profile is None:
        return None
    return SpecialistPreview(
        user_id=profile.user_id,
        full_name=profile.full_name,
        avatar_id=profile.avatar_id,
        categories=profile.categories,
        rating_avg=float(profile.rating_avg or 0),
        rating_count=profile.rating_count or 0,
    )


def _to_application_out(a: Application, profile) -> ApplicationOut:
    return ApplicationOut(
        id=a.id,
        project_id=a.project_id,
        specialist_id=a.specialist_id,
        cover_letter=a.cover_letter,
        status=a.status,
        created_at=a.created_at,
        specialist=_preview(profile),
    )


@router.post("/projects/{project_id}/applications", response_model=ApplicationOut, status_code=201)
async def apply(
    project_id: UUID,
    payload: ApplicationIn,
    user: CurrentUser,
    session: SessionDep,
) -> ApplicationOut:
    a = await svc.apply(session, user, project_id, payload.cover_letter)
    profiles = await get_profiles_by_user_ids(session, [a.specialist_id])
    return _to_application_out(a, profiles.get(a.specialist_id))


@router.get("/projects/{project_id}/applications", response_model=list[ApplicationOut])
async def list_applicants(
    project_id: UUID, user: CurrentUser, session: SessionDep
) -> list[ApplicationOut]:
    items = await svc.list_for_project(session, user, project_id)
    profiles = await get_profiles_by_user_ids(session, [a.specialist_id for a in items])
    return [_to_application_out(a, profiles.get(a.specialist_id)) for a in items]


@router.post("/applications/{application_id}/withdraw", response_model=ApplicationOut)
async def withdraw(application_id: UUID, user: CurrentUser, session: SessionDep) -> ApplicationOut:
    a = await svc.withdraw(session, user, application_id)
    profiles = await get_profiles_by_user_ids(session, [a.specialist_id])
    return _to_application_out(a, profiles.get(a.specialist_id))


@router.post("/projects/{project_id}/direct-offers", response_model=DirectOfferOut, status_code=201)
async def offer(
    project_id: UUID,
    payload: DirectOfferIn,
    user: CurrentUser,
    session: SessionDep,
) -> DirectOfferOut:
    o = await svc.create_offer(session, user, project_id, payload.specialist_id, payload.message)
    profiles = await get_profiles_by_user_ids(session, [o.specialist_id])
    profile = profiles.get(o.specialist_id)
    return DirectOfferOut(
        id=o.id,
        project_id=o.project_id,
        specialist_id=o.specialist_id,
        message=o.message,
        status=o.status,
        created_at=o.created_at,
        specialist=_preview(profile),
    )


@router.post("/direct-offers/{offer_id}/accept", response_model=DirectOfferOut)
async def accept_offer(offer_id: UUID, user: CurrentUser, session: SessionDep) -> DirectOfferOut:
    o = await svc.respond_to_offer(session, user, offer_id, True)
    profiles = await get_profiles_by_user_ids(session, [o.specialist_id])
    profile = profiles.get(o.specialist_id)
    return DirectOfferOut(
        id=o.id,
        project_id=o.project_id,
        specialist_id=o.specialist_id,
        message=o.message,
        status=o.status,
        created_at=o.created_at,
        specialist=_preview(profile),
    )


@router.post("/direct-offers/{offer_id}/reject", response_model=DirectOfferOut)
async def reject_offer(offer_id: UUID, user: CurrentUser, session: SessionDep) -> DirectOfferOut:
    o = await svc.respond_to_offer(session, user, offer_id, False)
    profiles = await get_profiles_by_user_ids(session, [o.specialist_id])
    profile = profiles.get(o.specialist_id)
    return DirectOfferOut(
        id=o.id,
        project_id=o.project_id,
        specialist_id=o.specialist_id,
        message=o.message,
        status=o.status,
        created_at=o.created_at,
        specialist=_preview(profile),
    )
