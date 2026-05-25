from __future__ import annotations

import enum
import uuid

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Timestamps, UUIDPK


class ChatParty(str, enum.Enum):
    CUSTOMER = "customer"
    SPECIALIST = "specialist"


class ChatThread(UUIDPK, Timestamps, Base):
    __tablename__ = "chat_threads"
    __table_args__ = (
        UniqueConstraint("project_id", "customer_id", "specialist_id", name="uq_thread_triplet"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="chat_threads")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="thread", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(UUIDPK, Timestamps, Base):
    __tablename__ = "messages"

    thread_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_party: Mapped[ChatParty] = mapped_column(
        Enum(ChatParty, name="chat_party", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    thread: Mapped[ChatThread] = relationship(back_populates="messages")
