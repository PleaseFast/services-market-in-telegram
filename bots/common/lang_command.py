"""Shared ``/lang`` handler implementation used by all three bots.

Parses ``/lang ru`` / ``/lang en``, validates against the supported set,
persists the preference on the linked ``User`` row (if any), and replies
in the new language.
"""

from __future__ import annotations

from aiogram.types import Message

from app.core.i18n import SUPPORTED, normalize
from bots.common.auth import get_user_by_tg
from bots.common.db import SessionLocal
from bots.common.i18n import t
from bots.common.lang import set_user_language


async def handle_lang_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    requested = (parts[1] if len(parts) > 1 else "").strip().lower()

    # Initial response should use the caller's current language, before any update.
    current_lang = normalize(getattr(message.from_user, "language_code", None))
    async with SessionLocal() as session_lookup:
        user_for_lang = await get_user_by_tg(session_lookup, message.from_user.id)
        if user_for_lang is not None and user_for_lang.language:
            current_lang = normalize(user_for_lang.language)

    if not requested:
        await message.answer(t("shared.language_usage", current_lang))
        return

    primary = requested.split("-", 1)[0]
    if primary not in SUPPORTED:
        await message.answer(
            t(
                "shared.unknown_language",
                current_lang,
                language=requested,
                supported=", ".join(SUPPORTED),
            )
        )
        return

    target_lang = normalize(requested)

    async with SessionLocal() as session:
        user = await get_user_by_tg(session, message.from_user.id)
        if user is not None:
            await set_user_language(session, user, target_lang)

    await message.answer(t("shared.language_changed", target_lang))
