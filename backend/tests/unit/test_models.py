"""SQLAlchemy metadata assertions: all 10 tables, MOD-09 TIMESTAMPTZ, MOD-10 indexes, IANA tz default."""

from __future__ import annotations

from app.models import (
    AuditLog,
    Base,
    Group,
    InviteToken,
    NutritionPlan,
    RefreshToken,
    ShoppingListState,
    User,
    Visibility,
    WeeklyPlanVariant,
    WeightLog,
    WorkoutLog,
)

EXPECTED = {
    "groups",
    "users",
    "nutrition_plans",
    "weekly_plan_variants",
    "workout_log",
    "weight_log",
    "shopping_list_state",
    "invite_tokens",
    "refresh_tokens",
    "audit_log",
}


def test_all_tables_registered() -> None:
    assert EXPECTED <= set(Base.metadata.tables.keys())


def test_all_models_importable() -> None:
    # Sanity: every model class actually maps to its expected table name
    assert User.__tablename__ == "users"
    assert Group.__tablename__ == "groups"
    assert NutritionPlan.__tablename__ == "nutrition_plans"
    assert WeeklyPlanVariant.__tablename__ == "weekly_plan_variants"
    assert WorkoutLog.__tablename__ == "workout_log"
    assert WeightLog.__tablename__ == "weight_log"
    assert ShoppingListState.__tablename__ == "shopping_list_state"
    assert InviteToken.__tablename__ == "invite_tokens"
    assert RefreshToken.__tablename__ == "refresh_tokens"
    assert AuditLog.__tablename__ == "audit_log"


def test_user_timezone_iana_default() -> None:
    # MOD-01: User.timezone defaults to Europe/Rome (IANA)
    assert User.__table__.c.timezone.default.arg == "Europe/Rome"


def test_user_created_at_timestamptz() -> None:
    # MOD-09: TIMESTAMPTZ everywhere — User.created_at must be timezone-aware
    assert User.__table__.c.created_at.type.timezone is True


def test_workout_user_date_index() -> None:
    # MOD-10: time-series index for workout_log
    assert any(idx.name == "ix_workout_user_date" for idx in WorkoutLog.__table__.indexes)


def test_weight_user_date_index() -> None:
    # MOD-10: time-series index for weight_log
    assert any(idx.name == "ix_weight_user_date" for idx in WeightLog.__table__.indexes)


def test_weekly_user_week_index() -> None:
    # MOD-10: time-series index for weekly_plan_variant
    assert any(idx.name == "ix_weekly_user_week" for idx in WeeklyPlanVariant.__table__.indexes)


def test_visibility_enum_values() -> None:
    # MOD-04: visibility enum private | group_shared
    assert Visibility.PRIVATE.value == "private"
    assert Visibility.GROUP_SHARED.value == "group_shared"


def test_nutrition_plan_partial_unique_active() -> None:
    # V11: at most one active plan per user — partial unique index `WHERE is_active = true`
    idx = next(
        (i for i in NutritionPlan.__table__.indexes if i.name == "ix_nutrition_plans_active_per_user"),
        None,
    )
    assert idx is not None
    assert idx.unique is True


def test_weight_log_unique_user_date() -> None:
    # MOD-06: one weigh-in per user per day
    constraints = WeightLog.__table__.constraints
    assert any(getattr(c, "name", None) == "uq_weight_user_date" for c in constraints)
