from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service_catalog import ServiceCatalogItem
from app.models.specialist_service import SpecialistService
from app.schemas.services import SpecialistServiceOut


async def list_catalog(session: AsyncSession) -> list[ServiceCatalogItem]:
    res = await session.execute(
        select(ServiceCatalogItem).order_by(
            asc(ServiceCatalogItem.category),
            asc(ServiceCatalogItem.subcategory),
            asc(ServiceCatalogItem.position),
            asc(ServiceCatalogItem.label),
        )
    )
    return list(res.scalars().all())


async def get_catalog_by_slugs(
    session: AsyncSession, slugs: list[str]
) -> dict[str, ServiceCatalogItem]:
    if not slugs:
        return {}
    res = await session.execute(
        select(ServiceCatalogItem).where(ServiceCatalogItem.slug.in_(slugs))
    )
    return {item.slug: item for item in res.scalars().all()}


async def list_for_profile(
    session: AsyncSession, profile_id: UUID
) -> list[SpecialistServiceOut]:
    """Return hydrated rows (joined with the catalog) for public consumption."""
    res = await session.execute(
        select(SpecialistService, ServiceCatalogItem)
        .join(ServiceCatalogItem, ServiceCatalogItem.id == SpecialistService.service_id)
        .where(SpecialistService.profile_id == profile_id)
        .order_by(
            asc(ServiceCatalogItem.category),
            asc(ServiceCatalogItem.subcategory),
            asc(SpecialistService.position),
            asc(ServiceCatalogItem.label),
        )
    )
    out: list[SpecialistServiceOut] = []
    for binding, catalog in res.all():
        out.append(
            SpecialistServiceOut(
                service_id=catalog.id,
                slug=catalog.slug,
                category=catalog.category,
                subcategory=catalog.subcategory,
                label=catalog.label,
                price_amount=binding.price_amount,
                price_currency=binding.price_currency,
                position=binding.position,
            )
        )
    return out


async def list_for_profiles(
    session: AsyncSession, profile_ids: list[UUID]
) -> dict[UUID, list[SpecialistServiceOut]]:
    """Bulk variant for the public list endpoint."""
    if not profile_ids:
        return {}
    res = await session.execute(
        select(SpecialistService, ServiceCatalogItem)
        .join(ServiceCatalogItem, ServiceCatalogItem.id == SpecialistService.service_id)
        .where(SpecialistService.profile_id.in_(profile_ids))
        .order_by(
            asc(ServiceCatalogItem.category),
            asc(ServiceCatalogItem.subcategory),
            asc(SpecialistService.position),
        )
    )
    out: dict[UUID, list[SpecialistServiceOut]] = {pid: [] for pid in profile_ids}
    for binding, catalog in res.all():
        out[binding.profile_id].append(
            SpecialistServiceOut(
                service_id=catalog.id,
                slug=catalog.slug,
                category=catalog.category,
                subcategory=catalog.subcategory,
                label=catalog.label,
                price_amount=binding.price_amount,
                price_currency=binding.price_currency,
                position=binding.position,
            )
        )
    return out
