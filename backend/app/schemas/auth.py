from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TelegramAuthIn(BaseModel):
    init_data: str = Field(description="Raw initData string from Telegram Mini App")
    role: UserRole | None = Field(
        default=None,
        description="Required only on first auth (to choose role).",
    )
    bot: str = Field(default="referee", description="Which bot's token to validate against: doers | customers | referee")


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str
