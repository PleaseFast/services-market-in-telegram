from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import SpecialistProfile, SpecialistProfileCategory


def _with_categories():
    return (
        selectinload(SpecialistProfile.timeline_items),
        selectinload(SpecialistProfile.category_rows),
    )


async def get_profile_by_user(session: AsyncSession, user_id: UUID) -> SpecialistProfile | None:
    res = await session.execute(
        select(SpecialistProfile)
        .options(*_with_categories())
        .where(SpecialistProfile.user_id == user_id)
    )
    return res.scalar_one_or_none()


async def get_profiles_by_user_ids(
    session: AsyncSession, user_ids: list[UUID]
) -> dict[UUID, SpecialistProfile]:
    if not user_ids:
        return {}
    res = await session.execute(
        select(SpecialistProfile)
        .options(selectinload(SpecialistProfile.category_rows))
        .where(SpecialistProfile.user_id.in_(user_ids))
    )
    return {p.user_id: p for p in res.scalars().all()}


async def has_profile_for_user(session: AsyncSession, user_id: UUID) -> bool:
    res = await session.execute(
        select(func.count()).select_from(SpecialistProfile).where(
            SpecialistProfile.user_id == user_id
        )
    )
    return bool((res.scalar() or 0) > 0)


async def search_specialists(
    session: AsyncSession,
    *,
    category: str | None = None,
    min_rating: Decimal | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[SpecialistProfile], int]:
    stmt = select(SpecialistProfile).options(*_with_categories())
    if category:
        stmt = stmt.where(
            SpecialistProfile.category_rows.any(
                SpecialistProfileCategory.category == category
            )
        )
    if min_rating is not None:
        stmt = stmt.where(SpecialistProfile.rating_avg >= min_rating)
    total = await session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    res = await session.execute(
        stmt.order_by(desc(SpecialistProfile.rating_avg)).limit(limit).offset(offset)
    )
    return list(res.scalars().all()), int(total or 0)
