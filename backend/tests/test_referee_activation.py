"""End-to-end coverage for the RefereeBot activation token + link service."""

from __future__ import annotations

import time

import jwt
import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import (
    REFEREE_ACTIVATION_TTL,
    create_referee_activation_token,
    decode_referee_activation_token,
)
from app.models.telegram import TelegramAccount
from app.models.user import User, UserRole
from app.services.auth import link_referee_account


# ---------------- token primitives ----------------


def test_activation_token_roundtrip():
    token = create_referee_activation_token("00000000-0000-0000-0000-000000000001")
    assert decode_referee_activation_token(token) == "00000000-0000-0000-0000-000000000001"


def test_activation_token_rejects_wrong_type():
    settings = get_settings()
    # An access-style token with type=access — must NOT be honoured as an
    # activation token.
    bad = jwt.encode(
        {"sub": "abc", "type": "access", "exp": int(time.time()) + 60},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    with pytest.raises(ValueError):
        decode_referee_activation_token(bad)


def test_activation_token_rejects_tampering():
    token = create_referee_activation_token("00000000-0000-0000-0000-000000000001")
    tampered = token[:-2] + ("aa" if token[-2:] != "aa" else "bb")
    with pytest.raises(Exception):  # InvalidSignatureError or similar
        decode_referee_activation_token(tampered)


def test_activation_token_ttl_short():
    # Sanity check — keep TTL bounded so a leaked token has small blast radius.
    assert REFEREE_ACTIVATION_TTL.total_seconds() <= 30 * 60


# ---------------- link_referee_account ----------------


@pytest.mark.asyncio
async def test_link_creates_account_when_none_exists(session):
    user = User(email="u1@x", role=UserRole.SPECIALIST, password_hash="x")
    session.add(user)
    await session.commit()

    acc = await link_referee_account(
        session, user.id, tg_user_id=12345, tg_username="alice", chat_id=12345
    )
    await session.commit()

    assert acc.user_id == user.id
    assert acc.tg_user_id == 12345
    assert acc.chat_id == 12345
    assert acc.referee_chat_id == 12345
    assert acc.referee_activated_at is not None


@pytest.mark.asyncio
async def test_link_refreshes_when_pair_already_matches(session):
    user = User(email="u2@x", role=UserRole.SPECIALIST, password_hash="x")
    session.add(user)
    await session.commit()
    await link_referee_account(session, user.id, 22, "bob", 22)
    await session.commit()

    # Idempotent re-activation
    acc = await link_referee_account(session, user.id, 22, "bob", 22)
    await session.commit()
    count = (
        await session.execute(
            select(TelegramAccount).where(TelegramAccount.user_id == user.id)
        )
    ).scalars().all()
    assert len(count) == 1
    assert acc.referee_chat_id == 22


@pytest.mark.asyncio
async def test_link_migrates_stale_telegram_to_correct_user(session):
    """Common case: a previous Mini-App auto-bootstrap created a stray
    specialist user holding the Telegram identity. Activating from the real
    web user should hand that Telegram over."""
    stale = User(email="stale@x", role=UserRole.SPECIALIST, password_hash="x")
    real = User(email="real@x", role=UserRole.CUSTOMER, password_hash="x")
    session.add_all([stale, real])
    await session.commit()

    session.add(TelegramAccount(user_id=stale.id, tg_user_id=777, chat_id=777))
    await session.commit()

    await link_referee_account(session, real.id, tg_user_id=777, tg_username=None, chat_id=777)
    await session.commit()

    rows = (await session.execute(select(TelegramAccount))).scalars().all()
    assert len(rows) == 1
    assert rows[0].user_id == real.id
    assert rows[0].tg_user_id == 777
    assert rows[0].referee_chat_id == 777


@pytest.mark.asyncio
async def test_link_replaces_user_previous_telegram(session):
    """User had a Telegram account linked, now activates with a different
    Telegram identity — the old row is removed so the unique constraint on
    ``user_id`` holds."""
    user = User(email="u3@x", role=UserRole.SPECIALIST, password_hash="x")
    session.add(user)
    await session.commit()
    session.add(TelegramAccount(user_id=user.id, tg_user_id=111, chat_id=111))
    await session.commit()

    await link_referee_account(session, user.id, tg_user_id=222, tg_username=None, chat_id=222)
    await session.commit()

    rows = (await session.execute(select(TelegramAccount))).scalars().all()
    assert len(rows) == 1
    assert rows[0].tg_user_id == 222
    assert rows[0].referee_chat_id == 222


# ---------------- HTTP endpoint ----------------


async def _register(client, email, role):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_referee_link_endpoint_returns_url_with_token(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "TG_REFEREE_BOT_USERNAME", "TestRefereeBot")

    tok = await _register(client, "linker@x.io", "specialist")
    r = await client.get(
        "/api/v1/auth/referee-link", headers={"Authorization": f"Bearer {tok}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["bot_username"] == "TestRefereeBot"
    assert body["url"].startswith("https://t.me/TestRefereeBot?start=link_")

    payload_token = body["url"].split("start=link_", 1)[1]
    # The token must decode back to *some* user id — full identity
    # roundtrip is covered above.
    assert decode_referee_activation_token(payload_token)


@pytest.mark.asyncio
async def test_referee_link_requires_auth(client):
    r = await client.get("/api/v1/auth/referee-link")
    assert r.status_code == 401
