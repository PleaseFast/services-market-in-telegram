"""drop messages table; add referee activation columns

Removes the ``messages`` table entirely — RefereeBot now relays Telegram
messages without persisting their bodies (see ``services/relay_queue.py`` for
the short-lived Redis buffer used when the counterpart hasn't started the bot
yet).

Adds two columns to ``telegram_accounts`` to track whether and when the user
opened RefereeBot specifically, so the relay loop can know whether direct
delivery is possible (a Telegram bot cannot DM a user who has never tapped
"Start" on it).

Revision ID: 0008_drop_msgs_referee_act
Revises: 0007_i18n_lang_templates
Create Date: 2026-05-31
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008_drop_msgs_referee_act"
down_revision = "0007_i18n_lang_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("messages")
    sa.Enum(name="chat_party").drop(op.get_bind(), checkfirst=True)

    op.add_column(
        "telegram_accounts",
        sa.Column("referee_chat_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "telegram_accounts",
        sa.Column("referee_activated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("telegram_accounts", "referee_activated_at")
    op.drop_column("telegram_accounts", "referee_chat_id")

    from sqlalchemy.dialects import postgresql

    chat_party = postgresql.ENUM(
        "customer", "specialist", name="chat_party", create_type=False
    )
    chat_party.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "thread_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chat_threads.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("sender_party", chat_party, nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tg_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
