from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SpecialistService(Base):
    """Binding row: a service from the catalog offered by a specialist, with price.

    Composite PK ``(profile_id, service_id)`` — adding a service to a profile
    is one INSERT; updating the price is one UPDATE; removing is one DELETE.
    The endpoint that edits these always operates as replace-all, so per-item
    timestamps aren't needed.
    """

    __tablename__ = "specialist_services"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_catalog.id", ondelete="CASCADE"),
        primary_key=True,
    )
    price_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default="0"
    )
    price_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD", server_default="USD"
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
