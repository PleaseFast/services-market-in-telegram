from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.specialist_service import SpecialistService
from app.models.user import User, UserRole
from app.repositories.services import get_catalog_by_slugs
from app.repositories.specialists import get_profile_by_user
from app.schemas.services import SpecialistServicesReplace
from app.services.errors import ConflictError, DomainError, ForbiddenError


async def replace_services(
    session: AsyncSession, user: User, payload: SpecialistServicesReplace
) -> None:
    if user.role != UserRole.SPECIALIST:
        raise ForbiddenError("Only specialists manage services")
    profile = await get_profile_by_user(session, user.id)
    if profile is None:
        raise ConflictError("Create your specialist profile first")

    slugs = [item.slug for item in payload.items]
    if len(set(slugs)) != len(slugs):
        raise DomainError("Duplicate service slug in request")

    catalog = await get_catalog_by_slugs(session, slugs)
    missing = [s for s in slugs if s not in catalog]
    if missing:
        raise DomainError(f"Unknown service slugs: {', '.join(missing[:5])}")

    # Replace-all: delete existing, insert new.
    await session.execute(
        delete(SpecialistService).where(SpecialistService.profile_id == profile.id)
    )
    for position, item in enumerate(payload.items):
        catalog_row = catalog[item.slug]
        session.add(
            SpecialistService(
                profile_id=profile.id,
                service_id=catalog_row.id,
                price_amount=item.price_amount,
                price_currency=item.price_currency.upper(),
                position=position,
            )
        )
    await session.commit()
