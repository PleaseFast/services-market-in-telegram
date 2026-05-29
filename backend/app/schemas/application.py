from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.application import ApplicationStatus


class ApplicationIn(BaseModel):
    cover_letter: str | None = Field(default=None, max_length=4000)


class SpecialistPreview(BaseModel):
    """Minimal preview of a specialist, embedded into ApplicationOut and DirectOfferOut.

    Lets the customer-facing UI render avatar + name + categories next to each
    applicant without a separate fetch per row.
    """

    user_id: UUID
    full_name: str
    avatar_id: str
    categories: list[str] = []
    rating_avg: float = 0.0
    rating_count: int = 0


class ApplicationOut(BaseModel):
    id: UUID
    project_id: UUID
    specialist_id: UUID
    cover_letter: str | None
    status: ApplicationStatus
    created_at: datetime
    specialist: SpecialistPreview | None = None

    model_config = {"from_attributes": True}


class DirectOfferIn(BaseModel):
    specialist_id: UUID
    message: str | None = Field(default=None, max_length=2000)


class DirectOfferOut(BaseModel):
    id: UUID
    project_id: UUID
    specialist_id: UUID
    message: str | None
    status: ApplicationStatus
    created_at: datetime
    specialist: SpecialistPreview | None = None

    model_config = {"from_attributes": True}
