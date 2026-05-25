from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.repositories.projects import get_project
from app.schemas.project import ProjectIn, ProjectPatch
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.notifications import NotificationType, notify


def _ensure_customer(user: User) -> None:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenError("Only customers can perform this action")


async def create_project(session: AsyncSession, user: User, data: ProjectIn) -> Project:
    _ensure_customer(user)
    project = Project(
        customer_id=user.id,
        title=data.title,
        description=data.description,
        budget=data.budget,
        currency=data.currency,
        deadline=data.deadline,
        template_id=data.template_id,
        status=ProjectStatus.OPEN if data.publish else ProjectStatus.DRAFT,
    )
    session.add(project)
    await session.commit()
    return project


async def update_project(session: AsyncSession, user: User, project_id: UUID, patch: ProjectPatch) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status not in (ProjectStatus.DRAFT, ProjectStatus.OPEN):
        raise ConflictError("Only draft/open projects can be edited")
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await session.commit()
    return project


async def publish_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.DRAFT:
        raise ConflictError("Only draft projects can be published")
    project.status = ProjectStatus.OPEN
    await session.commit()
    return project


async def select_specialist(
    session: AsyncSession, user: User, project_id: UUID, specialist_id: UUID
) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.OPEN:
        raise ConflictError("Project not open")

    # Validate the specialist actually applied (or had a direct offer accepted)
    from sqlalchemy import select

    app_res = await session.execute(
        select(Application).where(
            Application.project_id == project_id, Application.specialist_id == specialist_id
        )
    )
    application = app_res.scalar_one_or_none()
    if application is None:
        raise ConflictError("Specialist has not applied to this project")

    # Mark selected; reject others; close other chat threads
    application.status = ApplicationStatus.ACCEPTED
    project.selected_specialist_id = specialist_id
    project.status = ProjectStatus.IN_PROGRESS

    others = await session.execute(
        select(Application).where(
            Application.project_id == project_id,
            Application.specialist_id != specialist_id,
            Application.status == ApplicationStatus.PENDING,
        )
    )
    for other in others.scalars().all():
        other.status = ApplicationStatus.REJECTED
        await notify(
            session,
            other.specialist_id,
            NotificationType.APPLICATION_REJECTED,
            {"project_id": str(project_id), "title": project.title},
        )

    from app.models.chat import ChatThread

    threads = await session.execute(select(ChatThread).where(ChatThread.project_id == project_id))
    for t in threads.scalars().all():
        if t.specialist_id != specialist_id:
            t.closed = True

    await notify(
        session,
        specialist_id,
        NotificationType.APPLICATION_ACCEPTED,
        {"project_id": str(project_id), "title": project.title},
    )
    await notify(
        session,
        user.id,
        NotificationType.SPECIALIST_SELECTED,
        {"project_id": str(project_id), "specialist_id": str(specialist_id)},
    )
    await session.commit()
    return project


async def complete_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.IN_PROGRESS:
        raise ConflictError("Project is not in progress")
    project.status = ProjectStatus.COMPLETED
    if project.selected_specialist_id:
        await notify(
            session,
            project.selected_specialist_id,
            NotificationType.PROJECT_COMPLETED,
            {"project_id": str(project.id), "title": project.title},
        )
    await session.commit()
    return project


async def archive_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _project_visible_to(session, user, project_id)
    if project.status not in (ProjectStatus.COMPLETED, ProjectStatus.CANCELED):
        raise ConflictError("Only completed/canceled projects can be archived")
    project.status = ProjectStatus.ARCHIVED
    await session.commit()
    return project


async def cancel_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status not in (ProjectStatus.DRAFT, ProjectStatus.OPEN):
        raise ConflictError("Only draft/open projects can be canceled")
    project.status = ProjectStatus.CANCELED
    await session.commit()
    return project


# --- helpers ---

async def _owned_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await get_project(session, project_id)
    if project is None or project.deleted_at is not None:
        raise NotFoundError("Project not found")
    if project.customer_id != user.id:
        raise ForbiddenError("Not your project")
    return project


async def _project_visible_to(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await get_project(session, project_id)
    if project is None or project.deleted_at is not None:
        raise NotFoundError("Project not found")
    if user.id not in (project.customer_id, project.selected_specialist_id):
        raise ForbiddenError("Not visible")
    return project
