"""Idempotent demo-data loader. Run via `make seed`."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.profile import CustomerProfile, SpecialistProfile
from app.models.project import ProjectTemplate
from app.models.user import User, UserRole
from app.seed.templates import PROJECT_TEMPLATES

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")


DEMO_CUSTOMER_EMAIL = "customer@demo.local"
DEMO_SPECIALIST_EMAIL = "specialist@demo.local"
DEMO_PASSWORD = "demo1234!"


async def _seed_templates(session) -> None:
    existing = await session.execute(select(ProjectTemplate.title))
    seen = {row[0] for row in existing.all()}
    new = 0
    for t in PROJECT_TEMPLATES:
        if t["title"] in seen:
            continue
        session.add(
            ProjectTemplate(
                title=t["title"],
                category=t["category"],
                description_template=t.get("description_template", t.get("description_function", "")),
            )
        )
        new += 1
    log.info("Seeded %s project templates", new)


async def _seed_demo_users(session) -> None:
    res = await session.execute(select(User).where(User.email.in_([DEMO_CUSTOMER_EMAIL, DEMO_SPECIALIST_EMAIL])))
    existing_by_email = {u.email: u for u in res.scalars().all()}

    if DEMO_CUSTOMER_EMAIL not in existing_by_email:
        customer = User(
            email=DEMO_CUSTOMER_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.CUSTOMER,
        )
        session.add(customer)
        await session.flush()
        session.add(CustomerProfile(user_id=customer.id, display_name="Acme Inc."))
        log.info("Created demo customer %s / %s", DEMO_CUSTOMER_EMAIL, DEMO_PASSWORD)

    if DEMO_SPECIALIST_EMAIL not in existing_by_email:
        specialist = User(
            email=DEMO_SPECIALIST_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.SPECIALIST,
        )
        session.add(specialist)
        await session.flush()
        session.add(
            SpecialistProfile(
                user_id=specialist.id,
                full_name="Demo Specialist",
                age=29,
                category="Backend",
                years_experience=5,
                bio="Demo seeded specialist. Replace with real profile.",
            )
        )
        log.info("Created demo specialist %s / %s", DEMO_SPECIALIST_EMAIL, DEMO_PASSWORD)


async def main() -> None:
    async with SessionLocal() as session:
        await _seed_templates(session)
        await _seed_demo_users(session)
        await session.commit()
    log.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
