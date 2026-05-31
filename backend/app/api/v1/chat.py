"""Read-only chat-thread endpoints — give the frontend just enough metadata
to build a RefereeBot deep link straight into the right thread.

We deliberately do **not** expose message contents (the platform doesn't
persist them) or the counterparty's name beyond what the user already sees
elsewhere — only the routing primitive: which ChatThread is yours."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.core.deps import CurrentUser, SessionDep
from app.models.chat import ChatThread
from app.services.errors import NotFoundError

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatThreadOut(BaseModel):
    id: UUID
    project_id: UUID
    customer_id: UUID
    specialist_id: UUID
    closed: bool


@router.get("/projects/{project_id}/thread", response_model=ChatThreadOut)
async def get_project_thread(
    project_id: UUID, user: CurrentUser, session: SessionDep
) -> ChatThreadOut:
    """Return the thread for ``project_id`` involving the calling user.

    Membership is enforced by the WHERE clause — a customer or specialist
    only ever sees the thread they're a party to. Closed threads are still
    returned (the UI may still want to deep-link to view history; the bot
    will refuse further messages).
    """
    res = await session.execute(
        select(ChatThread).where(
            ChatThread.project_id == project_id,
            (ChatThread.customer_id == user.id) | (ChatThread.specialist_id == user.id),
        )
    )
    thread = res.scalar_one_or_none()
    if thread is None:
        raise NotFoundError("chat.thread_not_found", message="Thread not found")
    return ChatThreadOut(
        id=thread.id,
        project_id=thread.project_id,
        customer_id=thread.customer_id,
        specialist_id=thread.specialist_id,
        closed=thread.closed,
    )
