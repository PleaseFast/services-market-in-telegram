"""Resolve which language to address a Telegram user in.

Precedence:
1. The persisted ``User.language`` if we know the user.
2. The Telegram-reported ``language_code`` on the incoming message.
3. The product-wide DEFAULT (Russian).

Also handles persisting an initial preference on first ``/start`` so the
notification fan-out — which only has a UUID, not the inbound message —
later resolves to the same language without re-asking.
"""

from __future__ import annotations

import logging
from uuid import UUID

from aiogram.types import User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import DEFAULT, normalize
from app.models.user import User

log = logging.getLogger(__name__)


def resolve_from_tg(tg_user: TgUser | None) -> str:
    if tg_user is None:
        return DEFAULT
    return normalize(getattr(tg_user, "language_code", None))


async def resolve_for_user(session: AsyncSession, user: User | None) -> str:
    if user is None:
        return DEFAULT
    return normalize(user.language)


async def language_for_user_id(session: AsyncSession, user_id: UUID | str) -> str:
    """Look up the stored language by user_id; used by notification fan-out."""
    try:
        uid = user_id if isinstance(user_id, UUID) else UUID(str(user_id))
    except (ValueError, AttributeError):
        return DEFAULT
    res = await session.execute(select(User.language).where(User.id == uid))
    raw = res.scalar_one_or_none()
    return normalize(raw)


async def ensure_user_language(
    session: AsyncSession, user: User | None, tg_user: TgUser | None
) -> str:
    """Persist a first-seen language for a known user; return whichever lang
    should drive this turn's responses.

    Never overwrites an existing preference — once a user picks a language
    (via ``/lang`` or the web UI), the Telegram client locale stops
    influencing them.
    """
    detected = resolve_from_tg(tg_user)
    if user is None:
        return detected
    if not user.language:
        user.language = detected
        try:
            await session.commit()
        except Exception:
            log.exception("Failed to persist initial language for user %s", user.id)
            await session.rollback()
    return normalize(user.language)


async def set_user_language(
    session: AsyncSession, user: User, lang: str
) -> str:
    normalized = normalize(lang)
    user.language = normalized
    await session.commit()
    return normalized
