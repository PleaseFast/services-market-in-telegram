"""profile redesign: avatar_id, timeline items, service catalog, specialist services

Revision ID: 0003_profile_redesign
Revises: 0002_project_category_and_views
Create Date: 2026-05-29
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_profile_redesign"
down_revision = "0002_project_category_and_views"
branch_labels = None
depends_on = None


TIMELINE_KIND_VALUES = ("work", "education", "achievement")
DEFAULT_AVATAR_ID = "fox:amber"


def upgrade() -> None:
    bind = op.get_bind()

    # --- avatar_id columns on profiles ---------------------------------------
    op.add_column(
        "specialist_profiles",
        sa.Column(
            "avatar_id",
            sa.String(40),
            nullable=False,
            server_default=DEFAULT_AVATAR_ID,
        ),
    )
    op.add_column(
        "customer_profiles",
        sa.Column(
            "avatar_id",
            sa.String(40),
            nullable=False,
            server_default=DEFAULT_AVATAR_ID,
        ),
    )

    # --- profile_timeline_items ---------------------------------------------
    timeline_kind = postgresql.ENUM(*TIMELINE_KIND_VALUES, name="timeline_kind", create_type=False)
    timeline_kind.create(bind, checkfirst=True)

    op.create_table(
        "profile_timeline_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("kind", timeline_kind, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("start_year", sa.SmallInteger(), nullable=False),
        sa.Column("end_year", sa.SmallInteger(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_profile_timeline_items_profile_kind_position",
        "profile_timeline_items",
        ["profile_id", "kind", "position"],
    )

    # --- backfill timeline from workplaces (kind=work) and portfolio_links (kind=achievement) ---
    current_year = datetime.now(timezone.utc).year

    op.execute(
        sa.text(
            """
            INSERT INTO profile_timeline_items
              (profile_id, kind, title, description, start_year, end_year, is_current, position)
            SELECT
              sw.profile_id,
              'work',
              CASE
                WHEN COALESCE(sw.company, '') = '' THEN sw.title
                ELSE sw.title || ' · ' || sw.company
              END,
              COALESCE(sw.period, ''),
              GREATEST(:floor_year, :now_year - GREATEST(COALESCE(sp.years_experience, 1), 1)),
              :now_year,
              TRUE,
              ROW_NUMBER() OVER (PARTITION BY sw.profile_id ORDER BY sw.created_at) - 1
            FROM specialist_workplaces sw
            JOIN specialist_profiles sp ON sp.id = sw.profile_id
            """
        ).bindparams(now_year=current_year, floor_year=1950)
    )
    op.execute(
        sa.text(
            """
            INSERT INTO profile_timeline_items
              (profile_id, kind, title, description, start_year, end_year, is_current, position)
            SELECT
              spl.profile_id,
              'achievement',
              COALESCE(NULLIF(spl.label, ''), 'Portfolio link'),
              spl.url,
              :now_year,
              :now_year,
              FALSE,
              ROW_NUMBER() OVER (PARTITION BY spl.profile_id ORDER BY spl.created_at) - 1
            FROM specialist_portfolio_links spl
            """
        ).bindparams(now_year=current_year)
    )

    # --- drop old child tables -----------------------------------------------
    op.drop_table("specialist_portfolio_links")
    op.drop_table("specialist_workplaces")

    # --- drop old avatar_url columns ----------------------------------------
    op.drop_column("specialist_profiles", "avatar_url")
    op.drop_column("customer_profiles", "avatar_url")

    # --- service_catalog -----------------------------------------------------
    op.create_table(
        "service_catalog",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("subcategory", sa.String(80), nullable=False),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_service_catalog_slug"),
    )
    op.create_index(
        "ix_service_catalog_category_subcategory_position",
        "service_catalog",
        ["category", "subcategory", "position"],
    )
    op.create_index("ix_service_catalog_slug", "service_catalog", ["slug"])

    # --- specialist_services -------------------------------------------------
    op.create_table(
        "specialist_services",
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "service_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_catalog.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("price_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("specialist_services")
    op.drop_index("ix_service_catalog_slug", table_name="service_catalog")
    op.drop_index(
        "ix_service_catalog_category_subcategory_position", table_name="service_catalog"
    )
    op.drop_table("service_catalog")

    # Re-add avatar_url and the dropped child tables (best-effort; backfill is
    # not reversed — pre-launch state acceptable).
    op.add_column(
        "customer_profiles",
        sa.Column("avatar_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "specialist_profiles",
        sa.Column("avatar_url", sa.String(500), nullable=True),
    )

    op.create_table(
        "specialist_workplaces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("company", sa.String(120), nullable=False),
        sa.Column("period", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "specialist_portfolio_links",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("specialist_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("label", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.drop_column("specialist_profiles", "avatar_id")
    op.drop_column("customer_profiles", "avatar_id")

    op.drop_index(
        "ix_profile_timeline_items_profile_kind_position",
        table_name="profile_timeline_items",
    )
    op.drop_table("profile_timeline_items")
    sa.Enum(name="timeline_kind").drop(op.get_bind(), checkfirst=True)
