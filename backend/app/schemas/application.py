from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.application import ApplicationStatus
from app.schemas.common import ORMBase


class ApplicationIn(BaseModel):
    cover_letter: str | None = Field(default=None, max_length=4000)


class ApplicationOut(ORMBase):
    id: UUID
    project_id: UUID
    specialist_id: UUID
    cover_letter: str | None
    status: ApplicationStatus
    created_at: datetime


class DirectOfferIn(BaseModel):
    specialist_id: UUID
    message: str | None = Field(default=None, max_length=2000)


class DirectOfferOut(ORMBase):
    id: UUID
    project_id: UUID
    specialist_id: UUID
    message: str | None
    status: ApplicationStatus
    created_at: datetime
