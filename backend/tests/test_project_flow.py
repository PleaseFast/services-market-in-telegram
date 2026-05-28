import pytest


async def _register(client, email, role):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def _auth(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


@pytest.mark.asyncio
async def test_full_project_lifecycle(client):
    customer = await _register(client, "c@x.io", "customer")
    specialist = await _register(client, "s@x.io", "specialist")

    # specialist creates profile
    r = await client.put(
        "/api/v1/specialists/me",
        headers=_auth(specialist),
        json={
            "full_name": "Sam Sample",
            "age": 30,
            "category": "Backend",
            "years_experience": 7,
            "bio": "fixer of bugs",
        },
    )
    assert r.status_code == 200

    # customer creates a published project
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Build API", "description": "REST API", "budget": 5000, "publish": True},
    )
    assert r.status_code == 201, r.text
    project_id = r.json()["id"]

    # specialist applies
    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "pick me"},
    )
    assert r.status_code == 201, r.text

    # specialist cannot apply twice
    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "again"},
    )
    assert r.status_code == 409

    # customer sees the application
    r = await client.get(
        f"/api/v1/projects/{project_id}/applications", headers=_auth(customer)
    )
    assert r.status_code == 200
    apps = r.json()
    assert len(apps) == 1
    specialist_id = apps[0]["specialist_id"]

    # customer selects specialist
    r = await client.post(
        f"/api/v1/projects/{project_id}/select-specialist/{specialist_id}",
        headers=_auth(customer),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    # public feed should no longer contain the project
    r = await client.get("/api/v1/projects")
    assert all(p["id"] != project_id for p in r.json()["items"])

    # complete
    r = await client.post(
        f"/api/v1/projects/{project_id}/complete", headers=_auth(customer)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    # reviews (both directions)
    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(customer),
        json={"rating": 5, "text": "great"},
    )
    assert r.status_code == 201
    r = await client.post(
        f"/api/v1/projects/{project_id}/reviews",
        headers=_auth(specialist),
        json={"rating": 4, "text": "good client"},
    )
    assert r.status_code == 201

    # archive
    r = await client.post(
        f"/api/v1/projects/{project_id}/archive", headers=_auth(customer)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "archived"
