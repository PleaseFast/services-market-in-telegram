from uuid import UUID

from fastapi import APIRouter, Query

from app.core.deps import CurrentUser, SessionDep
from app.repositories.projects import get_project
from app.schemas.common import Page
from app.schemas.review import ReviewIn, ReviewOut
from app.services import reviews as svc

router = APIRouter(tags=["reviews"])


@router.post("/projects/{project_id}/reviews", response_model=ReviewOut, status_code=201)
async def create(
    project_id: UUID, payload: ReviewIn, user: CurrentUser, session: SessionDep
) -> ReviewOut:
    r = await svc.create_review(session, user, project_id, payload.rating, payload.text)
    project = await get_project(session, project_id)
    author_name = await svc._author_name(session, r.author_id)
    return ReviewOut(
        id=r.id,
        project_id=r.project_id,
        project_title=project.title if project else "",
        author_id=r.author_id,
        author_name=author_name,
        subject_id=r.subject_id,
        rating=r.rating,
        text=r.text,
        created_at=r.created_at,
    )


@router.get("/users/{user_id}/reviews", response_model=Page[ReviewOut])
async def list_reviews(
    user_id: UUID,
    session: SessionDep,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ReviewOut]:
    items, total = await svc.list_for_subject(session, user_id, limit=limit, offset=offset)
    return Page(
        items=[
            ReviewOut(
                id=r.id,
                project_id=r.project_id,
                project_title=title,
                author_id=r.author_id,
                author_name=author_name,
                subject_id=r.subject_id,
                rating=r.rating,
                text=r.text,
                created_at=r.created_at,
            )
            for r, title, author_name in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
