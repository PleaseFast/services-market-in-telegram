"""Short-lived Redis buffer for RefereeBot relay attempts.

When a sender posts in a chat thread but the counterpart has not yet activated
RefereeBot, we cannot DM them. We also will not store the message body — only
the Telegram pointer (source chat_id + message_id) — so we can replay via
``bot.copy_message`` once the counterpart starts the bot. Pointers expire
after :data:`PENDING_TTL_SECONDS`; nothing survives beyond delivery or expiry.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from app.core.redis import get_redis

log = logging.getLogger(__name__)

PENDING_TTL_SECONDS = 7 * 24 * 3600
MAX_PENDING_PER_USER = 50


def _key(recipient_id: UUID | str) -> str:
    return f"relay_pending:{recipient_id}"


async def enqueue(recipient_id: UUID | str, pointer: dict[str, Any]) -> None:
    """Append a pointer for later replay. Bounded; oldest dropped when full.

    The TTL is reset on every push so an active conversation doesn't expire
    mid-flight; the key disappears 7 days after the last push if the
    counterpart never shows up.
    """
    redis = get_redis()
    key = _key(recipient_id)
    payload = json.dumps(pointer, default=str)
    try:
        await redis.rpush(key, payload)
        await redis.ltrim(key, -MAX_PENDING_PER_USER, -1)
        await redis.expire(key, PENDING_TTL_SECONDS)
    except Exception:
        log.exception("relay_queue.enqueue failed for %s", recipient_id)


async def drain(recipient_id: UUID | str) -> list[dict[str, Any]]:
    """Atomically read+clear the queue. Returns pointers in arrival order.

    Uses a MULTI/EXEC pipeline so we never lose pointers to a racing pusher
    that lands between LRANGE and DEL.
    """
    redis = get_redis()
    key = _key(recipient_id)
    try:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.lrange(key, 0, -1)
            pipe.delete(key)
            raw_list, _ = await pipe.execute()
    except Exception:
        log.exception("relay_queue.drain failed for %s", recipient_id)
        return []

    pointers: list[dict[str, Any]] = []
    for raw in raw_list or []:
        try:
            pointers.append(json.loads(raw))
        except Exception:
            log.exception("relay_queue: dropping malformed pointer %r", raw)
    return pointers
