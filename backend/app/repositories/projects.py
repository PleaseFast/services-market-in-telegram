from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import (
    Project,
    ProjectStatus,
    ProjectTemplate,
    ProjectTemplateTranslation,
)
from app.models.project_view import ProjectView

SortMode = Literal["newest", "viewed"]


async def get_project(session: AsyncSession, project_id: UUID) -> Project | None:
    return await session.get(Project, project_id)


async def list_open_projects(
    session: AsyncSession,
    *,
    q: str | None = None,
    budget_min: Decimal | None = None,
    budget_max: Decimal | None = None,
    viewer_categories: list[str] | None = None,
    viewer_user_id: UUID | None = None,
    sort: SortMode = "newest",
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Project], int]:
    stmt = select(Project).where(
        Project.status == ProjectStatus.OPEN, Project.deleted_at.is_(None)
    )
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Project.title.ilike(like), Project.description.ilike(like)))
    if budget_min is not None:
        stmt = stmt.where(Project.budget >= budget_min)
    if budget_max is not None:
        stmt = stmt.where(Project.budget <= budget_max)
    if viewer_categories:
        stmt = stmt.where(Project.category.in_(viewer_categories))

    # Count BEFORE the order_by/limit/offset.
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )

    if sort == "viewed" and viewer_user_id is not None:
        stmt = stmt.outerjoin(
            ProjectView,
            and_(
                ProjectView.project_id == Project.id,
                ProjectView.user_id == viewer_user_id,
            ),
        ).order_by(
            ProjectView.last_viewed_at.desc().nulls_last(),
            Project.created_at.desc(),
        )
    else:
        stmt = stmt.order_by(Project.created_at.desc())

    res = await session.execute(stmt.limit(limit).offset(offset))
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


async def list_open_by_customer(
    session: AsyncSession,
    customer_id: UUID,
    *,
    limit: int = 20,
) -> list[Project]:
    """Open (published) projects owned by a customer.

    Used by the embedded customer info block on a project page so a viewer
    can see what else this customer currently has on offer. Sorted by the
    publish time so the freshest listings appear first.
    """
    stmt = (
        select(Project)
        .where(
            Project.customer_id == customer_id,
            Project.status == ProjectStatus.OPEN,
            Project.deleted_at.is_(None),
        )
        .order_by(Project.published_at.desc().nulls_last(), Project.created_at.desc())
        .limit(limit)
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


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


async def list_templates_localized(
    session: AsyncSession, lang: str
) -> list[tuple[ProjectTemplate, str, str]]:
    """Return (template, localized_title, localized_description) triples.

    Falls back to the canonical English row when a translation for ``lang``
    isn't seeded yet — that way the API never returns blanks even mid-rollout.
    """
    res = await session.execute(
        select(ProjectTemplate).order_by(ProjectTemplate.category, ProjectTemplate.title)
    )
    templates = list(res.scalars().all())
    if not templates:
        return []
    ids = [t.id for t in templates]
    tres = await session.execute(
        select(ProjectTemplateTranslation).where(
            ProjectTemplateTranslation.template_id.in_(ids),
            ProjectTemplateTranslation.locale == lang,
        )
    )
    by_id = {tr.template_id: tr for tr in tres.scalars().all()}
    out: list[tuple[ProjectTemplate, str, str]] = []
    for t in templates:
        tr = by_id.get(t.id)
        if tr is not None:
            out.append((t, tr.title, tr.description))
        else:
            out.append((t, t.title, t.description_template))
    return out
