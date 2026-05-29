"""Customer-side specialist catalog filtering (category + min_rating) and
specialist-side multi-category feed scoping + profile_complete signal."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest


async def _register(client, email: str, role: str) -> str:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


async def _save_profile(client, tok: str, *, full_name: str, categories: list[str]) -> str:
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(tok),
        json={
            "full_name": full_name,
            "age": 30,
            "categories": categories,
            "years_experience": 5,
            "bio": "",
        },
    )
    assert r.status_code == 200, r.text
    return r.json()["user_id"]


@pytest.mark.asyncio
async def test_profile_complete_flag(client):
    spec = await _register(client, "pc@x.io", "specialist")
    r = await client.get("/api/v1/auth/me", headers=_auth(spec))
    assert r.status_code == 200
    assert r.json()["profile_complete"] is False

    await _save_profile(client, spec, full_name="PC", categories=["AI"])

    r = await client.get("/api/v1/auth/me", headers=_auth(spec))
    assert r.json()["profile_complete"] is True

    # Customers also need a CustomerProfile (display_name) before the
    # onboarding gate considers them complete.
    cust = await _register(client, "pc-c@x.io", "customer")
    r = await client.get("/api/v1/auth/me", headers=_auth(cust))
    assert r.json()["profile_complete"] is False

    r = await client.put(
        "/api/v1/customers/me",
        headers=_auth(cust),
        json={"display_name": "PC Customer"},
    )
    assert r.status_code == 200, r.text

    r = await client.get("/api/v1/auth/me", headers=_auth(cust))
    assert r.json()["profile_complete"] is True


@pytest.mark.asyncio
async def test_specialist_with_multiple_categories_sees_projects_from_all(client):
    cust = await _register(client, "mc-c@x.io", "customer")
    spec = await _register(client, "mc-s@x.io", "specialist")
    await _save_profile(client, spec, full_name="Multi", categories=["Backend", "AI"])

    async def _make(title, description):
        r = await client.post(
            "/api/v1/projects",
            headers=_auth(cust),
            json={
                "title": title,
                "description": description,
                "budget": 100,
                "publish": True,
            },
        )
        assert r.status_code == 201, r.text
        return r.json()

    backend_p = await _make("Stripe integration", "fastapi")
    assert backend_p["category"] == "Backend"
    ai_p = await _make("LLM prompt tuning", "openai gpt-4")
    assert ai_p["category"] == "AI"
    bot_p = await _make("Telegram bot", "aiogram fsm")
    assert bot_p["category"] == "Bots"

    r = await client.get("/api/v1/projects", headers=_auth(spec))
    ids = {p["id"] for p in r.json()["items"]}
    assert backend_p["id"] in ids
    assert ai_p["id"] in ids
    assert bot_p["id"] not in ids


@pytest.mark.asyncio
async def test_specialists_catalog_category_and_rating_filters(client, session):
    """Two specialists with different categories + ratings; combinable filters."""
    from sqlalchemy import update
    from app.models.profile import SpecialistProfile

    s_front = await _register(client, "f@x.io", "specialist")
    s_back = await _register(client, "b@x.io", "specialist")
    s_back_multi = await _register(client, "bm@x.io", "specialist")

    front_id = await _save_profile(
        client, s_front, full_name="Frontie", categories=["Frontend"]
    )
    back_id = await _save_profile(
        client, s_back, full_name="Backie", categories=["Backend"]
    )
    multi_id = await _save_profile(
        client, s_back_multi, full_name="Multi", categories=["Backend", "AI"]
    )

    # Bump ratings: front=2.5, back=4.5, multi=4.9
    async def _rate(user_id: str, value: float) -> None:
        await session.execute(
            update(SpecialistProfile)
            .where(SpecialistProfile.user_id == UUID(user_id))
            .values(rating_avg=Decimal(str(value)), rating_count=1)
        )
        await session.commit()

    await _rate(front_id, 2.5)
    await _rate(back_id, 4.5)
    await _rate(multi_id, 4.9)

    # No filter — all three
    r = await client.get("/api/v1/specialists")
    ids = {p["user_id"] for p in r.json()["items"]}
    assert ids == {front_id, back_id, multi_id}

    # category=Backend → back + multi (multi has Backend in its set)
    r = await client.get("/api/v1/specialists?category=Backend")
    ids = {p["user_id"] for p in r.json()["items"]}
    assert ids == {back_id, multi_id}

    # category=AI → only multi
    r = await client.get("/api/v1/specialists?category=AI")
    ids = {p["user_id"] for p in r.json()["items"]}
    assert ids == {multi_id}

    # min_rating=4 → back + multi (front is 2.5)
    r = await client.get("/api/v1/specialists?min_rating=4")
    ids = {p["user_id"] for p in r.json()["items"]}
    assert ids == {back_id, multi_id}

    # Combined: category=Backend & min_rating=4.7 → only multi
    r = await client.get("/api/v1/specialists?category=Backend&min_rating=4.7")
    ids = {p["user_id"] for p in r.json()["items"]}
    assert ids == {multi_id}


@pytest.mark.asyncio
async def test_profile_rejects_empty_categories(client):
    spec = await _register(client, "empty@x.io", "specialist")
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(spec),
        json={
            "full_name": "E",
            "age": 30,
            "categories": [],
            "years_experience": 1,
            "bio": "",
        },
    )
    assert r.status_code == 422
