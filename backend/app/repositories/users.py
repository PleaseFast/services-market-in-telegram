from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.telegram import TelegramAccount
from app.models.user import User


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(
        User,
        user_id,
        options=[
            selectinload(User.specialist_profile),
            selectinload(User.customer_profile),
            selectinload(User.telegram_account),
        ],
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def get_user_by_tg_id(session: AsyncSession, tg_user_id: int) -> User | None:
    res = await session.execute(
        select(User)
        .join(TelegramAccount, TelegramAccount.user_id == User.id)
        .where(TelegramAccount.tg_user_id == tg_user_id)
        .options(
            selectinload(User.telegram_account),
            selectinload(User.specialist_profile),
            selectinload(User.customer_profile),
        )
    )
    return res.scalar_one_or_none()
