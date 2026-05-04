"""WeeklyPlanVariant model + Visibility enum (MOD-04, MOD-10).

Tracks per-(user, week, day, meal) the variant chosen + visibility (private vs group_shared).
`version` enables LWW conflict resolution + 409 surfacing per CONVENTION 13.
"""

from __future__ import annotations

from datetime import date
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class Visibility(str, PyEnum):
    """Resource visibility on shareable models. Cene/pranzi default `group_shared` Phase 2."""

    PRIVATE = "private"
    GROUP_SHARED = "group_shared"


class WeeklyPlanVariant(Base):
    __tablename__ = "weekly_plan_variants"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("nutrition_plans.id", ondelete="CASCADE"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon..6=Sun
    # breakfast | lunch | dinner | snack
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 'A' | 'B' | 'pasta'
    variant_key: Mapped[str] = mapped_column(String(20), nullable=False)
    visibility: Mapped[Visibility] = mapped_column(
        SAEnum(Visibility, name="visibility_enum"),
        default=Visibility.PRIVATE,
        nullable=False,
    )
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    # LWW conflict tracking (CONV-13)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_at: Mapped[TimestampTZ]
    created_at: Mapped[TimestampTZ]

    __table_args__ = (
        # MOD-10: time-series index on (user_id, week_start)
        Index("ix_weekly_user_week", "user_id", "week_start"),
        # Phase 2 family sync helper: list shared variants for a given week
        Index("ix_weekly_group_share", "week_start", "visibility"),
        # Plan 02-04: per-day variant uniqueness — one row per (user, week, day, meal)
        UniqueConstraint(
            "user_id",
            "week_start",
            "day_of_week",
            "meal_type",
            name="uq_weekly_variant_per_day",
        ),
    )
