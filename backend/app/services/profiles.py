from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.categories import clamp_category
from app.models.profile import (
    CustomerProfile,
    SpecialistProfile,
    SpecialistProfileCategory,
)
from app.models.user import User, UserRole
from app.repositories.specialists import get_profile_by_user
from app.schemas.profile import CustomerProfileIn, SpecialistProfileIn
from app.services.errors import ConflictError, ForbiddenError


def _normalise_categories(raw: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in raw:
        clamped = clamp_category(value)
        if clamped not in seen:
            seen.add(clamped)
            out.append(clamped)
    return out


async def _replace_categories(
    session: AsyncSession, profile_id, categories: list[str]
) -> None:
    """Delete-and-insert the join rows without going through the ORM
    collection — touching ``profile.category_rows`` directly would trigger a
    sync lazy load on the just-flushed instance and trip MissingGreenlet in
    async land."""
    await session.execute(
        delete(SpecialistProfileCategory).where(
            SpecialistProfileCategory.specialist_profile_id == profile_id
        )
    )
    for c in categories:
        session.add(
            SpecialistProfileCategory(specialist_profile_id=profile_id, category=c)
        )


async def upsert_specialist_profile(
    session: AsyncSession, user: User, data: SpecialistProfileIn
) -> SpecialistProfile:
    if user.role != UserRole.SPECIALIST:
        raise ForbiddenError(
            "profiles.specialist_only",
            message="Only specialists can manage a specialist profile",
        )

    categories = _normalise_categories(data.categories)
    if not categories:
        raise ConflictError(
            "profiles.category_required", message="At least one category is required"
        )

    profile = await get_profile_by_user(session, user.id)
    if profile is None:
        profile = SpecialistProfile(
            user_id=user.id,
            full_name=data.full_name,
            age=data.age,
            years_experience=data.years_experience,
            bio=data.bio,
            avatar_id=data.avatar_id,
        )
        session.add(profile)
        await session.flush()  # need profile.id for the FK rows
    else:
        profile.full_name = data.full_name
        profile.age = data.age
        profile.years_experience = data.years_experience
        profile.bio = data.bio
        profile.avatar_id = data.avatar_id

    await _replace_categories(session, profile.id, categories)

    await session.commit()
    return await get_profile_by_user(session, user.id)  # type: ignore[return-value]


async def upsert_customer_profile(
    session: AsyncSession, user: User, data: CustomerProfileIn
) -> CustomerProfile:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenError(
            "profiles.customer_only",
            message="Only customers can manage a customer profile",
        )
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
        raise ConflictError(
            "profiles.no_specialist_profile", message="Specialist profile not created"
        )
    return p
