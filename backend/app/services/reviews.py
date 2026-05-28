from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import CustomerProfile, SpecialistProfile
from app.models.project import Project, ProjectStatus
from app.models.review import Review
from app.models.user import User, UserRole
from app.repositories.projects import get_project
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.notifications import NotificationType, notify


async def create_review(
    session: AsyncSession, user: User, project_id: UUID, rating: int, text: str | None
) -> Review:
    project = await get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project not found")
    if project.status not in (ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED):
        raise ConflictError("Project not completed")
    if user.id not in (project.customer_id, project.selected_specialist_id):
        raise ForbiddenError("You did not participate in this project")
    subject_id = (
        project.selected_specialist_id
        if user.id == project.customer_id
        else project.customer_id
    )
    if subject_id is None:
        raise ConflictError("No counterparty to review")

    review = Review(
        project_id=project_id,
        author_id=user.id,
        subject_id=subject_id,
        rating=rating,
        text=text,
    )
    session.add(review)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError("You already reviewed this project") from e

    await _recompute_rating(session, subject_id)
    await notify(
        session,
        subject_id,
        NotificationType.NEW_REVIEW,
        {"project_id": str(project_id), "rating": rating},
    )
    await session.commit()
    return review


async def list_for_subject(
    session: AsyncSession,
    subject_id: UUID,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[Review, str]], int]:
    """Return (review, project_title) pairs and the total count for paging.

    Joining Project here keeps the response self-contained — the public
    reviews block doesn't need a second round-trip per row to fetch titles.
    """
    base = (
        select(Review, Project.title)
        .join(Project, Project.id == Review.project_id)
        .where(Review.subject_id == subject_id)
    )
    total = await session.scalar(select(func.count()).select_from(base.order_by(None).subquery()))
    res = await session.execute(
        base.order_by(Review.created_at.desc()).limit(limit).offset(offset)
    )
    return [(row[0], row[1]) for row in res.all()], int(total or 0)


async def _recompute_rating(session: AsyncSession, subject_id: UUID) -> None:
    subject = await session.get(User, subject_id)
    if subject is None:
        return
    res = await session.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.subject_id == subject_id)
    )
    avg, count = res.one()
    avg_val = Decimal(avg or 0).quantize(Decimal("0.01"))
    count_val = int(count or 0)

    if subject.role == UserRole.SPECIALIST:
        res2 = await session.execute(
            select(SpecialistProfile).where(SpecialistProfile.user_id == subject_id)
        )
        profile = res2.scalar_one_or_none()
        if profile:
            profile.rating_avg = avg_val
            profile.rating_count = count_val
    else:
        res2 = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == subject_id)
        )
        profile = res2.scalar_one_or_none()
        if profile:
            profile.rating_avg = avg_val
            profile.rating_count = count_val
