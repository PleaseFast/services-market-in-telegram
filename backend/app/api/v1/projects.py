from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Header, Query, Response

from app.core.categories import clamp_category
from app.core.deps import CurrentUser, CurrentUserOptional, SessionDep
from app.core.i18n import parse_accept_language
from app.models.project import ProjectStatus
from app.models.user import UserRole
from app.repositories.projects import (
    get_project,
    list_open_projects,
    list_projects_for_customer,
    list_projects_for_specialist,
    list_templates_localized,
)
from app.repositories.specialists import get_profile_by_user
from app.schemas.common import Page
from app.schemas.project import (
    ProjectDetailOut,
    ProjectIn,
    ProjectOut,
    ProjectPatch,
    ProjectTemplateOut,
)
from app.services import projects as project_svc
from app.services.errors import NotFoundError
from app.services.project_views import record_view

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/templates", response_model=list[ProjectTemplateOut])
async def templates(
    session: SessionDep,
    viewer: CurrentUserOptional,
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
) -> list[ProjectTemplateOut]:
    lang = (viewer.language if viewer is not None else None) or parse_accept_language(
        accept_language
    )
    rows = await list_templates_localized(session, lang)
    return [
        ProjectTemplateOut(
            id=t.id,
            title=title,
            category=t.category,
            description_template=description,
        )
        for (t, title, description) in rows
    ]


@router.get("", response_model=Page[ProjectOut])
async def public_feed(
    session: SessionDep,
    viewer: CurrentUserOptional,
    q: str | None = Query(default=None, max_length=200),
    budget_min: Decimal | None = Query(default=None, ge=0),
    budget_max: Decimal | None = Query(default=None, ge=0),
    sort: Literal["newest", "viewed"] = Query(default="newest"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ProjectOut]:
    """Open-project feed.

    When the viewer is an authenticated specialist with a profile, the feed is
    automatically scoped to projects in any of the specialist's profile
    categories (no per-request category filter is exposed — specialists already
    chose them on their profile). Guests and customers see the full feed.

    ``sort="viewed"`` requires an authenticated viewer to be meaningful;
    otherwise it degrades to ``newest``.
    """
    viewer_categories: list[str] | None = None
    viewer_user_id: UUID | None = None
    if viewer is not None and viewer.role == UserRole.SPECIALIST:
        profile = await get_profile_by_user(session, viewer.id)
        if profile is not None:
            cats = [clamp_category(c) for c in profile.categories]
            # Dedupe in case clamp_category collapsed a few onto "Other".
            seen: set[str] = set()
            viewer_categories = [c for c in cats if not (c in seen or seen.add(c))]
            if not viewer_categories:
                viewer_categories = None
            viewer_user_id = viewer.id

    items, total = await list_open_projects(
        session,
        q=q,
        budget_min=budget_min,
        budget_max=budget_max,
        viewer_categories=viewer_categories,
        viewer_user_id=viewer_user_id,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[ProjectOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/mine/customer", response_model=Page[ProjectOut])
async def my_customer_projects(
    user: CurrentUser,
    session: SessionDep,
    status: ProjectStatus | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ProjectOut]:
    items, total = await list_projects_for_customer(
        session, user.id, statuses=[status] if status else None, limit=limit, offset=offset
    )
    return Page(
        items=[ProjectOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/mine/specialist", response_model=Page[ProjectOut])
async def my_specialist_projects(
    user: CurrentUser,
    session: SessionDep,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ProjectOut]:
    items, total = await list_projects_for_specialist(session, user.id, limit=limit, offset=offset)
    return Page(
        items=[ProjectOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ProjectOut, status_code=201)
async def create(payload: ProjectIn, user: CurrentUser, session: SessionDep) -> ProjectOut:
    p = await project_svc.create_project(session, user, payload)
    return ProjectOut.model_validate(p)


@router.get("/{project_id}", response_model=ProjectDetailOut)
async def detail(
    project_id: UUID,
    session: SessionDep,
    viewer: CurrentUserOptional,
) -> ProjectDetailOut:
    p = await get_project(session, project_id)
    if p is None or p.deleted_at is not None:
        raise NotFoundError("projects.not_found", message="Project not found")

    viewer_is_owner = viewer is not None and viewer.id == p.customer_id
    if p.status == ProjectStatus.PAUSED and not viewer_is_owner:
        raise NotFoundError("projects.not_found", message="Project not found")

    higher_rated: int | None = None
    if (
        viewer is not None
        and viewer.role == UserRole.SPECIALIST
        and viewer.id != p.customer_id
    ):
        # Best-effort view tracking — failures are swallowed inside record_view.
        await record_view(session, p.id, viewer.id)
        higher_rated = await project_svc.count_higher_rated_applicants(
            session, p.id, viewer.id
        )

    out = ProjectDetailOut.model_validate(p)
    out.higher_rated_applicants = higher_rated
    return out


@router.patch("/{project_id}", response_model=ProjectOut)
async def patch(project_id: UUID, payload: ProjectPatch, user: CurrentUser, session: SessionDep) -> ProjectOut:
    p = await project_svc.update_project(session, user, project_id, payload)
    return ProjectOut.model_validate(p)


@router.post("/{project_id}/publish", response_model=ProjectOut)
async def publish(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.publish_project(session, user, project_id))


@router.post("/{project_id}/select-specialist/{specialist_id}", response_model=ProjectOut)
async def select(
    project_id: UUID, specialist_id: UUID, user: CurrentUser, session: SessionDep
) -> ProjectOut:
    return ProjectOut.model_validate(
        await project_svc.select_specialist(session, user, project_id, specialist_id)
    )


@router.post("/{project_id}/complete", response_model=ProjectOut)
async def complete(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.complete_project(session, user, project_id))


@router.post("/{project_id}/archive", response_model=ProjectOut)
async def archive(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.archive_project(session, user, project_id))


@router.post("/{project_id}/cancel", response_model=ProjectOut)
async def cancel(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.cancel_project(session, user, project_id))


@router.post("/{project_id}/pause", response_model=ProjectOut)
async def pause(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.pause_project(session, user, project_id))


@router.post("/{project_id}/resume", response_model=ProjectOut)
async def resume(project_id: UUID, user: CurrentUser, session: SessionDep) -> ProjectOut:
    return ProjectOut.model_validate(await project_svc.resume_project(session, user, project_id))


@router.delete("/{project_id}", status_code=204, response_class=Response)
async def delete(project_id: UUID, user: CurrentUser, session: SessionDep) -> Response:
    await project_svc.delete_project(session, user, project_id)
    return Response(status_code=204)
