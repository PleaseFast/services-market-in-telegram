"""multi-category specialist profiles

Replaces the single ``specialist_profiles.category`` string column with a
``specialist_profile_categories`` join table so each specialist can opt into
multiple categories. The old value is backfilled as a single row in the new
table before the column is dropped.

Revision ID: 0005_specialist_multi_category
Revises: 0004_pause_and_published_at
Create Date: 2026-05-30
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_specialist_multi_category"
down_revision = "0004_pause_and_published_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "specialist_profile_categories",
        sa.Column(
            "specialist_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(80), nullable=False),
        sa.PrimaryKeyConstraint(
            "specialist_profile_id", "category", name="pk_specialist_profile_categories"
        ),
    )
    op.create_index(
        "ix_specialist_profile_categories_category",
        "specialist_profile_categories",
        ["category"],
    )

    # Backfill: turn the legacy single-category column into one association row
    # per profile. Skip rows with a NULL/empty category just in case.
    op.execute(
        """
        INSERT INTO specialist_profile_categories (specialist_profile_id, category)
        SELECT id, category
          FROM specialist_profiles
         WHERE category IS NOT NULL AND category <> ''
        """
    )

    op.drop_index("ix_specialist_profiles_category", table_name="specialist_profiles")
    op.drop_column("specialist_profiles", "category")


def downgrade() -> None:
    op.add_column(
        "specialist_profiles",
        sa.Column("category", sa.String(80), nullable=True),
    )
    # Restore at most one category per profile (alphabetically lowest, for
    # determinism). Information loss is unavoidable once multi-select shipped.
    op.execute(
        """
        UPDATE specialist_profiles AS sp
           SET category = sub.category
          FROM (
                SELECT specialist_profile_id, MIN(category) AS category
                  FROM specialist_profile_categories
                 GROUP BY specialist_profile_id
               ) AS sub
         WHERE sp.id = sub.specialist_profile_id
        """
    )
    op.alter_column("specialist_profiles", "category", nullable=False)
    op.create_index(
        "ix_specialist_profiles_category", "specialist_profiles", ["category"]
    )
    op.drop_index(
        "ix_specialist_profile_categories_category",
        table_name="specialist_profile_categories",
    )
    op.drop_table("specialist_profile_categories")
