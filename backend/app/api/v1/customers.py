from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import CurrentUser, SessionDep
from app.models.profile import CustomerProfile
from app.schemas.profile import CustomerProfileIn, CustomerProfileOut
from app.services.profiles import upsert_customer_profile

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/me", response_model=CustomerProfileOut)
async def get_my_profile(user: CurrentUser) -> CustomerProfileOut:
    if user.customer_profile is None:
        raise HTTPException(404, "Profile not found")
    return CustomerProfileOut.model_validate(user.customer_profile)


@router.put("/me", response_model=CustomerProfileOut)
async def put_my_profile(
    payload: CustomerProfileIn, user: CurrentUser, session: SessionDep
) -> CustomerProfileOut:
    p = await upsert_customer_profile(session, user, payload)
    return CustomerProfileOut.model_validate(p)


@router.get("/{user_id}", response_model=CustomerProfileOut)
async def get_profile(user_id: UUID, session: SessionDep) -> CustomerProfileOut:
    res = await session.execute(select(CustomerProfile).where(CustomerProfile.user_id == user_id))
    p = res.scalar_one_or_none()
    if p is None:
        raise HTTPException(404, "Profile not found")
    return CustomerProfileOut.model_validate(p)
