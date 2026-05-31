from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import CurrentUser, SessionDep
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.services.errors import NotFoundError

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(user: CurrentUser, session: SessionDep) -> list[NotificationOut]:
    res = await session.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
    )
    return [NotificationOut.model_validate(n) for n in res.scalars().all()]


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(
    notification_id: UUID, user: CurrentUser, session: SessionDep
) -> NotificationOut:
    n = await session.get(Notification, notification_id)
    if n is None or n.user_id != user.id:
        raise NotFoundError("notifications.not_found", message="Not found")
    if n.read_at is None:
        n.read_at = datetime.now(UTC)
        await session.commit()
    return NotificationOut.model_validate(n)
