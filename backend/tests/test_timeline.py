"""Per-item CRUD + reorder for the specialist profile timeline."""
from __future__ import annotations

import pytest


async def _register_specialist(client, email: str) -> str:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": "specialist"},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


async def _save_profile(client, tok: str) -> None:
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(tok),
        json={
            "full_name": "Sam",
            "age": 30,
            "categories": ["Backend"],
            "years_experience": 5,
            "bio": "",
        },
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_create_list_update_delete(client):
    tok = await _register_specialist(client, "t1@x.io")
    await _save_profile(client, tok)

    # Create three items of mixed kinds
    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "work", "title": "Acme · Backend Engineer",
            "description": "fastapi", "start_year": 2020, "end_year": None,
            "is_current": True,
        },
    )
    assert r.status_code == 201, r.text
    work = r.json()
    assert work["position"] == 0
    assert work["end_year"] is None
    assert work["is_current"] is True

    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "education", "title": "MIT", "description": "CS",
            "start_year": 2014, "end_year": 2018, "is_current": False,
        },
    )
    assert r.status_code == 201, r.text
    edu = r.json()

    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "achievement", "title": "Open source",
            "description": "Maintainer of foo", "start_year": 2022, "end_year": 2023,
            "is_current": False,
        },
    )
    assert r.status_code == 201, r.text

    # List all
    r = await client.get("/api/v1/specialists/me/timeline", headers=_auth(tok))
    assert r.status_code == 200
    assert len(r.json()) == 3

    # Filter by kind
    r = await client.get("/api/v1/specialists/me/timeline?kind=work", headers=_auth(tok))
    assert len(r.json()) == 1

    # Patch: turn off is_current on the work entry, set end_year
    r = await client.patch(
        f"/api/v1/specialists/me/timeline/{work['id']}",
        headers=_auth(tok),
        json={"is_current": False, "end_year": 2024},
    )
    assert r.status_code == 200
    assert r.json()["end_year"] == 2024
    assert r.json()["is_current"] is False

    # Delete the education entry
    r = await client.delete(
        f"/api/v1/specialists/me/timeline/{edu['id']}", headers=_auth(tok)
    )
    assert r.status_code == 204
    r = await client.get("/api/v1/specialists/me/timeline", headers=_auth(tok))
    assert len(r.json()) == 2


@pytest.mark.asyncio
async def test_year_validation(client):
    tok = await _register_specialist(client, "t2@x.io")
    await _save_profile(client, tok)

    # end_year < start_year (with is_current=false) should 422
    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "work", "title": "T", "description": "",
            "start_year": 2020, "end_year": 2010, "is_current": False,
        },
    )
    assert r.status_code == 422

    # is_current=false but no end_year
    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "work", "title": "T", "description": "",
            "start_year": 2020, "is_current": False,
        },
    )
    assert r.status_code == 422

    # Year out of range
    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(tok),
        json={
            "kind": "work", "title": "T", "description": "",
            "start_year": 1800, "end_year": 2020, "is_current": False,
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_reorder_move(client):
    tok = await _register_specialist(client, "t3@x.io")
    await _save_profile(client, tok)

    # Create two work items: A (position 0), B (position 1)
    ids = []
    for title in ("AAA", "BBB"):
        r = await client.post(
            "/api/v1/specialists/me/timeline",
            headers=_auth(tok),
            json={
                "kind": "work", "title": title, "description": "",
                "start_year": 2020, "end_year": 2021, "is_current": False,
            },
        )
        ids.append(r.json()["id"])

    # Move B up: positions should swap
    r = await client.post(
        f"/api/v1/specialists/me/timeline/{ids[1]}/move",
        headers=_auth(tok),
        json={"direction": "up"},
    )
    assert r.status_code == 200
    assert r.json()["position"] == 0

    r = await client.get("/api/v1/specialists/me/timeline?kind=work", headers=_auth(tok))
    by_id = {item["id"]: item for item in r.json()}
    assert by_id[ids[0]]["position"] == 1
    assert by_id[ids[1]]["position"] == 0

    # Moving the top item up further is a no-op (still at 0)
    r = await client.post(
        f"/api/v1/specialists/me/timeline/{ids[1]}/move",
        headers=_auth(tok),
        json={"direction": "up"},
    )
    assert r.status_code == 200
    assert r.json()["position"] == 0


@pytest.mark.asyncio
async def test_cross_user_isolation(client):
    a = await _register_specialist(client, "iso-a@x.io")
    b = await _register_specialist(client, "iso-b@x.io")
    await _save_profile(client, a)
    await _save_profile(client, b)

    # A creates an item
    r = await client.post(
        "/api/v1/specialists/me/timeline",
        headers=_auth(a),
        json={
            "kind": "work", "title": "A item", "description": "",
            "start_year": 2020, "end_year": 2021, "is_current": False,
        },
    )
    item_id = r.json()["id"]

    # B can't patch or delete A's item
    r = await client.patch(
        f"/api/v1/specialists/me/timeline/{item_id}",
        headers=_auth(b),
        json={"title": "stolen"},
    )
    assert r.status_code == 404

    r = await client.delete(
        f"/api/v1/specialists/me/timeline/{item_id}", headers=_auth(b)
    )
    assert r.status_code == 404
