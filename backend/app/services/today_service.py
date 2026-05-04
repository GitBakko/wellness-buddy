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

# Plan 02-04: ordered Italian day slugs (0=Mon..6=Sun) — mirrors plan_sections._INT_TO_DAY_SLUG.
_INT_TO_DAY_SLUG = ("lun", "mar", "mer", "gio", "ven", "sab", "dom")


def _options_for_day(slot_dict: dict, day_of_week: int) -> list:
    """Resolve a list of MealOption-shaped dicts for a given day_of_week.

    Plan 02-04 contract — `slot_dict` may be:
      * `{day_slug: [opts]}` (grid format, real Stefano + Marta plans), OR
      * `{'default': [opts]}` (subheading format, EXAMPLE.md backward compat).

    Lookup precedence: today's day_slug → 'default' → first dict value (defensive).
    Returns `[]` when no options found.
    """
    if not isinstance(slot_dict, dict) or not slot_dict:
        return []
    today_slug = _INT_TO_DAY_SLUG[day_of_week]
    options = slot_dict.get(today_slug) or slot_dict.get("default")
    if not options:
        # Defensive — return any first non-empty list so callers degrade gracefully.
        for v in slot_dict.values():
            if isinstance(v, list) and v:
                options = v
                break
    return list(options) if isinstance(options, list) else []


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


def _meals_from_parsed(
    parsed: dict,
    day_of_week: int = 0,
    variant_by_meal: dict[str, WeeklyPlanVariant] | None = None,
) -> list[MealEntry]:
    """Emit today's meal list from parsed_json. Variant selection defaults to first option.

    Plan 02-04: lunches/dinners are resolved per-day. `day_of_week` (0=Mon..6=Sun) drives
    the day_slug lookup; falls back to 'default' for subheading-format plans.
    `variant_by_meal` (when provided) lets the user's stored selection override the
    "first option" fallback so the recipe title shown matches the chosen variant.

    Display order (Plan 02-03 gap closure): breakfast → lunch → snack → dinner.
    Spuntino sits between lunch and dinner because Stefano/Marta consume it
    mid-afternoon (15:30-16:00), not after dinner.
    """
    variant_by_meal = variant_by_meal or {}
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
        options = _options_for_day(slot_dict if isinstance(slot_dict, dict) else {}, day_of_week)
        if not options:
            continue
        # Pick the user's selected variant if present; otherwise first option (default).
        selected_key = variant_by_meal[slot].variant_key if slot in variant_by_meal else None
        opt: dict | None = None
        if selected_key:
            for candidate in options:
                if isinstance(candidate, dict) and str(candidate.get("key")) == selected_key:
                    opt = candidate
                    break
        if opt is None:
            opt = options[0] if isinstance(options[0], dict) else None
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
        # Plan 02-04: variants drive both completion AND which lunch/dinner variant
        # to surface. Build a lookup by meal_type → WeeklyPlanVariant for today's row.
        variants = (
            await session.scalars(
                select(WeeklyPlanVariant).where(
                    WeeklyPlanVariant.user_id == user.id,
                    WeeklyPlanVariant.week_start == week_start,
                    WeeklyPlanVariant.day_of_week == day_of_week,
                )
            )
        ).all()
        variant_by_meal: dict[str, WeeklyPlanVariant] = {v.meal_type: v for v in variants}

        meals = _meals_from_parsed(
            plan.parsed_json or {},
            day_of_week=day_of_week,
            variant_by_meal=variant_by_meal,
        )

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
