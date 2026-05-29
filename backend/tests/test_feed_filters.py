"""Feed-side tests: category auto-assignment, search/budget filters,
viewer-profile scoping, and Viewed-first sort."""
from __future__ import annotations

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


async def _create_project(
    client, token: str, *, title: str, description: str = "", budget: int = 0,
    category: str | None = None, template_id: str | None = None,
) -> dict:
    payload = {
        "title": title,
        "description": description,
        "budget": budget,
        "publish": True,
    }
    if category is not None:
        payload["category"] = category
    if template_id is not None:
        payload["template_id"] = template_id
    r = await client.post("/api/v1/projects", headers=_auth(token), json=payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.mark.asyncio
async def test_manual_project_gets_keyword_suggested_category(client):
    customer = await _register(client, "c1@x.io", "customer")
    p = await _create_project(
        client, customer, title="Telegram bot for orders", description="aiogram fsm"
    )
    assert p["category"] == "Bots"


@pytest.mark.asyncio
async def test_explicit_category_overrides_suggestion(client):
    customer = await _register(client, "c2@x.io", "customer")
    # Title alone would suggest Backend; the explicit Other should win.
    p = await _create_project(
        client, customer, title="Stripe API integration", category="Other"
    )
    assert p["category"] == "Other"


@pytest.mark.asyncio
async def test_unmatched_falls_back_to_other(client):
    customer = await _register(client, "c3@x.io", "customer")
    p = await _create_project(
        client, customer, title="Something vague here", description="no signals"
    )
    assert p["category"] == "Other"


@pytest.mark.asyncio
async def test_text_search_and_budget_filters(client):
    customer = await _register(client, "c4@x.io", "customer")
    cheap = await _create_project(
        client, customer, title="Stripe integration", description="api", budget=300
    )
    pricey = await _create_project(
        client, customer, title="React dashboard", description="ui", budget=4000
    )

    # q=stripe matches the title of the cheap one but not the pricey one
    r = await client.get("/api/v1/projects?q=stripe")
    ids = {p["id"] for p in r.json()["items"]}
    assert cheap["id"] in ids
    assert pricey["id"] not in ids

    # budget_min=1000 should exclude the cheap one
    r = await client.get("/api/v1/projects?budget_min=1000")
    ids = {p["id"] for p in r.json()["items"]}
    assert cheap["id"] not in ids
    assert pricey["id"] in ids

    # budget range that excludes both
    r = await client.get("/api/v1/projects?budget_min=10000&budget_max=20000")
    assert r.json()["items"] == []


@pytest.mark.asyncio
async def test_feed_is_scoped_to_specialist_profile_category(client):
    customer = await _register(client, "c5@x.io", "customer")
    specialist = await _register(client, "s5@x.io", "specialist")

    # specialist picks Backend on their profile
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(specialist),
        json={
            "full_name": "Pat", "age": 28, "categories": ["Backend"],
            "years_experience": 3, "bio": "",
        },
    )
    assert r.status_code == 200, r.text

    backend_p = await _create_project(
        client, customer, title="Stripe API integration", description="fastapi"
    )
    assert backend_p["category"] == "Backend"
    bot_p = await _create_project(
        client, customer, title="Telegram bot for orders", description="aiogram"
    )
    assert bot_p["category"] == "Bots"

    # Specialist sees only Backend projects.
    r = await client.get("/api/v1/projects", headers=_auth(specialist))
    ids = {p["id"] for p in r.json()["items"]}
    assert backend_p["id"] in ids
    assert bot_p["id"] not in ids

    # Guests see both.
    r = await client.get("/api/v1/projects")
    ids = {p["id"] for p in r.json()["items"]}
    assert backend_p["id"] in ids
    assert bot_p["id"] in ids


@pytest.mark.asyncio
async def test_sort_viewed_bubbles_visited_projects_to_top(client):
    customer = await _register(client, "c6@x.io", "customer")
    specialist = await _register(client, "s6@x.io", "specialist")

    await client.put(
        "/api/v1/specialists/me",
        headers=_auth(specialist),
        json={
            "full_name": "View", "age": 28, "categories": ["Backend"],
            "years_experience": 3, "bio": "",
        },
    )

    first = await _create_project(
        client, customer, title="Stripe API one", description="api", budget=100
    )
    second = await _create_project(
        client, customer, title="Stripe API two", description="api", budget=200
    )
    # third is created last, so under sort=newest it appears first by default.
    third = await _create_project(
        client, customer, title="Stripe API three", description="api", budget=300
    )

    # Default newest sort: third is on top.
    r = await client.get("/api/v1/projects?sort=newest", headers=_auth(specialist))
    items = r.json()["items"]
    assert items[0]["id"] == third["id"]

    # The specialist opens the first project's detail page.
    r = await client.get(f"/api/v1/projects/{first['id']}", headers=_auth(specialist))
    assert r.status_code == 200

    # sort=viewed should now put `first` on top; the other two trail behind
    # in some order (created_at tiebreak isn't load-bearing here).
    r = await client.get("/api/v1/projects?sort=viewed", headers=_auth(specialist))
    items = r.json()["items"]
    assert items[0]["id"] == first["id"]
    trailing_ids = {p["id"] for p in items[1:]}
    assert trailing_ids == {second["id"], third["id"]}
