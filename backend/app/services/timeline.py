from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile_timeline_item import ProfileTimelineItem, TimelineKind
from app.models.user import User, UserRole
from app.repositories.specialists import get_profile_by_user
from app.repositories.timeline import find_neighbor, get_item, list_items, next_position
from app.schemas.timeline import TimelineItemCreate, TimelineItemIn
from app.services.errors import ConflictError, ForbiddenError, NotFoundError


async def _ensure_specialist_profile(session: AsyncSession, user: User):
    if user.role != UserRole.SPECIALIST:
        raise ForbiddenError("Only specialists have a timeline")
    profile = await get_profile_by_user(session, user.id)
    if profile is None:
        raise ConflictError("Create your specialist profile first")
    return profile


async def list_my_items(
    session: AsyncSession, user: User, *, kind: TimelineKind | None = None
) -> list[ProfileTimelineItem]:
    profile = await _ensure_specialist_profile(session, user)
    return await list_items(session, profile.id, kind=kind)


async def create_item(
    session: AsyncSession, user: User, data: TimelineItemCreate
) -> ProfileTimelineItem:
    profile = await _ensure_specialist_profile(session, user)
    kind = TimelineKind(data.kind)
    pos = await next_position(session, profile.id, kind)
    item = ProfileTimelineItem(
        profile_id=profile.id,
        kind=kind,
        title=data.title,
        description=data.description,
        start_year=data.start_year,
        end_year=data.end_year if not data.is_current else None,
        is_current=data.is_current,
        position=pos,
    )
    session.add(item)
    await session.commit()
    return item


async def update_item(
    session: AsyncSession, user: User, item_id: UUID, data: TimelineItemIn
) -> ProfileTimelineItem:
    profile = await _ensure_specialist_profile(session, user)
    item = await get_item(session, item_id)
    if item is None or item.profile_id != profile.id:
        raise NotFoundError("Timeline item not found")
    payload = data.model_dump(exclude_unset=True)
    # Apply each field that was explicitly sent.
    for field in ("title", "description", "start_year", "is_current"):
        if field in payload:
            setattr(item, field, payload[field])
    if "kind" in payload:
        item.kind = TimelineKind(payload["kind"])
    if "end_year" in payload:
        item.end_year = payload["end_year"]
    # Normalize: if currently set, end_year must be null.
    if item.is_current:
        item.end_year = None
    else:
        if item.end_year is None:
            raise ConflictError("end_year is required when is_current is false")
        if item.end_year < item.start_year:
            raise ConflictError("end_year must be >= start_year")
    await session.commit()
    return item


async def delete_item(session: AsyncSession, user: User, item_id: UUID) -> None:
    profile = await _ensure_specialist_profile(session, user)
    item = await get_item(session, item_id)
    if item is None or item.profile_id != profile.id:
        raise NotFoundError("Timeline item not found")
    await session.delete(item)
    await session.commit()


async def move_item(
    session: AsyncSession,
    user: User,
    item_id: UUID,
    direction: Literal["up", "down"],
) -> ProfileTimelineItem:
    """Swap the item's position with its same-kind neighbor."""
    profile = await _ensure_specialist_profile(session, user)
    item = await get_item(session, item_id)
    if item is None or item.profile_id != profile.id:
        raise NotFoundError("Timeline item not found")
    target_pos = item.position - 1 if direction == "up" else item.position + 1
    if target_pos < 0:
        return item  # already at top; no-op
    neighbor = await find_neighbor(
        session, profile_id=profile.id, kind=item.kind, target_position=target_pos
    )
    if neighbor is None:
        return item  # no neighbor in that direction
    # Swap with explicit UPDATEs to avoid any subtlety with ORM dirty-tracking
    # of two same-class instances being updated in one flush.
    item_id = item.id
    neighbor_id = neighbor.id
    item_pos = item.position
    neighbor_pos = neighbor.position
    await session.execute(
        update(ProfileTimelineItem)
        .where(ProfileTimelineItem.id == item_id)
        .values(position=neighbor_pos)
    )
    await session.execute(
        update(ProfileTimelineItem)
        .where(ProfileTimelineItem.id == neighbor_id)
        .values(position=item_pos)
    )
    await session.commit()
    await session.refresh(item)
    return item
