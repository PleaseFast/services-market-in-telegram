from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile_timeline_item import ProfileTimelineItem, TimelineKind


async def list_items(
    session: AsyncSession, profile_id: UUID, *, kind: TimelineKind | None = None
) -> list[ProfileTimelineItem]:
    stmt = select(ProfileTimelineItem).where(ProfileTimelineItem.profile_id == profile_id)
    if kind is not None:
        stmt = stmt.where(ProfileTimelineItem.kind == kind)
    stmt = stmt.order_by(
        asc(ProfileTimelineItem.kind),
        asc(ProfileTimelineItem.position),
        asc(ProfileTimelineItem.created_at),
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_item(session: AsyncSession, item_id: UUID) -> ProfileTimelineItem | None:
    return await session.get(ProfileTimelineItem, item_id)


async def next_position(session: AsyncSession, profile_id: UUID, kind: TimelineKind) -> int:
    # ``res or -1`` would be wrong here because 0 is falsy — explicitly compare
    # to None so position 0 doesn't get coerced to -1.
    res = await session.scalar(
        select(func.coalesce(func.max(ProfileTimelineItem.position), -1)).where(
            ProfileTimelineItem.profile_id == profile_id,
            ProfileTimelineItem.kind == kind,
        )
    )
    return (int(res) if res is not None else -1) + 1


async def find_neighbor(
    session: AsyncSession,
    *,
    profile_id: UUID,
    kind: TimelineKind,
    target_position: int,
) -> ProfileTimelineItem | None:
    res = await session.execute(
        select(ProfileTimelineItem).where(
            ProfileTimelineItem.profile_id == profile_id,
            ProfileTimelineItem.kind == kind,
            ProfileTimelineItem.position == target_position,
        )
    )
    return res.scalar_one_or_none()
