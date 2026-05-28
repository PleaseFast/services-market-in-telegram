from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.deps import CurrentUser, SessionDep
from app.repositories.services import list_catalog, list_for_profile
from app.repositories.specialists import get_profile_by_user
from app.schemas.services import (
    ServiceCatalogOut,
    SpecialistServiceOut,
    SpecialistServicesReplace,
)
from app.services import specialist_services as svc

router = APIRouter(tags=["services"])


@router.get("/services/catalog", response_model=list[ServiceCatalogOut])
async def get_catalog(session: SessionDep) -> list[ServiceCatalogOut]:
    items = await list_catalog(session)
    return [ServiceCatalogOut.model_validate(i) for i in items]


@router.get("/specialists/{user_id}/services", response_model=list[SpecialistServiceOut])
async def get_specialist_services(
    user_id: UUID, session: SessionDep
) -> list[SpecialistServiceOut]:
    profile = await get_profile_by_user(session, user_id)
    if profile is None:
        raise HTTPException(404, "Profile not found")
    return await list_for_profile(session, profile.id)


@router.put("/specialists/me/services", status_code=204)
async def put_my_services(
    payload: SpecialistServicesReplace, user: CurrentUser, session: SessionDep
) -> None:
    await svc.replace_services(session, user, payload)
