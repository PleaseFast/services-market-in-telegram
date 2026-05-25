from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telegram import TelegramAccount
from app.models.user import User


async def get_user_by_tg(session: AsyncSession, tg_user_id: int) -> User | None:
    res = await session.execute(
        select(User)
        .join(TelegramAccount, TelegramAccount.user_id == User.id)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    )
    return res.scalar_one_or_none()


async def update_chat_id(session: AsyncSession, tg_user_id: int, chat_id: int) -> None:
    res = await session.execute(
        select(TelegramAccount).where(TelegramAccount.tg_user_id == tg_user_id)
    )
    acc = res.scalar_one_or_none()
    if acc is None:
        return
    acc.chat_id = chat_id
    acc.auth_date = datetime.now(UTC)
    await session.commit()
