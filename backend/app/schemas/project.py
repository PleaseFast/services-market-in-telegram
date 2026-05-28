from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.categories import CATEGORIES
from app.models.project import ProjectStatus
from app.schemas.common import ORMBase

CategoryLiteral = Literal[
    "Frontend",
    "Backend",
    "Bots",
    "Mobile",
    "DevOps",
    "Data",
    "Design",
    "AI",
    "Other",
]

# Compile-time sanity check that the Literal matches the runtime tuple.
assert set(CATEGORIES) == set(CategoryLiteral.__args__)  # type: ignore[attr-defined]


class ProjectTemplateOut(ORMBase):
    id: UUID
    title: str
    category: str
    description_template: str


class ProjectIn(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    description: str = Field(default="", max_length=8000)
    budget: Decimal = Field(default=Decimal(0), ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    deadline: date | None = None
    template_id: UUID | None = None
    category: CategoryLiteral | None = None
    publish: bool = False


class ProjectPatch(BaseModel):
    title: str | None = Field(default=None, min_length=4, max_length=200)
    description: str | None = Field(default=None, max_length=8000)
    budget: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    deadline: date | None = None
    category: CategoryLiteral | None = None


class ProjectOut(ORMBase):
    id: UUID
    customer_id: UUID
    title: str
    description: str
    budget: Decimal
    currency: str
    deadline: date | None
    status: ProjectStatus
    category: str
    selected_specialist_id: UUID | None
    template_id: UUID | None
    created_at: datetime
    updated_at: datetime
