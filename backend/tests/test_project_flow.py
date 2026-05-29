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
            "categories": ["Backend"],
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


@pytest.mark.asyncio
async def test_pause_resume_hides_from_specialists(client):
    customer = await _register(client, "c.pause@x.io", "customer")
    specialist = await _register(client, "s.pause@x.io", "specialist")

    await client.put(
        "/api/v1/specialists/me",
        headers=_auth(specialist),
        json={
            "full_name": "Pat Pause",
            "age": 30,
            "categories": ["Backend"],
            "years_experience": 5,
            "bio": "",
        },
    )

    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Pause Test", "description": "REST API", "budget": 1000, "publish": True},
    )
    assert r.status_code == 201
    body = r.json()
    project_id = body["id"]
    published_at = body["published_at"]
    assert published_at is not None

    # pause
    r = await client.post(f"/api/v1/projects/{project_id}/pause", headers=_auth(customer))
    assert r.status_code == 200
    assert r.json()["status"] == "paused"

    # specialist feed excludes paused
    r = await client.get("/api/v1/projects", headers=_auth(specialist))
    assert r.status_code == 200
    assert all(p["id"] != project_id for p in r.json()["items"])

    # specialist detail 404 for paused
    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(specialist))
    assert r.status_code == 404

    # customer can still see paused
    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(customer))
    assert r.status_code == 200
    assert r.json()["status"] == "paused"

    # apply rejected while paused
    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "no"},
    )
    assert r.status_code == 409

    # edit while paused is allowed
    r = await client.patch(
        f"/api/v1/projects/{project_id}",
        headers=_auth(customer),
        json={"title": "Pause Test Edited"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Pause Test Edited"

    # resume
    r = await client.post(f"/api/v1/projects/{project_id}/resume", headers=_auth(customer))
    assert r.status_code == 200
    assert r.json()["status"] == "open"
    # published_at unchanged
    assert r.json()["published_at"] == published_at

    # specialist can now apply
    r = await client.post(
        f"/api/v1/projects/{project_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": "yes"},
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_delete_project_rules(client):
    customer = await _register(client, "c.del@x.io", "customer")
    specialist = await _register(client, "s.del@x.io", "specialist")

    await client.put(
        "/api/v1/specialists/me",
        headers=_auth(specialist),
        json={
            "full_name": "Del Specialist",
            "age": 30,
            "categories": ["Backend"],
            "years_experience": 5,
            "bio": "",
        },
    )

    # delete a DRAFT
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Draft One", "description": "x", "budget": 100, "publish": False},
    )
    draft_id = r.json()["id"]
    r = await client.delete(f"/api/v1/projects/{draft_id}", headers=_auth(customer))
    assert r.status_code == 204
    r = await client.get(f"/api/v1/projects/{draft_id}", headers=_auth(customer))
    assert r.status_code == 404

    # cannot delete an IN_PROGRESS project
    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Active", "description": "x", "budget": 100, "publish": True},
    )
    active_id = r.json()["id"]
    r = await client.post(
        f"/api/v1/projects/{active_id}/applications",
        headers=_auth(specialist),
        json={"cover_letter": ""},
    )
    assert r.status_code == 201
    apps = (await client.get(
        f"/api/v1/projects/{active_id}/applications", headers=_auth(customer)
    )).json()
    sid = apps[0]["specialist_id"]
    r = await client.post(
        f"/api/v1/projects/{active_id}/select-specialist/{sid}",
        headers=_auth(customer),
    )
    assert r.status_code == 200
    r = await client.delete(f"/api/v1/projects/{active_id}", headers=_auth(customer))
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_higher_rated_applicants_counter(client, session):
    from decimal import Decimal
    from uuid import UUID

    from app.models.profile import SpecialistProfile

    customer = await _register(client, "c.rate@x.io", "customer")
    viewer = await _register(client, "viewer.rate@x.io", "specialist")
    higher_a = await _register(client, "ha.rate@x.io", "specialist")
    higher_b = await _register(client, "hb.rate@x.io", "specialist")
    lower = await _register(client, "low.rate@x.io", "specialist")

    async def _profile(tok, full_name):
        r = await client.put(
            "/api/v1/specialists/me",
            headers=_auth(tok),
            json={
                "full_name": full_name,
                "age": 30,
                "categories": ["Backend"],
                "years_experience": 5,
                "bio": "",
            },
        )
        assert r.status_code == 200
        return UUID(r.json()["user_id"])

    viewer_id = await _profile(viewer, "Viewer")
    higher_a_id = await _profile(higher_a, "Higher A")
    higher_b_id = await _profile(higher_b, "Higher B")
    lower_id = await _profile(lower, "Lower")

    async def _set_rating(user_id: UUID, rating: float) -> None:
        from sqlalchemy import update
        await session.execute(
            update(SpecialistProfile)
            .where(SpecialistProfile.user_id == user_id)
            .values(rating_avg=Decimal(str(rating)), rating_count=1)
        )
        await session.commit()

    await _set_rating(viewer_id, 4.6)
    await _set_rating(higher_a_id, 4.8)
    await _set_rating(higher_b_id, 4.9)
    await _set_rating(lower_id, 4.0)

    r = await client.post(
        "/api/v1/projects",
        headers=_auth(customer),
        json={"title": "Rating Test", "description": "x", "budget": 100, "publish": True},
    )
    assert r.status_code == 201
    project_id = r.json()["id"]

    for tok in (higher_a, higher_b, lower):
        r = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            headers=_auth(tok),
            json={"cover_letter": ""},
        )
        assert r.status_code == 201

    # viewer hasn't applied yet — sees 2 higher-rated applicants
    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(viewer))
    assert r.status_code == 200
    body = r.json()
    assert body["higher_rated_applicants"] == 2
    assert body["published_at"] is not None

    # customer detail doesn't include the count
    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(customer))
    assert r.status_code == 200
    assert r.json()["higher_rated_applicants"] is None
