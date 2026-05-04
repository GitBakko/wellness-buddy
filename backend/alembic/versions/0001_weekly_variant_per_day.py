"""Plan 02-04 — per-day weekly variants composite unique constraint.

Add `UNIQUE(user_id, week_start, day_of_week, meal_type)` to `weekly_plan_variants`
so the (user_id, week_start, day_of_week, meal_type) tuple identifies one variant
selection. The `day_of_week` column already exists in the baseline; this migration
only enforces the composite uniqueness so concurrent upserts collide deterministically
(LWW + version int + 409 toast — CONV-13).

Backward compat: no data migration needed — existing rows already carry day_of_week
because the model exposed it from baseline.

Revision ID: 8137b2e24001
Revises: a694bcd4d792
Create Date: 2026-05-04
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8137b2e24001"
down_revision: str | Sequence[str] | None = "a694bcd4d792"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the (user_id, week_start, day_of_week, meal_type) composite UNIQUE."""
    op.create_unique_constraint(
        "uq_weekly_variant_per_day",
        "weekly_plan_variants",
        ["user_id", "week_start", "day_of_week", "meal_type"],
    )


def downgrade() -> None:
    """Drop the composite unique constraint."""
    op.drop_constraint(
        "uq_weekly_variant_per_day",
        "weekly_plan_variants",
        type_="unique",
    )
