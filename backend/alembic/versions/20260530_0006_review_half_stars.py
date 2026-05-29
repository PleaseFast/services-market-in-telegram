"""review ratings stored as half-stars (0..10)

Switches ``reviews.rating`` from an integer 1..5 to ``rating_half`` 0..10
(half-star resolution). The API exposes the value as a float 0.0..5.0 in
steps of 0.5; storing the doubled integer avoids float-equality concerns
in the CHECK constraint and stays portable across SQLite + Postgres.

Any existing row's integer rating is preserved by doubling (e.g. 5 → 10).

Revision ID: 0006_review_half_stars
Revises: 0005_specialist_multi_category
Create Date: 2026-05-30
"""
from __future__ import annotations

from alembic import op

revision = "0006_review_half_stars"
down_revision = "0005_specialist_multi_category"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_review_rating_range", "reviews", type_="check")
    op.alter_column("reviews", "rating", new_column_name="rating_half")
    op.execute("UPDATE reviews SET rating_half = rating_half * 2")
    op.create_check_constraint(
        "ck_review_rating_half_range",
        "reviews",
        "rating_half BETWEEN 0 AND 10",
    )


def downgrade() -> None:
    op.drop_constraint("ck_review_rating_half_range", "reviews", type_="check")
    # Half-stars below 2 would collapse to 0; floor-divide preserves the
    # closest legal integer rating.
    op.execute("UPDATE reviews SET rating_half = rating_half / 2")
    op.alter_column("reviews", "rating_half", new_column_name="rating")
    op.create_check_constraint(
        "ck_review_rating_range",
        "reviews",
        "rating BETWEEN 1 AND 5",
    )
