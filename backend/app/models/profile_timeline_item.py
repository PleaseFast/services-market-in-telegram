from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, SmallInteger, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, Timestamps, UUIDPK


class TimelineKind(str, enum.Enum):
    WORK = "work"
    EDUCATION = "education"
    ACHIEVEMENT = "achievement"


class ProfileTimelineItem(UUIDPK, Timestamps, Base):
    """Unified timeline entry on a specialist profile.

    Replaces the previous ``SpecialistWorkplace`` and ``SpecialistPortfolioLink``
    tables with a single normalized shape (work / education / achievement).
    """

    __tablename__ = "profile_timeline_items"
    __table_args__ = (
        Index(
            "ix_profile_timeline_items_profile_kind_position",
            "profile_id",
            "kind",
            "position",
        ),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[TimelineKind] = mapped_column(
        Enum(
            TimelineKind,
            name="timeline_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    start_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
