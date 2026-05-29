from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Timestamps, UUIDPK


class Review(UUIDPK, Timestamps, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("project_id", "author_id", name="uq_review_project_author"),
        CheckConstraint("rating_half BETWEEN 0 AND 10", name="ck_review_rating_half_range"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Rating stored as half-stars in 0..10 so a CHECK constraint can enforce
    # the 0.5 step without floating-point comparisons. API layer converts to
    # a float 0.0..5.0.
    rating_half: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="reviews")

    @property
    def rating(self) -> float:
        return self.rating_half / 2.0
