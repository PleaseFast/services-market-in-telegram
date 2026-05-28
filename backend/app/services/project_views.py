"""Per-specialist project view tracking.

Best-effort: failures must never break the parent transaction or the detail
endpoint. Uses a portable select-then-insert-or-update pattern that works on
both PostgreSQL (prod) and SQLite (tests).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_view import ProjectView

logger = logging.getLogger(__name__)


async def record_view(session: AsyncSession, project_id: UUID, user_id: UUID) -> None:
    """Record (or refresh) that ``user_id`` opened ``project_id``.

    Increments ``view_count`` and sets ``last_viewed_at`` to now. Swallows
    exceptions so a view never breaks an enclosing request.
    """
    try:
        now = datetime.now(timezone.utc)
        existing = await session.scalar(
            select(ProjectView).where(
                ProjectView.project_id == project_id,
                ProjectView.user_id == user_id,
            )
        )
        if existing is None:
            session.add(
                ProjectView(
                    project_id=project_id,
                    user_id=user_id,
                    view_count=1,
                    first_viewed_at=now,
                    last_viewed_at=now,
                )
            )
        else:
            existing.view_count = (existing.view_count or 0) + 1
            existing.last_viewed_at = now
        await session.commit()
    except Exception:  # noqa: BLE001 — best-effort
        logger.exception("Failed to record project view")
        try:
            await session.rollback()
        except Exception:  # noqa: BLE001
            pass
