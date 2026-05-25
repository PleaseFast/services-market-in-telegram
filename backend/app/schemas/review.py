from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=4000)


class ReviewOut(ORMBase):
    id: UUID
    project_id: UUID
    author_id: UUID
    subject_id: UUID
    rating: int
    text: str | None
    created_at: datetime
