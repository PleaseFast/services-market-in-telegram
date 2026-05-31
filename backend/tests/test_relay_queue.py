"""Coverage for the short-lived Redis delivery queue used by RefereeBot.

We stub ``app.core.redis.get_redis`` with a tiny in-memory mock that mimics
the subset of redis-py we use: ``rpush``, ``ltrim``, ``expire``, ``lrange``,
``delete``, ``llen``, and the async pipeline (``MULTI/EXEC``).
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.services import relay_queue


class _Pipeline:
    def __init__(self, store: "FakeRedis") -> None:
        self._store = store
        self._ops: list[tuple[str, tuple]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def lrange(self, key, start, end):
        self._ops.append(("lrange", (key, start, end)))

    def delete(self, key):
        self._ops.append(("delete", (key,)))

    async def execute(self):
        results = []
        for op, args in self._ops:
            if op == "lrange":
                results.append(self._store._lrange(*args))
            elif op == "delete":
                results.append(self._store._delete(*args))
        self._ops.clear()
        return results


class FakeRedis:
    def __init__(self) -> None:
        self.lists: dict[str, list[str]] = {}
        self.ttls: dict[str, int] = {}

    # --- list ops ---
    async def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)
        return len(self.lists[key])

    async def ltrim(self, key, start, end):
        if key not in self.lists:
            return True
        items = self.lists[key]
        if end == -1:
            end = len(items) - 1
        self.lists[key] = items[start : end + 1]
        return True

    async def expire(self, key, seconds):
        self.ttls[key] = seconds
        return True

    async def llen(self, key):
        return len(self.lists.get(key, []))

    def _lrange(self, key, start, end):
        items = self.lists.get(key, [])
        if end == -1:
            end = len(items) - 1
        return items[start : end + 1]

    def _delete(self, key):
        existed = key in self.lists
        self.lists.pop(key, None)
        self.ttls.pop(key, None)
        return 1 if existed else 0

    def pipeline(self, transaction: bool = True):
        return _Pipeline(self)


@pytest.fixture
def fake_redis(monkeypatch):
    fr = FakeRedis()
    monkeypatch.setattr("app.services.relay_queue.get_redis", lambda: fr)
    return fr


def _pointer(idx: int) -> dict:
    return {
        "thread_id": str(uuid4()),
        "sender_party": "customer",
        "sender_name": f"Sender{idx}",
        "project_id": str(uuid4()),
        "project_title": f"P{idx}",
        "source_chat_id": 111,
        "source_message_id": idx,
        "recipient_lang": "en",
    }


@pytest.mark.asyncio
async def test_enqueue_then_drain_round_trip(fake_redis):
    recipient = uuid4()
    await relay_queue.enqueue(recipient, _pointer(1))
    await relay_queue.enqueue(recipient, _pointer(2))

    drained = await relay_queue.drain(recipient)

    assert [p["source_message_id"] for p in drained] == [1, 2]
    assert await fake_redis.llen(f"relay_pending:{recipient}") == 0


@pytest.mark.asyncio
async def test_enqueue_sets_ttl(fake_redis):
    recipient = uuid4()
    await relay_queue.enqueue(recipient, _pointer(1))

    assert fake_redis.ttls[f"relay_pending:{recipient}"] == relay_queue.PENDING_TTL_SECONDS


@pytest.mark.asyncio
async def test_enqueue_caps_at_max(fake_redis):
    recipient = uuid4()
    for i in range(relay_queue.MAX_PENDING_PER_USER + 5):
        await relay_queue.enqueue(recipient, _pointer(i))

    drained = await relay_queue.drain(recipient)

    assert len(drained) == relay_queue.MAX_PENDING_PER_USER
    # Oldest dropped — the surviving entries are the most recent ones.
    assert drained[0]["source_message_id"] == 5
    assert drained[-1]["source_message_id"] == relay_queue.MAX_PENDING_PER_USER + 4


@pytest.mark.asyncio
async def test_drain_on_empty_returns_empty(fake_redis):
    assert await relay_queue.drain(uuid4()) == []


@pytest.mark.asyncio
async def test_drain_skips_malformed_pointers(fake_redis):
    recipient = uuid4()
    fake_redis.lists[f"relay_pending:{recipient}"] = [
        json.dumps(_pointer(1)),
        "not-json",
        json.dumps(_pointer(2)),
    ]

    drained = await relay_queue.drain(recipient)

    assert [p["source_message_id"] for p in drained] == [1, 2]
