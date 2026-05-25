from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus, ProjectTemplate


async def get_project(session: AsyncSession, project_id: UUID) -> Project | None:
    return await session.get(Project, project_id)


async def list_open_projects(
    session: AsyncSession,
    *,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Project], int]:
    stmt = select(Project).where(Project.status == ProjectStatus.OPEN, Project.deleted_at.is_(None))
    if category:
        # join templates for category match if template was used; also allow substring on title
        stmt = stmt.where(
            or_(Project.title.ilike(f"%{category}%"), Project.description.ilike(f"%{category}%"))
        )

    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    res = await session.execute(stmt.order_by(Project.created_at.desc()).limit(limit).offset(offset))
    return list(res.scalars().all()), int(total or 0)


async def list_projects_for_customer(
    session: AsyncSession,
    customer_id: UUID,
    *,
    statuses: list[ProjectStatus] | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Project], int]:
    stmt = select(Project).where(Project.customer_id == customer_id, Project.deleted_at.is_(None))
    if statuses:
        stmt = stmt.where(Project.status.in_(statuses))
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    res = await session.execute(stmt.order_by(Project.created_at.desc()).limit(limit).offset(offset))
    return list(res.scalars().all()), int(total or 0)


async def list_projects_for_specialist(
    session: AsyncSession,
    specialist_id: UUID,
    *,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Project], int]:
    stmt = select(Project).where(
        and_(Project.selected_specialist_id == specialist_id, Project.deleted_at.is_(None))
    )
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    res = await session.execute(stmt.order_by(Project.created_at.desc()).limit(limit).offset(offset))
    return list(res.scalars().all()), int(total or 0)


async def list_templates(session: AsyncSession) -> list[ProjectTemplate]:
    res = await session.execute(select(ProjectTemplate).order_by(ProjectTemplate.category, ProjectTemplate.title))
    return list(res.scalars().all())
