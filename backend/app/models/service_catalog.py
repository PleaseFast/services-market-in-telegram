from __future__ import annotations

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, Timestamps, UUIDPK


class ServiceCatalogItem(UUIDPK, Timestamps, Base):
    """Predefined service offered on the marketplace.

    Seeded from ``app.core.service_catalog.SERVICE_CATALOG``. The ``slug`` is
    the canonical identifier (e.g. ``design.web.landing-page-design``); the
    triple ``(category, subcategory, label)`` is the presentation form.
    """

    __tablename__ = "service_catalog"
    __table_args__ = (
        Index("ix_service_catalog_category_subcategory_position", "category", "subcategory", "position"),
    )

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
