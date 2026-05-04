"""Shopping aggregation service (SHOP-01..SHOP-06, SHOP-08, D-05..D-09).

The pipeline:

  1. ``aggregate_for_week`` reads the active plan + selected variants for the
     given week and walks (day, slot) tuples — 7 days × 4 slots = 28 entries.
  2. Each meal block contributes a list of ingredient strings; each line is
     parsed into ``ParsedIngredient`` rows by
     :mod:`app.services.ingredient_parser`.
  3. Rows are bucketed by ``(canonical_name, unit)`` so distinct units stay
     split (``pasta 80g`` vs ``1 confezione di pasta``) while same-unit rows
     merge cleanly. ``q.b.`` (``unit="qb"``) collapses regardless of recipe
     count (Pitfall #14 — count = 1 always).
  4. Each row's category comes from the meal-level ``**Categoria:**``
     annotation if present (validated against the 5 locked categories);
     otherwise from :func:`category_mapper.lookup`. Unknown / invalid
     categories fall back to ``"Dispensa"``.
  5. Persisted check state from ``ShoppingListState.items_json`` is merged in
     so the UI restores user's tick marks after re-aggregation.

LWW conflict resolution (CONV-13): :func:`toggle_check` increments
``ShoppingListState.version`` on every PATCH; the frontend echoes the version
back and the API surfaces 409 if a stale version is sent (Plan 02-07 — cross-
user reads add the matrix).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from datetime import date as date_t
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.plan import NutritionPlan
from app.models.shopping import ShoppingListState
from app.models.user import User
from app.models.variant import WeeklyPlanVariant
from app.services import category_mapper, ingredient_parser
from app.services.weekly_service import MEAL_SLOTS

# Italian months for human-readable shopping list date headers.
ITALIAN_MONTHS = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)


def _format_quantity_it(amount: float | None, unit: str | None) -> str:
    """Italian quantity rendering: ``"400 g"`` / ``"2 confezioni"`` / ``"q.b."`` / ``"1,5 kg"``.

    Returns the empty string when both ``amount`` and ``unit`` are absent so
    the UI can omit the secondary line entirely.
    """
    if unit == "qb":
        return "q.b."
    if amount is None:
        return ""
    # italian decimal: 1.5 → "1,5" (only when fractional part present)
    if amount == int(amount):
        amount_str = str(int(amount))
    else:
        amount_str = f"{amount:g}".replace(".", ",")
    if unit:
        return f"{amount_str} {unit}"
    return amount_str


def _aggregate_ingredients(meals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pure aggregation core — input list of meal dicts → flat list of bucket dicts.

    Each meal dict carries:
      * ``ingredients`` — list of strings OR ingredient-shaped dicts.
      * ``category`` — optional explicit ``**Categoria:**`` annotation.
      * ``source_label`` — opaque tag (e.g. ``"lunch_d0"``) recorded for the
        per-day view.

    Returns a list of buckets keyed by ``(canonical_name, unit)``. Each bucket
    is the dict shape consumed by :class:`ShoppingItem`.

    Exposed for unit testing — :func:`aggregate_for_week` is the DB-bound
    entry-point used by the API.
    """
    buckets: dict[tuple[str, str | None], dict[str, Any]] = defaultdict(
        lambda: {
            "amount_total": 0.0,
            "amount_seen": False,
            "sources": [],
            "category": None,
            "category_explicit": False,
            "name_display": None,
        }
    )

    for meal in meals:
        meal_category_hint = meal.get("category")
        source_label = meal.get("source_label", "")
        for ing in meal.get("ingredients") or []:
            if isinstance(ing, str):
                line = ing
            elif isinstance(ing, dict):
                line = ing.get("name")
            else:
                line = None
            if not line:
                continue
            parsed_list = ingredient_parser.parse(str(line))
            for p in parsed_list:
                if not p.name:
                    continue
                key = (p.name, p.unit)
                bucket = buckets[key]
                # Track display name (preserve first occurrence's casing — but
                # input is already normalised lower; title-case for UI).
                if not bucket["name_display"]:
                    bucket["name_display"] = p.name.title()
                bucket["sources"].append(source_label)
                if p.unit == "qb":
                    # q.b. count = 1 regardless of recipe count (Pitfall #14)
                    pass
                elif p.amount is not None:
                    bucket["amount_total"] += p.amount
                    bucket["amount_seen"] = True
                # Category resolution (T-02-05-01): explicit annotation wins
                # only when it's one of the 5 locked categories; else keyword
                # lookup; else Dispensa fallback.
                if not bucket["category_explicit"]:
                    if meal_category_hint and meal_category_hint in category_mapper.CATEGORY_ORDER:
                        bucket["category"] = meal_category_hint
                        bucket["category_explicit"] = True
                    elif not bucket["category"]:
                        bucket["category"] = category_mapper.lookup(p.name)

    out: list[dict[str, Any]] = []
    for (canonical_name, unit), bucket in buckets.items():
        amount = bucket["amount_total"] if bucket["amount_seen"] else None
        cat = bucket["category"] or "Dispensa"
        if cat not in category_mapper.CATEGORY_ORDER:
            cat = "Dispensa"
        out.append(
            {
                "canonical_name": canonical_name,
                "name_display": bucket["name_display"] or canonical_name.title(),
                "amount": amount,
                "unit": unit,
                "quantity_it": _format_quantity_it(amount, unit),
                "category": cat,
                "checked": False,
                "sources": list(bucket["sources"]),
            }
        )
    return out


_DAY_SLUGS = ("lun", "mar", "mer", "gio", "ven", "sab", "dom")


def _resolve_meal(
    parsed: dict[str, Any] | None,
    slot: str,
    variant_key: str,
    *,
    day_of_week: int = 0,
) -> dict[str, Any]:
    """Look up meal block for (slot, variant_key, day_of_week) — mirrors weekly_service."""
    if not isinstance(parsed, dict) or not parsed:
        return {}
    if slot == "breakfast":
        b = parsed.get("breakfast")
        return b if isinstance(b, dict) else {}
    if slot in ("lunch", "dinner"):
        plural = "lunches" if slot == "lunch" else "dinners"
        section = parsed.get(plural) or {}
        if not isinstance(section, dict):
            return {}
        day_slug = _DAY_SLUGS[day_of_week] if 0 <= day_of_week <= 6 else None
        options = (
            (section.get(day_slug) if day_slug else None)
            or section.get("default")
            or next((v for v in section.values() if isinstance(v, list) and v), [])
        )
        if not isinstance(options, list):
            return {}
        for opt in options:
            if isinstance(opt, dict) and str(opt.get("key")) == variant_key:
                return opt
        return options[0] if options and isinstance(options[0], dict) else {}
    if slot == "snack":
        snacks = parsed.get("snacks")
        if not isinstance(snacks, list) or not snacks:
            return {}
        for opt in snacks:
            if isinstance(opt, dict) and str(opt.get("key")) == variant_key:
                return opt
        return snacks[0] if isinstance(snacks[0], dict) else {}
    return {}


async def aggregate_for_week(
    session: AsyncSession,
    *,
    user: User,
    week_start: date_t,
) -> dict[str, Any]:
    """Build the categorized + aggregated shopping list payload (SHOP-01, SHOP-02, SHOP-04)."""
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
    variant_map = {(v.day_of_week, v.meal_type): v.variant_key for v in variants}

    # Build meal-list input for the pure aggregator.
    meals: list[dict[str, Any]] = []
    for d in range(7):
        for slot in MEAL_SLOTS:
            variant_key = variant_map.get((d, slot), "default")
            meal_block = _resolve_meal(plan.parsed_json, slot, variant_key, day_of_week=d)
            meals.append(
                {
                    "ingredients": meal_block.get("ingredients") or [],
                    "category": meal_block.get("category"),
                    "source_label": f"{slot}_d{d}",
                }
            )

    aggregated = _aggregate_ingredients(meals)

    # Group into 5 fixed-order categories
    category_buckets: dict[str, list[dict[str, Any]]] = {
        c: [] for c in category_mapper.CATEGORY_ORDER
    }
    for item in aggregated:
        cat = item["category"]
        if cat not in category_buckets:
            cat = "Dispensa"
        category_buckets[cat].append(item)

    # Apply persisted check state if any.
    state = (
        await session.scalars(
            select(ShoppingListState).where(
                ShoppingListState.user_id == user.id,
                ShoppingListState.week_start == week_start,
            )
        )
    ).first()
    checked_set: set[tuple[str, str | None]] = set()
    if state and state.items_json:
        for c in state.items_json.get("checked", []):
            checked_set.add((c.get("canonical_name", ""), c.get("unit")))

    for cat_items in category_buckets.values():
        for item in cat_items:
            if (item["canonical_name"], item["unit"]) in checked_set:
                item["checked"] = True

    version = state.version if state else 0
    return {
        "week_start": week_start.isoformat(),
        "categories": [
            {
                "name": c,
                "items": sorted(category_buckets[c], key=lambda x: x["canonical_name"]),
            }
            for c in category_mapper.CATEGORY_ORDER
        ],
        "version": version,
    }


async def toggle_check(
    session: AsyncSession,
    *,
    user: User,
    week_start: date_t,
    canonical_name: str,
    unit: str | None,
    checked: bool,
) -> dict[str, Any]:
    """Persist a single checkbox state (SHOP-03). Increments ``version`` on every call."""
    state = (
        await session.scalars(
            select(ShoppingListState).where(
                ShoppingListState.user_id == user.id,
                ShoppingListState.week_start == week_start,
            )
        )
    ).first()
    if state is None:
        state = ShoppingListState(
            user_id=user.id,
            week_start=week_start,
            items_json={"checked": []},
            version=0,
        )
        session.add(state)

    items = dict(state.items_json or {"checked": []})
    check_list = list(items.get("checked", []))
    # Drop any existing entry for the same (canonical_name, unit) tuple
    check_list = [
        c
        for c in check_list
        if not (c.get("canonical_name") == canonical_name and c.get("unit") == unit)
    ]
    if checked:
        check_list.append({"canonical_name": canonical_name, "unit": unit})
    items["checked"] = check_list
    state.items_json = items
    state.version = (state.version or 0) + 1
    await session.commit()
    await session.refresh(state)

    return await aggregate_for_week(session, user=user, week_start=week_start)


async def reset_shopping_list_for_user(
    session: AsyncSession,
    *,
    user_id: UUID,
    week_start: date_t | None = None,
) -> None:
    """SHOP-08 — clear checkbox state for the given week (or current week if None).

    Called by both the user-initiated POST /reset endpoint and the
    APScheduler weekly job at Mon 00:00 user-local.
    """
    if week_start is None:
        today = datetime.now(UTC).date()
        week_start = today - timedelta(days=today.weekday())
    state = (
        await session.scalars(
            select(ShoppingListState).where(
                ShoppingListState.user_id == user_id,
                ShoppingListState.week_start == week_start,
            )
        )
    ).first()
    if state:
        state.items_json = {"checked": []}
        state.version = (state.version or 0) + 1
        await session.commit()


async def build_pdf_payload(
    session: AsyncSession,
    *,
    user: User,
    week_start: date_t,
) -> dict[str, Any]:
    """Plan 02-06 hand-off — build the WeasyPrint Jinja2 template payload.

    Returns a dict with non-empty categories and an italian human-friendly
    week_start_long string. Plan 02-06 will replace the 501 stub on the
    /export-pdf endpoint with a call to this function + ``PdfExporter``.
    """
    agg = await aggregate_for_week(session, user=user, week_start=week_start)
    non_empty = [c for c in agg["categories"] if c["items"]]
    long_it = f"{week_start.day} {ITALIAN_MONTHS[week_start.month - 1]} {week_start.year}"
    return {
        "week_start": agg["week_start"],
        "week_start_long_it": long_it,
        "domain": "wellness-buddy.epartner.it",
        "categories": [
            {
                "name": c["name"],
                "items": [
                    {"name": it["name_display"], "quantity_it": it["quantity_it"]}
                    for it in c["items"]
                ],
            }
            for c in non_empty
        ],
    }
