from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.telegram import TelegramAccount
from app.models.user import User, UserRole
from bots.common.db import SessionLocal


async def chat_id_for_user_id(user_id_str: str, role: UserRole | None = None) -> int | None:
    """Look up a user's Telegram chat_id, optionally filtering by role."""
    try:
        uid = UUID(user_id_str)
    except ValueError:
        return None
    async with SessionLocal() as session:
        stmt = (
            select(TelegramAccount.chat_id)
            .join(User, User.id == TelegramAccount.user_id)
            .where(TelegramAccount.user_id == uid)
        )
        if role is not None:
            stmt = stmt.where(User.role == role)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
