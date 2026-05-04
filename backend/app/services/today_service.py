"""Today aggregator service — Plan 07.

Computes `/today` payload: date + day_of_week + greeting_period + meals (from active
plan's parsed_json) + completion state + today's weight + today's workout.

Source: TODAY-01..TODAY-08, T-API-02 (cross-user authz scope = own user_id only),
        UI-SPEC §7.2 (greeting period server-computed from user IANA tz),
        CONV-09 (TIMESTAMPTZ + Europe/Rome default), Plan 04 PlanParsedSchema.
"""

from __future__ import annotations

from datetime import date as date_t
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant
from app.models.weight import WeightLog
from app.models.workout import WorkoutLog
from app.schemas.today import (
    MealEntry,
    MealMacro,
    TodayResponse,
    TodayWeight,
    TodayWorkout,
)

MEAL_TYPES = ("breakfast", "lunch", "dinner", "snack")


def _greeting_period(now: datetime) -> str:
    """UI-SPEC §7.2 buckets, computed in user's IANA tz."""
    h = now.hour
    if 5 <= h < 12:
        return "morning"
    if 12 <= h < 18:
        return "afternoon"
    if 18 <= h < 23:
        return "evening"
    return "night"


def _coerce_macros(raw: object) -> MealMacro:
    """Build MealMacro defensively from parsed_json (which may carry stray keys)."""
    if not isinstance(raw, dict):
        return MealMacro()
    return MealMacro(
        kcal=int(raw.get("kcal", 0) or 0),
        protein_g=float(raw.get("protein_g", 0) or 0),
        carbs_g=float(raw.get("carbs_g", 0) or 0),
        fat_g=float(raw.get("fat_g", 0) or 0),
    )


def _coerce_photo_url(raw: object) -> str | None:
    """Pass-through for parsed_json photo_url (Plan 01-09).

    Returns the value when it's a non-empty string ≤500 chars, else None.
    The strict cap mirrors `MealOption.photo_url` Pydantic validator and
    keeps Spoofing-class threats contained at the service boundary.
    """
    if not isinstance(raw, str):
        return None
    val = raw.strip()
    if not val or len(val) > 500:
        return None
    return val


def _meals_from_parsed(parsed: dict) -> list[MealEntry]:
    """Emit Phase 1 meal list from parsed_json. Variant selection (Phase 2) defaults
    to first option per slot. Plan 01-09: passes optional photo_url through.

    Display order (Plan 02-03 gap closure): breakfast → lunch → snack → dinner.
    Spuntino sits between lunch and dinner because Stefano/Marta consume it
    mid-afternoon (15:30-16:00), not after dinner.
    """
    breakfast_meal: MealEntry | None = None
    lunch_meal: MealEntry | None = None
    dinner_meal: MealEntry | None = None
    snack_meals: list[MealEntry] = []

    breakfast = parsed.get("breakfast")
    if isinstance(breakfast, dict) and breakfast:
        breakfast_meal = MealEntry(
            meal_type="breakfast",
            variant_key=str(breakfast.get("key") or "default"),
            title=str(breakfast.get("title") or "Colazione"),
            macros=_coerce_macros(breakfast.get("macros")),
            photo_url=_coerce_photo_url(breakfast.get("photo_url")),
        )

    for slot, parsed_key in (("lunch", "lunches"), ("dinner", "dinners")):
        slot_dict = parsed.get(parsed_key)
        if not isinstance(slot_dict, dict) or not slot_dict:
            continue
        options = slot_dict.get("default")
        if not options:
            options = next(iter(slot_dict.values()), [])
        if not options:
            continue
        opt = options[0] if isinstance(options, list) else None
        if not isinstance(opt, dict):
            continue
        entry = MealEntry(
            meal_type=slot,
            variant_key=str(opt.get("key") or "default"),
            title=str(opt.get("title") or slot.capitalize()),
            macros=_coerce_macros(opt.get("macros")),
            photo_url=_coerce_photo_url(opt.get("photo_url")),
        )
        if slot == "lunch":
            lunch_meal = entry
        else:
            dinner_meal = entry

    snacks = parsed.get("snacks") or []
    if isinstance(snacks, list):
        for sn in snacks:
            if not isinstance(sn, dict):
                continue
            snack_meals.append(
                MealEntry(
                    meal_type="snack",
                    variant_key=str(sn.get("key") or "default"),
                    title=str(sn.get("title") or "Spuntino"),
                    macros=_coerce_macros(sn.get("macros")),
                    photo_url=_coerce_photo_url(sn.get("photo_url")),
                )
            )

    ordered: list[MealEntry] = []
    if breakfast_meal:
        ordered.append(breakfast_meal)
    if lunch_meal:
        ordered.append(lunch_meal)
    ordered.extend(snack_meals)  # snack sits between lunch and dinner
    if dinner_meal:
        ordered.append(dinner_meal)
    return ordered


async def _user_today(user: User) -> tuple[date_t, int, datetime]:
    """Return (today_date, day_of_week_mon0, now_in_tz) using user's IANA tz."""
    tz = ZoneInfo(user.timezone or "Europe/Rome")
    now = datetime.now(tz)
    return now.date(), now.weekday(), now


async def build_today_payload(session: AsyncSession, user: User) -> TodayResponse:
    """Aggregate today's view scoped to `user.id` only (T-API-02)."""
    today, day_of_week, now = await _user_today(user)
    week_start = today - timedelta(days=day_of_week)

    # Active plan (user-scoped)
    plan = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.user_id == user.id,
                NutritionPlan.is_active.is_(True),
            )
        )
    ).first()

    meals: list[MealEntry] = []
    if plan:
        meals = _meals_from_parsed(plan.parsed_json or {})

        # Apply completion state from this week's variants
        variants = (
            await session.scalars(
                select(WeeklyPlanVariant).where(
                    WeeklyPlanVariant.user_id == user.id,
                    WeeklyPlanVariant.week_start == week_start,
                    WeeklyPlanVariant.day_of_week == day_of_week,
                )
            )
        ).all()
        # When multiple snacks share meal_type='snack', mark them all complete if a
        # variant row says so — Phase 1 behavior; Phase 2 may distinguish per snack key.
        completed_meal_types = {v.meal_type for v in variants if v.completed}
        for m in meals:
            if m.meal_type in completed_meal_types:
                m.completed = True

    # Today's weight (user-scoped)
    weight_row = (
        await session.scalars(
            select(WeightLog).where(WeightLog.user_id == user.id, WeightLog.date == today)
        )
    ).first()
    weight_today = (
        TodayWeight(id=str(weight_row.id), weight_kg=weight_row.weight_kg) if weight_row else None
    )

    # Today's workout (user-scoped)
    workout_row = (
        await session.scalars(
            select(WorkoutLog).where(WorkoutLog.user_id == user.id, WorkoutLog.date == today)
        )
    ).first()
    workout_today = (
        TodayWorkout(
            id=str(workout_row.id),
            trained=workout_row.trained,
            duration_min=workout_row.duration_min,
            calories_burned=workout_row.calories_burned,
            workout_type=workout_row.workout_type,
            notes=workout_row.notes,
        )
        if workout_row
        else None
    )

    return TodayResponse(
        date=today,
        day_of_week=day_of_week,
        greeting_period=_greeting_period(now),
        meals=meals,
        weight_today=weight_today,
        workout_today=workout_today,
    )


async def complete_meal(session: AsyncSession, *, user: User, meal_type: str) -> WeeklyPlanVariant:
    """Mark `meal_type` completed for today's variant row (creates if absent).

    Visibility default: `group_shared` for lunch/dinner, `private` otherwise (CONV-14).
    """
    if meal_type not in MEAL_TYPES:
        raise AppException(400, "Tipo pasto non valido.", "invalid_meal_type")

    today, day_of_week, _now = await _user_today(user)
    week_start = today - timedelta(days=day_of_week)

    plan = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.user_id == user.id,
                NutritionPlan.is_active.is_(True),
            )
        )
    ).first()
    if not plan:
        raise AppException(400, "Nessun piano attivo.", "no_active_plan")

    variant = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == user.id,
                WeeklyPlanVariant.week_start == week_start,
                WeeklyPlanVariant.day_of_week == day_of_week,
                WeeklyPlanVariant.meal_type == meal_type,
            )
        )
    ).first()

    if not variant:
        variant = WeeklyPlanVariant(
            user_id=user.id,
            plan_id=plan.id,
            week_start=week_start,
            day_of_week=day_of_week,
            meal_type=meal_type,
            variant_key="default",
            visibility=(
                Visibility.GROUP_SHARED if meal_type in ("lunch", "dinner") else Visibility.PRIVATE
            ),
            completed=True,
        )
        session.add(variant)
    else:
        variant.completed = True
        variant.version = variant.version + 1

    await session.commit()
    await session.refresh(variant)
    return variant
