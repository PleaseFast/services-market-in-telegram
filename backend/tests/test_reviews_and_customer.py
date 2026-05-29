"""Bidirectional half-star reviews + customer profile gating + open-projects feed."""
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


async def _make_customer_profile(client, tok: str, name: str) -> None:
    r = await client.put(
        "/api/v1/customers/me",
        headers=_auth(tok),
        json={"display_name": name},
    )
    assert r.status_code == 200, r.text


async def _make_specialist_profile(client, tok: str, name: str) -> None:
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(tok),
        json={
            "full_name": name,
            "age": 30,
            "categories": ["Backend"],
            "years_experience": 4,
            "bio": "",
        },
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_auth_me_customer_profile_complete(client) -> None:
    tok = await _register(client, "needs.profile@x.io", "customer")

    r = await client.get("/api/v1/auth/me", headers=_auth(tok))
    assert r.status_code == 200
    assert r.json()["profile_complete"] is False

    await _make_customer_profile(client, tok, "Acme Co")

    r = await client.get("/api/v1/auth/me", headers=_auth(tok))
    assert r.status_code == 200
    assert r.json()["profile_complete"] is True


@pytest.mark.asyncio
async def test_review_half_step_validation(client) -> None:
    customer = await _register(client, "c.half@x.io", "customer")
    specialist = await _register(client, "s.half@x.io", "specialist")
    await _make_customer_profile(client, customer, "Half Customer")
    await _make_specialist_profile(client, specialist, "Half Specialist")

    # Get a completed project to attach reviews to.
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Half Test", "description": "x", "budget": 100, "publish": True},
    )
    project_id = r.json()["id"]
    await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": ""},
    )
    apps = (await client.get(
        f"/api/v1/projects/{project_id}/applications", headers=_auth(customer)
    )).json()
    await client.post(
        f"/api/v1/projects/{project_id}/select-specialist/{apps[0]['specialist_id']}",
        headers=_auth(customer),
    )
    await client.post(f"/api/v1/projects/{project_id}/complete", headers=_auth(customer))

    # invalid steps / out of range
    for bad in (4.3, 5.5, -0.5, 5.1):
        r = await client.post(
            f"/api/v1/projects/{project_id}/reviews",
            headers=_auth(customer),
            json={"rating": bad, "text": "x"},
        )
        assert r.status_code == 422, f"rating {bad} should be 422, got {r.status_code}"

    # 0 is valid
    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(customer),
        json={"rating": 0, "text": "lowest"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["rating"] == 0.0


@pytest.mark.asyncio
async def test_review_only_between_customer_and_selected_specialist(client) -> None:
    customer = await _register(client, "c.scope@x.io", "customer")
    selected = await _register(client, "selected@x.io", "specialist")
    other = await _register(client, "other.applicant@x.io", "specialist")
    await _make_customer_profile(client, customer, "Scoped Customer")
    await _make_specialist_profile(client, selected, "Selected")
    await _make_specialist_profile(client, other, "Other")

    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Scope", "description": "x", "budget": 100, "publish": True},
    )
    project_id = r.json()["id"]

    # both apply
    for tok in (selected, other):
        r = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            headers=_auth(tok),
            json={"cover_letter": ""},
        )
        assert r.status_code == 201

    apps = (await client.get(
        f"/api/v1/projects/{project_id}/applications", headers=_auth(customer)
    )).json()
    selected_id = next(
        a["specialist_id"] for a in apps if a["specialist_id"] != ""  # filter noop
    )
    # find the application from `selected` (selected@x.io)
    me = (await client.get("/api/v1/auth/me", headers=_auth(selected))).json()
    selected_id = me["id"]
    await client.post(
        f"/api/v1/projects/{project_id}/select-specialist/{selected_id}",
        headers=_auth(customer),
    )
    await client.post(f"/api/v1/projects/{project_id}/complete", headers=_auth(customer))

    # non-selected applicant cannot review
    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(other),
        json={"rating": 5, "text": "sneaky"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_review_recomputes_customer_rating_and_author_name(client) -> None:
    customer = await _register(client, "c.recomp@x.io", "customer")
    specialist = await _register(client, "s.recomp@x.io", "specialist")
    await _make_customer_profile(client, customer, "Recomp Customer")
    await _make_specialist_profile(client, specialist, "Recomp Specialist")

    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Recomp", "description": "x", "budget": 100, "publish": True},
    )
    project_id = r.json()["id"]
    customer_id = r.json()["customer_id"]
    await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": ""},
    )
    apps = (await client.get(
        f"/api/v1/projects/{project_id}/applications", headers=_auth(customer)
    )).json()
    await client.post(
        f"/api/v1/projects/{project_id}/select-specialist/{apps[0]['specialist_id']}",
        headers=_auth(customer),
    )
    await client.post(f"/api/v1/projects/{project_id}/complete", headers=_auth(customer))

    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(specialist),
        json={"rating": 4.5, "text": "nice client"},
    )
    assert r.status_code == 201
    assert r.json()["author_name"] == "Recomp Specialist"

    # Customer's rating updated to 4.5
    r = await client.get(f"/api/v1/customers/{customer_id}")
    assert r.status_code == 200
    body = r.json()
    assert float(body["rating_avg"]) == 4.5
    assert body["rating_count"] == 1

    # Public reviews list carries author_name
    r = await client.get(f"/api/v1/users/{customer_id}/reviews")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["author_name"] == "Recomp Specialist"
    assert items[0]["rating"] == 4.5


@pytest.mark.asyncio
async def test_open_projects_by_customer(client) -> None:
    customer = await _register(client, "c.feed@x.io", "customer")
    await _make_customer_profile(client, customer, "Feed Customer")

    me = (await client.get("/api/v1/auth/me", headers=_auth(customer))).json()
    customer_id = me["id"]

    # one OPEN, one DRAFT — only OPEN should appear
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Open One", "description": "x", "budget": 100, "publish": True},
    )
    open_id = r.json()["id"]
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Draft One", "description": "x", "budget": 100, "publish": False},
    )
    draft_id = r.json()["id"]

    r = await client.get(f"/api/v1/customers/{customer_id}/open-projects")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()]
    assert open_id in ids
    assert draft_id not in ids
