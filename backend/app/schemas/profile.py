from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.categories import CATEGORIES
from app.schemas.common import ORMBase
from app.schemas.project import CategoryLiteral
from app.schemas.services import SpecialistServiceOut
from app.schemas.timeline import TimelineItemOut


class SpecialistProfileIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=14, le=120)
    categories: list[CategoryLiteral] = Field(min_length=1, max_length=len(CATEGORIES))
    years_experience: int = Field(ge=0, le=80)
    bio: str = Field(default="", max_length=4000)
    avatar_id: str = Field(default="fox:amber", min_length=1, max_length=40)


class SpecialistProfileTimeline(BaseModel):
    work: list[TimelineItemOut] = []
    education: list[TimelineItemOut] = []
    achievement: list[TimelineItemOut] = []


class SpecialistProfileOut(ORMBase):
    id: UUID
    user_id: UUID
    full_name: str
    age: int
    categories: list[str] = []
    years_experience: int
    bio: str
    avatar_id: str
    rating_avg: Decimal
    rating_count: int
    timeline: SpecialistProfileTimeline = SpecialistProfileTimeline()
    services: list[SpecialistServiceOut] = []


class CustomerProfileIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    avatar_id: str = Field(default="fox:amber", min_length=1, max_length=40)


class CustomerProfileOut(ORMBase):
    id: UUID
    user_id: UUID
    display_name: str
    avatar_id: str
    rating_avg: Decimal
    rating_count: int
