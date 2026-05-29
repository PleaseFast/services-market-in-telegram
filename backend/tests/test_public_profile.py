"""Public specialist profile shape, paginated reviews with project titles,
and applicant preview embedding."""
from __future__ import annotations

import pytest


async def _register(client, email: str, role: str) -> str:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


@pytest.mark.asyncio
async def test_public_profile_shape(client):
    spec = await _register(client, "pub-spec@x.io", "specialist")
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(spec),
        json={
            "full_name": "Public Spec", "age": 29, "categories": ["Backend"],
            "years_experience": 4, "bio": "hello",
            "avatar_id": "owl:slate",
        },
    )
    assert r.status_code == 200
    user_id = r.json()["user_id"]

    # Add one of each kind
    for kind, title, sy, ey, current in [
        ("work", "Acme · Engineer", 2021, None, True),
        ("education", "MIT", 2014, 2018, False),
        ("achievement", "Open source", 2020, 2021, False),
    ]:
        r = await client.post(
            "/api/v1/specialists/me/timeline",
            headers=_auth(spec),
            json={
                "kind": kind, "title": title, "description": "",
                "start_year": sy, "end_year": ey, "is_current": current,
            },
        )
        assert r.status_code == 201, r.text

    r = await client.get(f"/api/v1/specialists/{user_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["avatar_id"] == "owl:slate"
    assert body["full_name"] == "Public Spec"
    assert "timeline" in body
    assert len(body["timeline"]["work"]) == 1
    assert len(body["timeline"]["education"]) == 1
    assert len(body["timeline"]["achievement"]) == 1
    assert body["services"] == []


@pytest.mark.asyncio
async def test_applicant_preview_embedded(client):
    cust = await _register(client, "pub-cust@x.io", "customer")
    spec = await _register(client, "pub-applicant@x.io", "specialist")
    await client.put(
        "/api/v1/specialists/me",
        headers=_auth(spec),
        json={
            "full_name": "Applicant One", "age": 28, "categories": ["Backend"],
            "years_experience": 2, "bio": "",
            "avatar_id": "cat:rose",
        },
    )

    r = await client.post(
        "/api/v1/projects",
        headers=_auth(cust),
        json={"title": "Stripe integration", "description": "fastapi", "budget": 1000, "publish": True},
    )
    project_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(spec),
        json={"cover_letter": "I can help"},
    )
    assert r.status_code == 201
    body = r.json()
    # On create, the response embeds the specialist preview
    assert body["specialist"]["full_name"] == "Applicant One"
    assert body["specialist"]["avatar_id"] == "cat:rose"
    assert body["specialist"]["categories"] == ["Backend"]

    # And on the customer list endpoint too
    r = await client.get(
        f"/api/v1/projects/{project_id}/applications", headers=_auth(cust)
    )
    items = r.json()
    assert len(items) == 1
    assert items[0]["specialist"]["full_name"] == "Applicant One"
    assert items[0]["specialist"]["avatar_id"] == "cat:rose"


@pytest.mark.asyncio
async def test_reviews_paged_with_project_titles(client):
    """Reviews endpoint returns Page[ReviewOut] with embedded project_title."""
    cust = await _register(client, "rev-cust@x.io", "customer")
    spec = await _register(client, "rev-spec@x.io", "specialist")
    await client.put(
        "/api/v1/specialists/me",
        headers=_auth(spec),
        json={
            "full_name": "Rev Spec", "age": 30, "categories": ["Backend"],
            "years_experience": 5, "bio": "",
        },
    )

    # Create + complete a project, then leave a review
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(cust),
        json={"title": "Reviewable project", "description": "x", "budget": 100, "publish": True},
    )
    project_id = r.json()["id"]
    await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(spec),
        json={"cover_letter": ""},
    )
    apps = (
        await client.get(
            f"/api/v1/projects/{project_id}/applications", headers=_auth(cust)
        )
    ).json()
    sid = apps[0]["specialist_id"]
    await client.post(
        f"/api/v1/projects/{project_id}/select-specialist/{sid}", headers=_auth(cust)
    )
    await client.post(f"/api/v1/projects/{project_id}/complete", headers=_auth(cust))

    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(cust),
        json={"rating": 5, "text": "great"},
    )
    assert r.status_code == 201
    assert r.json()["project_title"] == "Reviewable project"

    # List reviews — paginated shape with project_title
    r = await client.get(f"/api/v1/users/{sid}/reviews")
    body = r.json()
    assert "items" in body and "total" in body
    assert body["total"] == 1
    assert body["items"][0]["project_title"] == "Reviewable project"
    assert body["items"][0]["rating"] == 5
