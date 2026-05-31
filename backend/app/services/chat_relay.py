from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatParty, ChatThread, Message
from app.models.project import ProjectStatus
from app.models.user import User
from app.repositories.chat import find_thread, get_thread
from app.repositories.projects import get_project
from app.services.errors import ConflictError, ForbiddenError, NotFoundError


async def get_or_open_thread(
    session: AsyncSession, project_id: UUID, customer_id: UUID, specialist_id: UUID
) -> ChatThread:
    project = await get_project(session, project_id)
    if project is None:
        raise NotFoundError("projects.not_found", message="Project not found")
    if project.customer_id != customer_id:
        raise ForbiddenError("chat.customer_mismatch", message="Customer mismatch")
    if project.status not in (ProjectStatus.OPEN, ProjectStatus.IN_PROGRESS):
        raise ConflictError("chat.project_closed", message="Project closed to chat")

    thread = await find_thread(session, project_id, customer_id, specialist_id)
    if thread is None:
        thread = ChatThread(
            project_id=project_id, customer_id=customer_id, specialist_id=specialist_id
        )
        session.add(thread)
        await session.commit()
        await session.refresh(thread)
    return thread


async def post_message(
    session: AsyncSession,
    thread_id: UUID,
    sender_user: User,
    body: str,
    tg_message_id: int | None = None,
) -> tuple[Message, ChatThread, ChatParty, UUID]:
    """Persist a message in a thread; returns (message, thread, sender_party, counterparty_user_id)."""
    thread = await get_thread(session, thread_id)
    if thread is None:
        raise NotFoundError("chat.thread_not_found", message="Thread not found")
    if thread.closed:
        raise ConflictError("chat.thread_closed", message="Thread is closed")

    if sender_user.id == thread.customer_id:
        party = ChatParty.CUSTOMER
        counterparty = thread.specialist_id
    elif sender_user.id == thread.specialist_id:
        party = ChatParty.SPECIALIST
        counterparty = thread.customer_id
    else:
        raise ForbiddenError("chat.not_member", message="Not a member of this thread")

    msg = Message(thread_id=thread.id, sender_party=party, body=body, tg_message_id=tg_message_id)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg, thread, party, counterparty
