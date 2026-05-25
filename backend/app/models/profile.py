from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Timestamps, UUIDPK

if TYPE_CHECKING:
    from app.models.user import User


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
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="specialist_profile")
    workplaces: Mapped[list["SpecialistWorkplace"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    portfolio_links: Mapped[list["SpecialistPortfolioLink"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class SpecialistWorkplace(UUIDPK, Timestamps, Base):
    __tablename__ = "specialist_workplaces"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    company: Mapped[str] = mapped_column(String(120), nullable=False)
    period: Mapped[str | None] = mapped_column(String(60), nullable=True)

    profile: Mapped[SpecialistProfile] = relationship(back_populates="workplaces")


class SpecialistPortfolioLink(UUIDPK, Timestamps, Base):
    __tablename__ = "specialist_portfolio_links"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)

    profile: Mapped[SpecialistProfile] = relationship(back_populates="portfolio_links")


class CustomerProfile(UUIDPK, Timestamps, Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="customer_profile")
