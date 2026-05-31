from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.categories import clamp_category, suggest_category
from app.models.application import Application, ApplicationStatus
from app.models.profile import SpecialistProfile
from app.models.project import Project, ProjectStatus, ProjectTemplate
from app.models.user import User, UserRole
from app.repositories.projects import get_project
from app.schemas.project import ProjectIn, ProjectPatch
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.notifications import NotificationType, notify


def _ensure_customer(user: User) -> None:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenError("projects.customer_only", message="Only customers can perform this action")


async def create_project(session: AsyncSession, user: User, data: ProjectIn) -> Project:
    _ensure_customer(user)
    category = await _resolve_category(
        session, template_id=data.template_id, requested=data.category,
        title=data.title, description=data.description,
    )
    now = datetime.now(timezone.utc)
    project = Project(
        customer_id=user.id,
        title=data.title,
        description=data.description,
        budget=data.budget,
        currency=data.currency,
        deadline=data.deadline,
        template_id=data.template_id,
        category=category,
        status=ProjectStatus.OPEN if data.publish else ProjectStatus.DRAFT,
        published_at=now if data.publish else None,
    )
    session.add(project)
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def _resolve_category(
    session: AsyncSession,
    *,
    template_id: UUID | None,
    requested: str | None,
    title: str,
    description: str,
) -> str:
    """Pick a category for a newly-created project.

    Precedence:
      1. ``template_id`` — copy from the template (clamped to closed set).
      2. ``requested`` — explicit value from the client (already Literal-validated
         when it arrived, but clamp defensively).
      3. Keyword-based ``suggest_category`` fallback.
    """
    if template_id is not None:
        tpl = await session.get(ProjectTemplate, template_id)
        if tpl is not None:
            return clamp_category(tpl.category)
    if requested:
        return clamp_category(requested)
    return suggest_category(title, description)


async def update_project(session: AsyncSession, user: User, project_id: UUID, patch: ProjectPatch) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status not in (ProjectStatus.DRAFT, ProjectStatus.OPEN, ProjectStatus.PAUSED):
        raise ConflictError(
            "projects.bad_state_edit",
            message="Only draft/open/paused projects can be edited",
        )
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def publish_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.DRAFT:
        raise ConflictError(
            "projects.bad_state_publish", message="Only draft projects can be published"
        )
    project.status = ProjectStatus.OPEN
    if project.published_at is None:
        project.published_at = datetime.now(timezone.utc)
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def select_specialist(
    session: AsyncSession, user: User, project_id: UUID, specialist_id: UUID
) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.OPEN:
        raise ConflictError("projects.not_open", message="Project not open")

    # Validate the specialist actually applied (or had a direct offer accepted)
    from sqlalchemy import select

    app_res = await session.execute(
        select(Application).where(
            Application.project_id == project_id, Application.specialist_id == specialist_id
        )
    )
    application = app_res.scalar_one_or_none()
    if application is None:
        raise ConflictError(
            "projects.specialist_did_not_apply",
            message="Specialist has not applied to this project",
        )

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
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def complete_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.IN_PROGRESS:
        raise ConflictError(
            "projects.not_in_progress", message="Project is not in progress"
        )
    project.status = ProjectStatus.COMPLETED
    if project.selected_specialist_id:
        await notify(
            session,
            project.selected_specialist_id,
            NotificationType.PROJECT_COMPLETED,
            {"project_id": str(project.id), "title": project.title},
        )
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def archive_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _project_visible_to(session, user, project_id)
    if project.status not in (ProjectStatus.COMPLETED, ProjectStatus.CANCELED):
        raise ConflictError(
            "projects.bad_state_archive",
            message="Only completed/canceled projects can be archived",
        )
    project.status = ProjectStatus.ARCHIVED
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def cancel_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status not in (ProjectStatus.DRAFT, ProjectStatus.OPEN, ProjectStatus.PAUSED):
        raise ConflictError(
            "projects.bad_state_cancel",
            message="Only draft/open/paused projects can be canceled",
        )
    project.status = ProjectStatus.CANCELED
    await session.commit()
    # ``onupdate=func.now()`` marks ``updated_at`` as expired post-UPDATE;
    # refresh so the sync ORM-read path (Pydantic model_validate) doesn't try
    # to lazy-load and trip MissingGreenlet.
    await session.refresh(project)
    return project


async def pause_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.OPEN:
        raise ConflictError(
            "projects.bad_state_pause", message="Only open projects can be paused"
        )
    project.status = ProjectStatus.PAUSED
    await session.commit()
    await session.refresh(project)
    return project


async def resume_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await _owned_project(session, user, project_id)
    if project.status != ProjectStatus.PAUSED:
        raise ConflictError(
            "projects.bad_state_resume", message="Only paused projects can be resumed"
        )
    project.status = ProjectStatus.OPEN
    await session.commit()
    await session.refresh(project)
    return project


_DELETABLE_STATUSES = (
    ProjectStatus.DRAFT,
    ProjectStatus.OPEN,
    ProjectStatus.PAUSED,
    ProjectStatus.CANCELED,
)


async def delete_project(session: AsyncSession, user: User, project_id: UUID) -> None:
    project = await _owned_project(session, user, project_id)
    if project.status not in _DELETABLE_STATUSES:
        raise ConflictError(
            "projects.bad_state_delete", message="Active projects cannot be deleted"
        )
    project.deleted_at = datetime.now(timezone.utc)
    await session.commit()


async def count_higher_rated_applicants(
    session: AsyncSession, project_id: UUID, viewer_user_id: UUID
) -> int:
    viewer_rating_res = await session.execute(
        select(SpecialistProfile.rating_avg).where(SpecialistProfile.user_id == viewer_user_id)
    )
    viewer_rating = viewer_rating_res.scalar_one_or_none() or 0
    count = await session.scalar(
        select(func.count())
        .select_from(Application)
        .join(SpecialistProfile, SpecialistProfile.user_id == Application.specialist_id)
        .where(
            Application.project_id == project_id,
            Application.status == ApplicationStatus.PENDING,
            Application.specialist_id != viewer_user_id,
            SpecialistProfile.rating_avg > viewer_rating,
        )
    )
    return int(count or 0)


# --- helpers ---

async def _owned_project(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await get_project(session, project_id)
    if project is None or project.deleted_at is not None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.customer_id != user.id:
        raise ForbiddenError("projects.not_yours", message="Not your project")
    return project


async def _project_visible_to(session: AsyncSession, user: User, project_id: UUID) -> Project:
    project = await get_project(session, project_id)
    if project is None or project.deleted_at is not None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if user.id not in (project.customer_id, project.selected_specialist_id):
        raise ForbiddenError("projects.not_visible", message="Not visible")
    return project
