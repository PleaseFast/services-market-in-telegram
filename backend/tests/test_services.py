"""Service catalog + specialist services CRUD."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.service_catalog import SERVICE_CATALOG
from app.models.service_catalog import ServiceCatalogItem


async def _register_specialist(client, email: str) -> str:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": "specialist"},
    )
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


async def _save_profile(client, tok: str, category: str = "Backend") -> None:
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(tok),
        json={
            "full_name": "Sam", "age": 30, "categories": [category],
            "years_experience": 5, "bio": "",
        },
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_catalog_seed_and_endpoint(client, session):
    # Seed a couple of catalog entries manually since the test session is
    # in-memory and the seed runner is not invoked here.
    for entry in SERVICE_CATALOG[:5]:
        session.add(
            ServiceCatalogItem(
                slug=entry.slug,
                category=entry.category,
                subcategory=entry.subcategory,
                label=entry.label,
            )
        )
    await session.commit()

    r = await client.get("/api/v1/services/catalog")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 5
    assert all("slug" in item for item in body)


@pytest.mark.asyncio
async def test_specialist_services_replace_all(client, session):
    # Seed a couple of catalog rows
    seeded = []
    for entry in SERVICE_CATALOG[:3]:
        item = ServiceCatalogItem(
            slug=entry.slug,
            category=entry.category,
            subcategory=entry.subcategory,
            label=entry.label,
        )
        session.add(item)
        seeded.append(entry)
    await session.commit()

    tok = await _register_specialist(client, "svc1@x.io")
    await _save_profile(client, tok)

    # Initial empty list
    me = await client.get("/api/v1/specialists/me", headers=_auth(tok))
    assert me.json()["services"] == []

    # PUT two services
    r = await client.put(
        "/api/v1/specialists/me/services",
        headers=_auth(tok),
        json={
            "items": [
                {"slug": seeded[0].slug, "price_amount": "100.00", "price_currency": "USD"},
                {"slug": seeded[1].slug, "price_amount": "250.00", "price_currency": "USD"},
            ]
        },
    )
    assert r.status_code == 204, r.text

    # Re-fetch — both services included
    me = await client.get("/api/v1/specialists/me", headers=_auth(tok))
    body = me.json()
    slugs = {s["slug"] for s in body["services"]}
    assert slugs == {seeded[0].slug, seeded[1].slug}

    # Replace with a single different service
    r = await client.put(
        "/api/v1/specialists/me/services",
        headers=_auth(tok),
        json={"items": [{"slug": seeded[2].slug, "price_amount": "50.00", "price_currency": "USD"}]},
    )
    assert r.status_code == 204
    me = await client.get("/api/v1/specialists/me", headers=_auth(tok))
    slugs = {s["slug"] for s in me.json()["services"]}
    assert slugs == {seeded[2].slug}


@pytest.mark.asyncio
async def test_invalid_slug_rejected(client, session):
    tok = await _register_specialist(client, "svc2@x.io")
    await _save_profile(client, tok)

    r = await client.put(
        "/api/v1/specialists/me/services",
        headers=_auth(tok),
        json={"items": [{"slug": "not.a.real.slug", "price_amount": "100"}]},
    )
    assert r.status_code == 400
    assert "Unknown service" in r.text


@pytest.mark.asyncio
async def test_duplicate_slug_rejected(client, session):
    entry = SERVICE_CATALOG[0]
    session.add(
        ServiceCatalogItem(
            slug=entry.slug,
            category=entry.category,
            subcategory=entry.subcategory,
            label=entry.label,
        )
    )
    await session.commit()

    tok = await _register_specialist(client, "svc3@x.io")
    await _save_profile(client, tok)

    r = await client.put(
        "/api/v1/specialists/me/services",
        headers=_auth(tok),
        json={
            "items": [
                {"slug": entry.slug, "price_amount": "100"},
                {"slug": entry.slug, "price_amount": "200"},
            ]
        },
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_public_specialist_services_endpoint(client, session):
    entry = SERVICE_CATALOG[0]
    session.add(
        ServiceCatalogItem(
            slug=entry.slug, category=entry.category,
            subcategory=entry.subcategory, label=entry.label,
        )
    )
    await session.commit()

    tok = await _register_specialist(client, "svc4@x.io")
    await _save_profile(client, tok)
    await client.put(
        "/api/v1/specialists/me/services",
        headers=_auth(tok),
        json={"items": [{"slug": entry.slug, "price_amount": "42"}]},
    )

    me = await client.get("/api/v1/specialists/me", headers=_auth(tok))
    user_id = me.json()["user_id"]

    r = await client.get(f"/api/v1/specialists/{user_id}/services")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["slug"] == entry.slug
    assert float(body[0]["price_amount"]) == 42.0
