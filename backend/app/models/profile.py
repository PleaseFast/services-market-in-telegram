from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Timestamps, UUIDPK

if TYPE_CHECKING:
    from app.models.profile_timeline_item import ProfileTimelineItem
    from app.models.specialist_service import SpecialistService
    from app.models.user import User

DEFAULT_AVATAR_ID = "fox:amber"


class SpecialistProfile(UUIDPK, Timestamps, Base):
    __tablename__ = "specialist_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_id: Mapped[str] = mapped_column(
        String(40), nullable=False, default=DEFAULT_AVATAR_ID, server_default=DEFAULT_AVATAR_ID
    )
    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="specialist_profile")
    timeline_items: Mapped[list["ProfileTimelineItem"]] = relationship(
        cascade="all, delete-orphan",
    )
    services: Mapped[list["SpecialistService"]] = relationship(
        cascade="all, delete-orphan",
    )


class CustomerProfile(UUIDPK, Timestamps, Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_id: Mapped[str] = mapped_column(
        String(40), nullable=False, default=DEFAULT_AVATAR_ID, server_default=DEFAULT_AVATAR_ID
    )
    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="customer_profile")
