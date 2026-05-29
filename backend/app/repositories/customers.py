from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import CustomerProfile


async def has_profile_for_user(session: AsyncSession, user_id: UUID) -> bool:
    res = await session.execute(
        select(func.count())
        .select_from(CustomerProfile)
        .where(CustomerProfile.user_id == user_id)
    )
    return bool((res.scalar() or 0) > 0)
