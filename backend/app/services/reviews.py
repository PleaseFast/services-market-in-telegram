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


def _rating_to_half(rating: float) -> int:
    """Convert a 0.0..5.0 step-0.5 float into a 0..10 integer."""
    return int(round(rating * 2))


async def _author_name(session: AsyncSession, author_id: UUID) -> str:
    """Best-effort display name for the review author.

    Specialists publish ``full_name``; customers publish ``display_name``.
    Both profile types are guaranteed to exist once the post-registration
    onboarding gate is in place, but we still fall back to "Anonymous" so
    legacy rows without a profile don't crash the response.
    """
    res = await session.execute(
        select(SpecialistProfile.full_name).where(SpecialistProfile.user_id == author_id)
    )
    name = res.scalar_one_or_none()
    if name:
        return name
    res = await session.execute(
        select(CustomerProfile.display_name).where(CustomerProfile.user_id == author_id)
    )
    name = res.scalar_one_or_none()
    return name or "Anonymous"


async def create_review(
    session: AsyncSession, user: User, project_id: UUID, rating: float, text: str | None
) -> Review:
    project = await get_project(session, project_id)
    if project is None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.status not in (ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED):
        raise ConflictError("reviews.project_not_completed", message="Project not completed")
    if user.id not in (project.customer_id, project.selected_specialist_id):
        raise ForbiddenError(
            "reviews.not_participant", message="You did not participate in this project"
        )
    subject_id = (
        project.selected_specialist_id
        if user.id == project.customer_id
        else project.customer_id
    )
    if subject_id is None:
        raise ConflictError("reviews.no_counterparty", message="No counterparty to review")

    review = Review(
        project_id=project_id,
        author_id=user.id,
        subject_id=subject_id,
        rating_half=_rating_to_half(rating),
        text=text,
    )
    session.add(review)
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        raise ConflictError(
            "reviews.duplicate", message="You already reviewed this project"
        ) from e

    await _recompute_rating(session, subject_id)
    await notify(
        session,
        subject_id,
        NotificationType.NEW_REVIEW,
        {"project_id": str(project_id), "rating": review.rating},
    )
    await session.commit()
    return review


async def list_for_subject(
    session: AsyncSession,
    subject_id: UUID,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[Review, str, str]], int]:
    """Return (review, project_title, author_name) triples + total.

    Author name is sourced from whichever profile row matches the author —
    specialist or customer. ``func.coalesce`` is portable across SQLite and
    Postgres.
    """
    spec_name = (
        select(SpecialistProfile.full_name)
        .where(SpecialistProfile.user_id == Review.author_id)
        .correlate(Review)
        .scalar_subquery()
    )
    cust_name = (
        select(CustomerProfile.display_name)
        .where(CustomerProfile.user_id == Review.author_id)
        .correlate(Review)
        .scalar_subquery()
    )
    author_label = func.coalesce(spec_name, cust_name, "Anonymous")

    base = (
        select(Review, Project.title, author_label)
        .join(Project, Project.id == Review.project_id)
        .where(Review.subject_id == subject_id)
    )
    total = await session.scalar(
        select(func.count())
        .select_from(
            select(Review.id).where(Review.subject_id == subject_id).subquery()
        )
    )
    res = await session.execute(
        base.order_by(Review.created_at.desc()).limit(limit).offset(offset)
    )
    return [(row[0], row[1], row[2]) for row in res.all()], int(total or 0)


async def _recompute_rating(session: AsyncSession, subject_id: UUID) -> None:
    subject = await session.get(User, subject_id)
    if subject is None:
        return
    res = await session.execute(
        select(func.avg(Review.rating_half), func.count(Review.id)).where(
            Review.subject_id == subject_id
        )
    )
    avg_half, count = res.one()
    avg_val = (Decimal(avg_half or 0) / Decimal(2)).quantize(Decimal("0.01"))
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
