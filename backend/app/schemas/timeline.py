from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.profile_timeline_item import TimelineKind
from app.schemas.common import ORMBase

TimelineKindLiteral = Literal["work", "education", "achievement"]


def _year_bounds() -> tuple[int, int]:
    return 1950, datetime.now(timezone.utc).year + 1


class TimelineItemIn(BaseModel):
    """Request body for create / partial update (PATCH ignores None fields)."""

    kind: TimelineKindLiteral | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    start_year: int | None = Field(default=None)
    end_year: int | None = Field(default=None)
    is_current: bool | None = None

    @model_validator(mode="after")
    def _validate_years(self) -> "TimelineItemIn":
        floor, ceil = _year_bounds()
        if self.start_year is not None and not (floor <= self.start_year <= ceil):
            raise ValueError(f"start_year must be between {floor} and {ceil}")
        if self.end_year is not None and not (floor <= self.end_year <= ceil):
            raise ValueError(f"end_year must be between {floor} and {ceil}")
        # Cross-field rule only enforced when we have both years AND know the
        # is_current flag (treated as False if explicitly unset on a full create).
        if (
            self.is_current is False
            and self.end_year is not None
            and self.start_year is not None
            and self.end_year < self.start_year
        ):
            raise ValueError("end_year must be >= start_year")
        return self


class TimelineItemCreate(BaseModel):
    """Stricter create form — all required fields must be present."""

    kind: TimelineKindLiteral
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=4000)
    start_year: int
    end_year: int | None = None
    is_current: bool = False

    @model_validator(mode="after")
    def _validate(self) -> "TimelineItemCreate":
        floor, ceil = _year_bounds()
        if not (floor <= self.start_year <= ceil):
            raise ValueError(f"start_year must be between {floor} and {ceil}")
        if self.end_year is not None and not (floor <= self.end_year <= ceil):
            raise ValueError(f"end_year must be between {floor} and {ceil}")
        if not self.is_current and self.end_year is None:
            raise ValueError("end_year is required when is_current is false")
        if not self.is_current and self.end_year is not None and self.end_year < self.start_year:
            raise ValueError("end_year must be >= start_year")
        return self


class TimelineItemOut(ORMBase):
    id: UUID
    profile_id: UUID
    kind: TimelineKind
    title: str
    description: str
    start_year: int
    end_year: int | None
    is_current: bool
    position: int


class TimelineMoveIn(BaseModel):
    direction: Literal["up", "down"]
