from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProjectView(Base):
    """Per-specialist view history. Composite PK (project_id, user_id).

    Tracks how many times and when a given specialist opened a given project's
    detail page. Used by the feed's "Viewed first" sort.
    """

    __tablename__ = "project_views"
    __table_args__ = (
        Index("ix_project_views_user_last_viewed", "user_id", "last_viewed_at"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    first_viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
