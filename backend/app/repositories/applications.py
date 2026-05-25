from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, DirectOffer


async def list_applications_for_project(session: AsyncSession, project_id: UUID) -> list[Application]:
    res = await session.execute(
        select(Application).where(Application.project_id == project_id).order_by(Application.created_at)
    )
    return list(res.scalars().all())


async def get_application(session: AsyncSession, application_id: UUID) -> Application | None:
    return await session.get(Application, application_id)


async def get_offer(session: AsyncSession, offer_id: UUID) -> DirectOffer | None:
    return await session.get(DirectOffer, offer_id)


async def list_offers_for_specialist(session: AsyncSession, specialist_id: UUID) -> list[DirectOffer]:
    res = await session.execute(
        select(DirectOffer).where(DirectOffer.specialist_id == specialist_id).order_by(DirectOffer.created_at.desc())
    )
    return list(res.scalars().all())
