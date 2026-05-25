from uuid import UUID

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.schemas.review import ReviewIn, ReviewOut
from app.services import reviews as svc

router = APIRouter(tags=["reviews"])


@router.post("/projects/{project_id}/reviews", response_model=ReviewOut, status_code=201)
async def create(
    project_id: UUID, payload: ReviewIn, user: CurrentUser, session: SessionDep
) -> ReviewOut:
    r = await svc.create_review(session, user, project_id, payload.rating, payload.text)
    return ReviewOut.model_validate(r)


@router.get("/users/{user_id}/reviews", response_model=list[ReviewOut])
async def list_reviews(user_id: UUID, session: SessionDep) -> list[ReviewOut]:
    return [ReviewOut.model_validate(r) for r in await svc.list_for_subject(session, user_id)]
