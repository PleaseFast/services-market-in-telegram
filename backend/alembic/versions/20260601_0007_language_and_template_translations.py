"""user language column + project template translations

Adds ``users.language`` (default ``ru``) so we can persist a per-user
language preference, and a new ``project_template_translations`` table that
holds per-locale (title, description) for each canonical template row.

Revision ID: 0007_i18n_lang_templates
Revises: 0006_review_half_stars
Create Date: 2026-06-01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_i18n_lang_templates"
down_revision = "0006_review_half_stars"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.String(length=5),
            nullable=False,
            server_default="ru",
        ),
    )

    op.create_table(
        "project_template_translations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("project_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("locale", sa.String(length=5), nullable=False, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
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
        sa.UniqueConstraint("template_id", "locale", name="uq_template_locale"),
    )


def downgrade() -> None:
    op.drop_table("project_template_translations")
    op.drop_column("users", "language")
