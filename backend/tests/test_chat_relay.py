"""Unit-level coverage for the pure-routing chat_relay helpers.

These tests use the SQLite session fixture; they don't go through HTTP.
"""

from __future__ import annotations

import pytest

from app.models.chat import ChatParty, ChatThread
from app.models.profile import CustomerProfile, SpecialistProfile
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.services.chat_relay import (
    resolve_relay,
    validate_chat_deep_link,
)
from app.services.errors import ConflictError, ForbiddenError, NotFoundError


async def _seed_basic(session) -> tuple[User, User, User, Project, ChatThread]:
    customer = User(email="c@x", role=UserRole.CUSTOMER, password_hash="x")
    specialist = User(email="s@x", role=UserRole.SPECIALIST, password_hash="x")
    outsider = User(email="o@x", role=UserRole.SPECIALIST, password_hash="x")
    session.add_all([customer, specialist, outsider])
    await session.flush()
    session.add_all([
        CustomerProfile(user_id=customer.id, display_name="Cassie"),
        SpecialistProfile(
            user_id=specialist.id, full_name="Sam", age=30, years_experience=3, bio=""
        ),
    ])
    project = Project(
        customer_id=customer.id,
        title="API rewrite",
        description="x",
        budget=100,
        currency="USD",
        category="Backend",
        status=ProjectStatus.IN_PROGRESS,
        selected_specialist_id=specialist.id,
    )
    session.add(project)
    await session.flush()
    thread = ChatThread(
        project_id=project.id,
        customer_id=customer.id,
        specialist_id=specialist.id,
    )
    session.add(thread)
    await session.commit()
    await session.refresh(thread)
    return customer, specialist, outsider, project, thread


@pytest.mark.asyncio
async def test_resolve_relay_customer_to_specialist(session):
    customer, specialist, _outsider, project, thread = await _seed_basic(session)

    target = await resolve_relay(session, thread.id, customer)

    assert target.sender_party == ChatParty.CUSTOMER
    assert target.counterparty_user_id == specialist.id
    assert target.project.id == project.id
    assert target.sender_name == "Cassie"


@pytest.mark.asyncio
async def test_resolve_relay_specialist_to_customer(session):
    customer, specialist, _outsider, _project, thread = await _seed_basic(session)

    target = await resolve_relay(session, thread.id, specialist)

    assert target.sender_party == ChatParty.SPECIALIST
    assert target.counterparty_user_id == customer.id
    assert target.sender_name == "Sam"


@pytest.mark.asyncio
async def test_resolve_relay_rejects_outsider(session):
    _customer, _specialist, outsider, _project, thread = await _seed_basic(session)

    with pytest.raises(ForbiddenError):
        await resolve_relay(session, thread.id, outsider)


@pytest.mark.asyncio
async def test_resolve_relay_rejects_closed_thread(session):
    customer, _specialist, _outsider, _project, thread = await _seed_basic(session)
    thread.closed = True
    await session.commit()

    with pytest.raises(ConflictError):
        await resolve_relay(session, thread.id, customer)


@pytest.mark.asyncio
async def test_resolve_relay_unknown_thread(session):
    from uuid import uuid4

    customer = User(email="c2@x", role=UserRole.CUSTOMER, password_hash="x")
    session.add(customer)
    await session.commit()

    with pytest.raises(NotFoundError):
        await resolve_relay(session, uuid4(), customer)


# --- validate_chat_deep_link -------------------------------------------------

@pytest.mark.asyncio
async def test_deep_link_happy_path(session):
    _customer, specialist, _outsider, _project, thread = await _seed_basic(session)
    payload = f"chat_{thread.id}"

    result = await validate_chat_deep_link(session, payload, specialist.id)

    assert result is not None
    assert result.id == thread.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        None,
        "",
        "chat_",
        "chat_not-a-uuid",
        "open_thread:abc",
        "chat_123",
        "chatabc",
    ],
)
async def test_deep_link_rejects_malformed(session, payload):
    _customer, specialist, *_ = await _seed_basic(session)

    assert await validate_chat_deep_link(session, payload, specialist.id) is None


@pytest.mark.asyncio
async def test_deep_link_rejects_outsider(session):
    _customer, _specialist, outsider, _project, thread = await _seed_basic(session)
    payload = f"chat_{thread.id}"

    assert await validate_chat_deep_link(session, payload, outsider.id) is None


@pytest.mark.asyncio
async def test_deep_link_rejects_closed_thread(session):
    customer, _specialist, _outsider, _project, thread = await _seed_basic(session)
    thread.closed = True
    await session.commit()
    payload = f"chat_{thread.id}"

    assert await validate_chat_deep_link(session, payload, customer.id) is None


@pytest.mark.asyncio
async def test_deep_link_rejects_unknown_thread(session):
    from uuid import uuid4

    customer = User(email="c3@x", role=UserRole.CUSTOMER, password_hash="x")
    session.add(customer)
    await session.commit()

    assert await validate_chat_deep_link(session, f"chat_{uuid4()}", customer.id) is None
