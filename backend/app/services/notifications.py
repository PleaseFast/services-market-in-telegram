from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis, notify_channel
from app.models.notification import Notification


class NotificationType:
    NEW_APPLICATION = "new_application"
    APPLICATION_ACCEPTED = "application_accepted"
    APPLICATION_REJECTED = "application_rejected"
    SPECIALIST_SELECTED = "specialist_selected"
    PROJECT_COMPLETED = "project_completed"
    DIRECT_OFFER_RECEIVED = "direct_offer_received"
    DIRECT_OFFER_ANSWERED = "direct_offer_answered"
    NEW_REVIEW = "new_review"


async def notify(
    session: AsyncSession, user_id: UUID, type_: str, payload: dict[str, Any]
) -> Notification:
    n = Notification(user_id=user_id, type=type_, payload=payload)
    session.add(n)
    await session.flush()
    try:
        redis = get_redis()
        await redis.publish(
            notify_channel(str(user_id)),
            json.dumps({"id": str(n.id), "type": type_, "payload": payload}, default=str),
        )
    except Exception:
        # Notifications are best-effort; do not break the parent transaction
        pass
    return n
