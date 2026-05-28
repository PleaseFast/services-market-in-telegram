from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import CustomerProfile, SpecialistProfile
from app.models.user import User, UserRole
from app.repositories.specialists import get_profile_by_user
from app.schemas.profile import CustomerProfileIn, SpecialistProfileIn
from app.services.errors import ConflictError, ForbiddenError


async def upsert_specialist_profile(
    session: AsyncSession, user: User, data: SpecialistProfileIn
) -> SpecialistProfile:
    if user.role != UserRole.SPECIALIST:
        raise ForbiddenError("Only specialists can manage a specialist profile")

    profile = await get_profile_by_user(session, user.id)
    if profile is None:
        profile = SpecialistProfile(
            user_id=user.id,
            full_name=data.full_name,
            age=data.age,
            category=data.category,
            years_experience=data.years_experience,
            bio=data.bio,
            avatar_id=data.avatar_id,
        )
        session.add(profile)
    else:
        profile.full_name = data.full_name
        profile.age = data.age
        profile.category = data.category
        profile.years_experience = data.years_experience
        profile.bio = data.bio
        profile.avatar_id = data.avatar_id

    await session.commit()
    return await get_profile_by_user(session, user.id)  # type: ignore[return-value]


async def upsert_customer_profile(
    session: AsyncSession, user: User, data: CustomerProfileIn
) -> CustomerProfile:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenError("Only customers can manage a customer profile")
    profile = user.customer_profile
    if profile is None:
        profile = CustomerProfile(
            user_id=user.id, display_name=data.display_name, avatar_id=data.avatar_id
        )
        session.add(profile)
    else:
        profile.display_name = data.display_name
        profile.avatar_id = data.avatar_id
    await session.commit()
    return profile


async def delete_user(session: AsyncSession, user: User) -> None:
    # Soft delete to preserve referential history
    from datetime import UTC, datetime

    user.is_active = False
    user.deleted_at = datetime.now(UTC)
    user.email = None  # free the email
    await session.commit()


async def get_profile_or_error(session: AsyncSession, user_id) -> SpecialistProfile:
    p = await get_profile_by_user(session, user_id)
    if p is None:
        raise ConflictError("Specialist profile not created")
    return p
