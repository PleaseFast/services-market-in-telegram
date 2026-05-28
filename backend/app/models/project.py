from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDelete, Timestamps, UUIDPK


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELED = "canceled"


class ProjectTemplate(UUIDPK, Timestamps, Base):
    __tablename__ = "project_templates"

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description_template: Mapped[str] = mapped_column(Text, nullable=False, default="")


class Project(UUIDPK, Timestamps, SoftDelete, Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_status_created_at", "status", "created_at"),
        Index("ix_projects_selected_specialist", "selected_specialist_id"),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("project_templates.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    category: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default="Other", default="Other", index=True
    )

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=ProjectStatus.DRAFT,
    )
    selected_specialist_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    template: Mapped[ProjectTemplate | None] = relationship()
    applications = relationship("Application", back_populates="project", cascade="all, delete-orphan")
    direct_offers = relationship("DirectOffer", back_populates="project", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")
    chat_threads = relationship("ChatThread", back_populates="project", cascade="all, delete-orphan")
