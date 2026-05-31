from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.models.user import UserRole
from app.schemas.common import ORMBase


class UserOut(ORMBase):
    id: UUID
    email: EmailStr | None
    role: UserRole
    is_active: bool
    language: str = "ru"
    created_at: datetime
    profile_complete: bool = True


class LanguageOut(ORMBase):
    language: str


class LanguageIn(ORMBase):
    language: str
