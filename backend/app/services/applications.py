from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.application import Application, ApplicationStatus, DirectOffer
from app.models.project import ProjectStatus
from app.models.user import User, UserRole
from app.repositories.projects import get_project
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.notifications import NotificationType, notify


async def apply(
    session: AsyncSession, user: User, project_id: UUID, cover_letter: str | None
) -> Application:
    if user.role != UserRole.SPECIALIST:
        raise ForbiddenError("applications.specialist_only", message="Only specialists can apply")
    project = await get_project(session, project_id)
    if project is None or project.deleted_at is not None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.status != ProjectStatus.OPEN:
        raise ConflictError(
            "applications.project_not_open", message="Project not open for applications"
        )
    application = Application(
        project_id=project_id,
        specialist_id=user.id,
        cover_letter=cover_letter,
    )
    session.add(application)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError(
            "applications.already_applied", message="Already applied to this project"
        ) from e

    await notify(
        session,
        project.customer_id,
        NotificationType.NEW_APPLICATION,
        {
            "project_id": str(project.id),
            "title": project.title,
            "application_id": str(application.id),
        },
    )
    await session.commit()
    return application


async def withdraw(session: AsyncSession, user: User, application_id: UUID) -> Application:
    app_row = await session.get(Application, application_id)
    if app_row is None:
        raise NotFoundError("applications.not_found", message="Application not found")
    if app_row.specialist_id != user.id:
        raise ForbiddenError("applications.not_yours", message="Not your application")
    if app_row.status != ApplicationStatus.PENDING:
        raise ConflictError(
            "applications.not_pending", message="Application is not pending"
        )
    app_row.status = ApplicationStatus.WITHDRAWN
    await session.commit()
    return app_row


async def list_for_project(session: AsyncSession, user: User, project_id: UUID) -> list[Application]:
    project = await get_project(session, project_id)
    if project is None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.customer_id != user.id:
        raise ForbiddenError("projects.not_yours", message="Not your project")
    res = await session.execute(
        select(Application).where(Application.project_id == project_id).order_by(Application.created_at)
    )
    return list(res.scalars().all())


# --- direct offers (customer -> specialist) ---

async def create_offer(
    session: AsyncSession, user: User, project_id: UUID, specialist_id: UUID, message: str | None
) -> DirectOffer:
    project = await get_project(session, project_id)
    if project is None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.customer_id != user.id:
        raise ForbiddenError("projects.not_yours", message="Not your project")
    offer = DirectOffer(project_id=project_id, specialist_id=specialist_id, message=message)
    session.add(offer)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError("offers.duplicate", message="Offer already exists") from e

    await notify(
        session,
        specialist_id,
        NotificationType.DIRECT_OFFER_RECEIVED,
        {"project_id": str(project.id), "title": project.title, "offer_id": str(offer.id)},
    )
    await session.commit()
    return offer


async def respond_to_offer(
    session: AsyncSession, user: User, offer_id: UUID, accept: bool
) -> DirectOffer:
    offer = await session.get(DirectOffer, offer_id)
    if offer is None:
        raise NotFoundError("offers.not_found", message="Offer not found")
    if offer.specialist_id != user.id:
        raise ForbiddenError("offers.not_yours", message="Not your offer")
    if offer.status != ApplicationStatus.PENDING:
        raise ConflictError("offers.already_answered", message="Offer already answered")
    offer.status = ApplicationStatus.ACCEPTED if accept else ApplicationStatus.REJECTED

    project = await get_project(session, offer.project_id)
    if project is None:
        raise NotFoundError("projects.not_found", message="Project gone")

    if accept and project.status == ProjectStatus.OPEN:
        # auto-create an accepted application + select specialist
        session.add(
            Application(
                project_id=project.id,
                specialist_id=user.id,
                status=ApplicationStatus.ACCEPTED,
                cover_letter=None,
            )
        )
        project.selected_specialist_id = user.id
        project.status = ProjectStatus.IN_PROGRESS

    await notify(
        session,
        project.customer_id,
        NotificationType.DIRECT_OFFER_ANSWERED,
        {"project_id": str(project.id), "accepted": accept, "specialist_id": str(user.id)},
    )
    await session.commit()
    return offer
