from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.models.profile_timeline_item import TimelineKind
from app.schemas.timeline import (
    TimelineItemCreate,
    TimelineItemIn,
    TimelineItemOut,
    TimelineMoveIn,
)
from app.services import timeline as svc

router = APIRouter(prefix="/specialists/me/timeline", tags=["timeline"])


@router.get("", response_model=list[TimelineItemOut])
async def list_my_timeline(
    user: CurrentUser,
    session: SessionDep,
    kind: TimelineKind | None = Query(default=None),
) -> list[TimelineItemOut]:
    items = await svc.list_my_items(session, user, kind=kind)
    return [TimelineItemOut.model_validate(i) for i in items]


@router.post("", response_model=TimelineItemOut, status_code=status.HTTP_201_CREATED)
async def create(
    payload: TimelineItemCreate, user: CurrentUser, session: SessionDep
) -> TimelineItemOut:
    return TimelineItemOut.model_validate(await svc.create_item(session, user, payload))


@router.patch("/{item_id}", response_model=TimelineItemOut)
async def patch(
    item_id: UUID, payload: TimelineItemIn, user: CurrentUser, session: SessionDep
) -> TimelineItemOut:
    return TimelineItemOut.model_validate(await svc.update_item(session, user, item_id, payload))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(item_id: UUID, user: CurrentUser, session: SessionDep) -> None:
    await svc.delete_item(session, user, item_id)


@router.post("/{item_id}/move", response_model=TimelineItemOut)
async def move(
    item_id: UUID, payload: TimelineMoveIn, user: CurrentUser, session: SessionDep
) -> TimelineItemOut:
    return TimelineItemOut.model_validate(
        await svc.move_item(session, user, item_id, payload.direction)
    )
