from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatThread


async def get_thread(session: AsyncSession, thread_id: UUID) -> ChatThread | None:
    return await session.get(ChatThread, thread_id, options=[selectinload(ChatThread.messages)])


async def list_threads_for_project(session: AsyncSession, project_id: UUID) -> list[ChatThread]:
    res = await session.execute(
        select(ChatThread).where(ChatThread.project_id == project_id).order_by(ChatThread.created_at)
    )
    return list(res.scalars().all())


async def find_thread(
    session: AsyncSession, project_id: UUID, customer_id: UUID, specialist_id: UUID
) -> ChatThread | None:
    res = await session.execute(
        select(ChatThread).where(
            ChatThread.project_id == project_id,
            ChatThread.customer_id == customer_id,
            ChatThread.specialist_id == specialist_id,
        )
    )
    return res.scalar_one_or_none()
