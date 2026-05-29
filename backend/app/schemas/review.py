from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReviewIn(BaseModel):
    rating: float = Field(ge=0, le=5)
    text: str | None = Field(default=None, max_length=4000)

    @field_validator("rating")
    @classmethod
    def half_step(cls, v: float) -> float:
        doubled = v * 2
        if abs(doubled - round(doubled)) > 1e-9:
            raise ValueError("rating must be a multiple of 0.5")
        return round(doubled) / 2.0


class ReviewOut(BaseModel):
    """Hydrated review row used for both create and list responses."""

    id: UUID
    project_id: UUID
    project_title: str
    author_id: UUID
    author_name: str
    subject_id: UUID
    rating: float
    text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
