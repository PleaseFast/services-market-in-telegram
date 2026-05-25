from uuid import UUID

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.schemas.application import (
    ApplicationIn,
    ApplicationOut,
    DirectOfferIn,
    DirectOfferOut,
)
from app.services import applications as svc

router = APIRouter(tags=["applications"])


@router.post("/projects/{project_id}/applications", response_model=ApplicationOut, status_code=201)
async def apply(
    project_id: UUID,
    payload: ApplicationIn,
    user: CurrentUser,
    session: SessionDep,
) -> ApplicationOut:
    a = await svc.apply(session, user, project_id, payload.cover_letter)
    return ApplicationOut.model_validate(a)


@router.get("/projects/{project_id}/applications", response_model=list[ApplicationOut])
async def list_applicants(
    project_id: UUID, user: CurrentUser, session: SessionDep
) -> list[ApplicationOut]:
    items = await svc.list_for_project(session, user, project_id)
    return [ApplicationOut.model_validate(i) for i in items]


@router.post("/applications/{application_id}/withdraw", response_model=ApplicationOut)
async def withdraw(application_id: UUID, user: CurrentUser, session: SessionDep) -> ApplicationOut:
    a = await svc.withdraw(session, user, application_id)
    return ApplicationOut.model_validate(a)


@router.post("/projects/{project_id}/direct-offers", response_model=DirectOfferOut, status_code=201)
async def offer(
    project_id: UUID,
    payload: DirectOfferIn,
    user: CurrentUser,
    session: SessionDep,
) -> DirectOfferOut:
    o = await svc.create_offer(session, user, project_id, payload.specialist_id, payload.message)
    return DirectOfferOut.model_validate(o)


@router.post("/direct-offers/{offer_id}/accept", response_model=DirectOfferOut)
async def accept_offer(offer_id: UUID, user: CurrentUser, session: SessionDep) -> DirectOfferOut:
    return DirectOfferOut.model_validate(await svc.respond_to_offer(session, user, offer_id, True))


@router.post("/direct-offers/{offer_id}/reject", response_model=DirectOfferOut)
async def reject_offer(offer_id: UUID, user: CurrentUser, session: SessionDep) -> DirectOfferOut:
    return DirectOfferOut.model_validate(await svc.respond_to_offer(session, user, offer_id, False))
