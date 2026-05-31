"""Redis subscriber that fans notifications from the backend out to bot DMs."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable

from aiogram import Bot

from app.core.i18n import DEFAULT as DEFAULT_LANG
from app.core.redis import get_redis
from bots.common.db import SessionLocal
from bots.common.lang import language_for_user_id

log = logging.getLogger(__name__)

# A formatter receives the parsed payload and the recipient's language.
Formatter = Callable[[dict, str], str]


async def run_notification_loop(
    bot: Bot,
    user_chat_lookup: Callable[[str], Awaitable[int | None]],
    formatter: Formatter,
    type_filter: set[str] | None = None,
) -> None:
    """Subscribe to all notify:* channels; deliver DMs to bot users.

    user_chat_lookup(user_id_str) -> chat_id or None for this bot's audience
    """
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("notify:*")
    log.info("Subscribed to notify:*")

    async for msg in pubsub.listen():
        if msg["type"] != "pmessage":
            continue
        try:
            channel: str = msg["channel"]
            user_id = channel.split(":", 1)[1]
            payload = json.loads(msg["data"])
            if type_filter and payload.get("type") not in type_filter:
                continue
            chat_id = await user_chat_lookup(user_id)
            if chat_id is None:
                continue
            lang = DEFAULT_LANG
            try:
                async with SessionLocal() as session:
                    lang = await language_for_user_id(session, user_id)
            except Exception:
                log.exception("Failed to resolve language for %s — falling back", user_id)
            text = formatter(payload, lang)
            await bot.send_message(chat_id, text, parse_mode="HTML")
        except Exception:
            log.exception("Failed to deliver notification")
            await asyncio.sleep(0.1)
