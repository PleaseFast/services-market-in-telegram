from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import ORMBase


class WorkplaceIn(BaseModel):
    title: str = Field(max_length=120)
    company: str = Field(max_length=120)
    period: str | None = Field(default=None, max_length=60)


class WorkplaceOut(ORMBase):
    id: UUID
    title: str
    company: str
    period: str | None


class PortfolioLinkIn(BaseModel):
    url: HttpUrl
    label: str | None = Field(default=None, max_length=120)


class PortfolioLinkOut(ORMBase):
    id: UUID
    url: str
    label: str | None


class SpecialistProfileIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=14, le=120)
    category: str = Field(min_length=2, max_length=80)
    years_experience: int = Field(ge=0, le=80)
    bio: str = Field(default="", max_length=4000)
    avatar_url: str | None = Field(default=None, max_length=500)
    workplaces: list[WorkplaceIn] = Field(default_factory=list)
    portfolio_links: list[PortfolioLinkIn] = Field(default_factory=list)


class SpecialistProfileOut(ORMBase):
    id: UUID
    user_id: UUID
    full_name: str
    age: int
    category: str
    years_experience: int
    bio: str
    avatar_url: str | None
    rating_avg: Decimal
    rating_count: int
    workplaces: list[WorkplaceOut] = []
    portfolio_links: list[PortfolioLinkOut] = []


class CustomerProfileIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=500)


class CustomerProfileOut(ORMBase):
    id: UUID
    user_id: UUID
    display_name: str
    avatar_url: str | None
    rating_avg: Decimal
    rating_count: int
