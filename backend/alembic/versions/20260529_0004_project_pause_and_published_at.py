"""project pause status + published_at column

Adds:
- ``paused`` value to the ``project_status`` enum so customers can pause and
  resume the specialist search on an OPEN project without losing it.
- ``projects.published_at`` (nullable timestamptz) so specialists can see when
  a project was first published. Backfilled from ``created_at`` for any rows
  already in OPEN/IN_PROGRESS/COMPLETED/ARCHIVED — those are the states that
  can only be reached by going through OPEN, so their creation time is the
  best available proxy for publication time.

Revision ID: 0004_project_pause_and_published_at
Revises: 0003_profile_redesign
Create Date: 2026-05-29
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_pause_and_published_at"
down_revision = "0003_profile_redesign"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend the enum. ``ADD VALUE`` cannot run inside a transaction block on
    # older PG, but Alembic's default transaction-per-migration is fine on
    # PG 12+, and we're on PG 16-alpine per docker-compose.
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'paused'")

    # New publication timestamp. Nullable because drafts haven't been
    # published yet and historical rows have no recorded publication moment.
    op.add_column(
        "projects",
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Backfill: for every row that has been published at least once, use
    # created_at as a stand-in. Draft and canceled-from-draft rows stay NULL.
    op.execute(
        """
        UPDATE projects
           SET published_at = created_at
         WHERE status IN ('open', 'in_progress', 'completed', 'archived')
           AND published_at IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("projects", "published_at")
    # Postgres does not support removing a value from an enum; downgrade
    # leaves "paused" in the type. Any rows in PAUSED would need manual
    # remediation before this could be undone.
