"""Idempotent demo-data loader. Run via `make seed`."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.core.service_catalog import SERVICE_CATALOG
from app.models.profile import (
    CustomerProfile,
    SpecialistProfile,
    SpecialistProfileCategory,
)
from app.models.project import ProjectTemplate, ProjectTemplateTranslation
from app.models.service_catalog import ServiceCatalogItem
from app.models.user import User, UserRole
from app.seed.templates import LOCALIZED_TEMPLATES, PROJECT_TEMPLATES

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")


DEMO_CUSTOMER_EMAIL = "customer@demo.local"
DEMO_SPECIALIST_EMAIL = "specialist@demo.local"
DEMO_PASSWORD = "demo1234!"


async def _seed_templates(session) -> None:
    """Insert canonical English templates and per-locale translations.

    Dedupes by English title. Re-running adds only newly-introduced rows and
    backfills any missing translations for existing rows.
    """
    res = await session.execute(select(ProjectTemplate))
    by_title: dict[str, ProjectTemplate] = {t.title: t for t in res.scalars().all()}

    new_canonical = 0
    for t in PROJECT_TEMPLATES:
        if t["title"] in by_title:
            continue
        row = ProjectTemplate(
            title=t["title"],
            category=t["category"],
            description_template=t.get("description_template", ""),
        )
        session.add(row)
        await session.flush()
        by_title[t["title"]] = row
        new_canonical += 1
    log.info("Seeded %s project templates", new_canonical)

    # Translations are keyed by (template_id, locale). Fetch existing pairs
    # once so re-runs only insert missing rows.
    existing = await session.execute(
        select(ProjectTemplateTranslation.template_id, ProjectTemplateTranslation.locale)
    )
    seen_pairs = {(tid, loc) for tid, loc in existing.all()}

    new_translations = 0
    en_titles = [t["title"] for t in LOCALIZED_TEMPLATES["en"]]
    for locale, rows in LOCALIZED_TEMPLATES.items():
        if len(rows) != len(en_titles):
            log.warning(
                "Locale %s has %s templates but en has %s — skipping mismatched tail",
                locale,
                len(rows),
                len(en_titles),
            )
        for idx, row in enumerate(rows):
            if idx >= len(en_titles):
                break
            canonical = by_title.get(en_titles[idx])
            if canonical is None:
                continue
            if (canonical.id, locale) in seen_pairs:
                continue
            session.add(
                ProjectTemplateTranslation(
                    template_id=canonical.id,
                    locale=locale,
                    title=row["title"],
                    description=row.get("description_template", ""),
                )
            )
            new_translations += 1
    log.info("Seeded %s template translations", new_translations)


async def _seed_service_catalog(session) -> None:
    existing = await session.execute(select(ServiceCatalogItem.slug))
    seen = {row[0] for row in existing.all()}
    new = 0
    for position, entry in enumerate(SERVICE_CATALOG):
        if entry.slug in seen:
            continue
        session.add(
            ServiceCatalogItem(
                slug=entry.slug,
                category=entry.category,
                subcategory=entry.subcategory,
                label=entry.label,
                position=position,
            )
        )
        new += 1
    log.info("Seeded %s service catalog items", new)


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
        profile = SpecialistProfile(
            user_id=specialist.id,
            full_name="Demo Specialist",
            age=29,
            years_experience=5,
            bio="Demo seeded specialist. Replace with real profile.",
        )
        session.add(profile)
        await session.flush()
        session.add(
            SpecialistProfileCategory(
                specialist_profile_id=profile.id, category="Backend"
            )
        )
        log.info("Created demo specialist %s / %s", DEMO_SPECIALIST_EMAIL, DEMO_PASSWORD)


async def main() -> None:
    async with SessionLocal() as session:
        await _seed_templates(session)
        await _seed_service_catalog(session)
        await _seed_demo_users(session)
        await session.commit()
    log.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
