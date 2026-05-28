"""project category column, project_views, normalize profile category

Revision ID: 0002_project_category_and_views
Revises: 0001_initial
Create Date: 2026-05-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_project_category_and_views"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


CATEGORIES = (
    "Frontend",
    "Backend",
    "Bots",
    "Mobile",
    "DevOps",
    "Data",
    "Design",
    "AI",
    "Other",
)


def upgrade() -> None:
    # --- projects.category --------------------------------------------------
    op.add_column(
        "projects",
        sa.Column("category", sa.String(40), nullable=False, server_default="Other"),
    )
    op.create_index("ix_projects_category", "projects", ["category"])

    # Backfill from project_templates.category, clamped to the closed set.
    op.execute(
        sa.text(
            """
            UPDATE projects p
            SET category = pt.category
            FROM project_templates pt
            WHERE p.template_id = pt.id
              AND pt.category IN :cats
            """
        ).bindparams(sa.bindparam("cats", expanding=True, value=list(CATEGORIES)))
    )
    # Anything still outside the closed set (shouldn't happen now, but defensive)
    op.execute(
        sa.text(
            """
            UPDATE projects
            SET category = 'Other'
            WHERE category NOT IN :cats
            """
        ).bindparams(sa.bindparam("cats", expanding=True, value=list(CATEGORIES)))
    )

    # --- specialist_profiles.category normalization -------------------------
    op.execute(
        sa.text(
            """
            UPDATE specialist_profiles
            SET category = 'Other'
            WHERE category NOT IN :cats
            """
        ).bindparams(sa.bindparam("cats", expanding=True, value=list(CATEGORIES)))
    )

    # --- project_views ------------------------------------------------------
    op.create_table(
        "project_views",
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "first_viewed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_viewed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_project_views_user_last_viewed",
        "project_views",
        ["user_id", "last_viewed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_project_views_user_last_viewed", table_name="project_views")
    op.drop_table("project_views")
    op.drop_index("ix_projects_category", table_name="projects")
    op.drop_column("projects", "category")
