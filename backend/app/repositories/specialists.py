from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import SpecialistProfile


async def get_profile_by_user(session: AsyncSession, user_id: UUID) -> SpecialistProfile | None:
    res = await session.execute(
        select(SpecialistProfile)
        .options(selectinload(SpecialistProfile.timeline_items))
        .where(SpecialistProfile.user_id == user_id)
    )
    return res.scalar_one_or_none()


async def get_profiles_by_user_ids(
    session: AsyncSession, user_ids: list[UUID]
) -> dict[UUID, SpecialistProfile]:
    if not user_ids:
        return {}
    res = await session.execute(
        select(SpecialistProfile).where(SpecialistProfile.user_id.in_(user_ids))
    )
    return {p.user_id: p for p in res.scalars().all()}


async def search_specialists(
    session: AsyncSession,
    *,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[SpecialistProfile], int]:
    stmt = select(SpecialistProfile).options(
        selectinload(SpecialistProfile.timeline_items)
    )
    if category:
        stmt = stmt.where(SpecialistProfile.category.ilike(f"%{category}%"))
    total = await session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    res = await session.execute(
        stmt.order_by(desc(SpecialistProfile.rating_avg)).limit(limit).offset(offset)
    )
    return list(res.scalars().all()), int(total or 0)
