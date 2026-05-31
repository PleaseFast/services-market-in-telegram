"""Apply-time RefereeBot activation gate.

The other tests bypass this check (see ``conftest._skip_referee_activation_check``)
because they don't model Telegram linkage. This file unsets that bypass and
exercises the real behaviour."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.telegram import TelegramAccount
from app.models.user import User


@pytest.fixture(autouse=True)
def _skip_referee_activation_check():
    """Override conftest's autouse bypass — these tests want the real gate."""
    return None


async def _register(client, email, role):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


async def _set_specialist_profile(client, tok: str) -> None:
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(tok),
        json={
            "full_name": "Gate Test",
            "age": 30,
            "categories": ["Backend"],
            "years_experience": 3,
            "bio": "",
        },
    )
    assert r.status_code == 200


async def _publish_project(client, customer_tok: str) -> str:
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer_tok),
        json={"title": "Gate", "description": "x", "budget": 1, "publish": True},
    )
    assert r.status_code == 201
    return r.json()["id"]


@pytest.mark.asyncio
async def test_apply_rejected_without_referee_activation(client, session):
    customer = await _register(client, "c.gate@x.io", "customer")
    specialist = await _register(client, "s.gate@x.io", "specialist")
    await _set_specialist_profile(client, specialist)
    project_id = await _publish_project(client, customer)

    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "hi"},
    )
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "applications.referee_not_activated"
    # The bot @username travels in params so the client can render the CTA
    # without its own config.
    assert "bot_username" in body["params"]


@pytest.mark.asyncio
async def test_apply_allowed_after_referee_activation(client, session):
    customer = await _register(client, "c.gate2@x.io", "customer")
    specialist = await _register(client, "s.gate2@x.io", "specialist")
    await _set_specialist_profile(client, specialist)
    project_id = await _publish_project(client, customer)

    # Simulate the specialist tapping /start on RefereeBot: insert the
    # ``TelegramAccount`` row with ``referee_chat_id`` set.
    user = (
        await session.execute(select(User).where(User.email == "s.gate2@x.io"))
    ).scalar_one()
    session.add(
        TelegramAccount(
            user_id=user.id,
            tg_user_id=99001,
            referee_chat_id=99001,
        )
    )
    await session.commit()

    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "now i can"},
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_auth_me_reports_activation_state(client, session):
    specialist = await _register(client, "s.me@x.io", "specialist")

    me = (await client.get("/api/v1/auth/me", headers=_auth(specialist))).json()
    assert me["referee_activated"] is False

    user = (
        await session.execute(select(User).where(User.email == "s.me@x.io"))
    ).scalar_one()
    session.add(
        TelegramAccount(user_id=user.id, tg_user_id=99002, referee_chat_id=99002)
    )
    await session.commit()

    me = (await client.get("/api/v1/auth/me", headers=_auth(specialist))).json()
    assert me["referee_activated"] is True
