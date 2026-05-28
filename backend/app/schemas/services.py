from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ServiceCatalogOut(ORMBase):
    id: UUID
    slug: str
    category: str
    subcategory: str
    label: str
    position: int


class SpecialistServiceIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120)
    price_amount: Decimal = Field(default=Decimal(0), ge=0)
    price_currency: str = Field(default="USD", min_length=3, max_length=3)


class SpecialistServicesReplace(BaseModel):
    items: list[SpecialistServiceIn] = Field(default_factory=list)


class SpecialistServiceOut(BaseModel):
    """Public hydrated form — joined with the catalog row."""

    service_id: UUID
    slug: str
    category: str
    subcategory: str
    label: str
    price_amount: Decimal
    price_currency: str
    position: int

    model_config = {"from_attributes": True}
