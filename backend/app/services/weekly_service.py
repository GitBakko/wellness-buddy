"""Weekly aggregator service (WEEK-01..WEEK-05, D-02..D-04).

Builds the /api/weekly/{week_start} payload by joining the active NutritionPlan's
`parsed_json` with WeeklyPlanVariant rows for that user+week. Missing variants
fall back to the first option of each slot (D-03 — "default = Opzione A").

The payload shape is intentionally similar to today_service.build_today_payload
but expanded to 7 days × 4 meal slots = 28 meal entries.
"""

from __future__ import annotations

from datetime import date as date_t
from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import WeeklyPlanVariant

MEAL_SLOTS = ("breakfast", "lunch", "dinner", "snack")


async def build_weekly_payload(
    session: AsyncSession, *, user: User, week_start: date_t
) -> dict[str, Any]:
    """Build /api/weekly/{week_start} payload (WEEK-01, WEEK-02, WEEK-03)."""
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

    variants = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == user.id,
                WeeklyPlanVariant.week_start == week_start,
            )
        )
    ).all()
    # Index by (day_of_week, meal_type) → variant
    variant_map: dict[tuple[int, str], WeeklyPlanVariant] = {
        (v.day_of_week, v.meal_type): v for v in variants
    }

    days: list[dict[str, Any]] = []
    for d in range(7):
        day_date = week_start + timedelta(days=d)
        meals: list[dict[str, Any]] = []
        for slot in MEAL_SLOTS:
            v = variant_map.get((d, slot))
            meal_block = _resolve_meal(plan.parsed_json, slot, v.variant_key if v else "default")
            meals.append(
                {
                    "slot": slot,
                    "title": str(meal_block.get("title") or ""),
                    "variant_key": v.variant_key if v else "default",
                    "visibility": v.visibility.value if v else "private",
                    "version": v.version if v else 0,
                    "updated_at": (v.updated_at.isoformat() if v else None),
                    "completed": v.completed if v else False,
                    "owner_user_id": str(user.id),
                    "macros": dict(meal_block.get("macros") or {}),
                    "ingredients": list(meal_block.get("ingredients") or []),
                }
            )
        days.append({"date": day_date.isoformat(), "day_of_week": d, "meals": meals})

    totals = _aggregate_totals(days)
    return {
        "week_start": week_start.isoformat(),
        "days": days,
        "totals": totals,
    }


async def build_weekly_summary(
    session: AsyncSession, *, user: User, week_start: date_t
) -> dict[str, Any]:
    """WEEK-05: GET /api/weekly/{week_start}/summary — kcal/macro per day + week total."""
    payload = await build_weekly_payload(session, user=user, week_start=week_start)
    return {
        "week_start": payload["week_start"],
        "kcal_total": payload["totals"]["kcal"],
        "protein_g": payload["totals"]["protein_g"],
        "carbs_g": payload["totals"]["carbs_g"],
        "fat_g": payload["totals"]["fat_g"],
        "days": [
            {
                "date": d["date"],
                "kcal": sum(_macro(m, "kcal") for m in d["meals"]),
                "protein_g": sum(_macro(m, "protein_g") for m in d["meals"]),
                "carbs_g": sum(_macro(m, "carbs_g") for m in d["meals"]),
                "fat_g": sum(_macro(m, "fat_g") for m in d["meals"]),
            }
            for d in payload["days"]
        ],
    }


def _macro(meal: dict[str, Any], key: str) -> float:
    """Defensive macro extractor — `macros` may be missing or not a dict."""
    macros = meal.get("macros") or {}
    if not isinstance(macros, dict):
        return 0
    val = macros.get(key, 0)
    try:
        return float(val) if val is not None else 0
    except (TypeError, ValueError):
        return 0


_SLOT_KEYS = {
    "breakfast": "breakfasts",
    "lunch": "lunches",
    "dinner": "dinners",
    "snack": "snacks",
}


def _resolve_meal(parsed: dict[str, Any] | None, slot: str, variant_key: str) -> dict[str, Any]:
    """Look up the meal block in parsed_json by slot + variant.

    parsed_json layout (from MD parser, Plan 04):
      breakfast: { title, macros, ... }       (single dict)
      lunches:   { default: [ {key, title, macros, ...}, ... ] }
      dinners:   same as lunches
      snacks:    [ { key, title, macros, ... }, ... ]   (flat list)

    Phase 1 today_service walks the same shapes; here we honor variant_key but
    fall back to the first available option (D-03 default behavior) when not found.
    """
    if not isinstance(parsed, dict) or not parsed:
        return {}

    # Breakfast: single dict, ignore variant_key (today_service convention)
    if slot == "breakfast":
        b = parsed.get("breakfast")
        return b if isinstance(b, dict) else {}

    if slot in ("lunch", "dinner"):
        plural = _SLOT_KEYS[slot]
        section = parsed.get(plural) or {}
        if not isinstance(section, dict):
            return {}
        # The parser indexes lunches/dinners by a top-level "default" → list
        # of variants. variant_key 'A'/'B'/'pasta'/'special'/'default' picks
        # the matching item by `.key`; falls back to first option.
        options = section.get("default") or next(iter(section.values()), [])
        if not isinstance(options, list):
            return {}
        for opt in options:
            if isinstance(opt, dict) and str(opt.get("key")) == variant_key:
                return opt
        # Fallback: first option of slot
        return options[0] if options and isinstance(options[0], dict) else {}

    if slot == "snack":
        snacks = parsed.get("snacks")
        if not isinstance(snacks, list) or not snacks:
            return {}
        for opt in snacks:
            if isinstance(opt, dict) and str(opt.get("key")) == variant_key:
                return opt
        # Fallback: first snack
        return snacks[0] if isinstance(snacks[0], dict) else {}

    return {}


def _aggregate_totals(days: list[dict[str, Any]]) -> dict[str, float]:
    kcal = sum(_macro(m, "kcal") for d in days for m in d["meals"])
    protein = sum(_macro(m, "protein_g") for d in days for m in d["meals"])
    carbs = sum(_macro(m, "carbs_g") for d in days for m in d["meals"])
    fat = sum(_macro(m, "fat_g") for d in days for m in d["meals"])
    return {"kcal": kcal, "protein_g": protein, "carbs_g": carbs, "fat_g": fat}
