"""Weekly API — GET /, GET /summary, PATCH /variant (WEEK-01..05, FAM-04).

Plan 02-07 — GET endpoints accept optional ``?user_id={partner}`` query for
cross-user reads via ``get_user_with_group_access`` (V13). Cross-user response
filters meals to ``visibility=group_shared`` only. PATCH /variant remains
own-user only — mutating a partner's variant always 404s by construction
because ``upsert_variant`` keys on ``current_user.id``.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_user_with_group_access
from app.core.exceptions import AppException
from app.models.user import User
from app.models.variant import Visibility
from app.schemas.weekly import (
    PatchVariantPayload,
    VariantResponse,
    WeeklyResponse,
    WeeklySummaryResponse,
)
from app.services import variant_service, weekly_service

router = APIRouter(prefix="/api/weekly", tags=["weekly"])


def _parse_week_start(raw: str) -> date:
    try:
        return date.fromisoformat(raw)
    except ValueError as e:
        raise AppException(422, "Data settimana non valida.", "validation_error") from e


def _parse_if_unmodified_since(raw: str | None) -> datetime | None:
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError as e:
        raise AppException(
            422,
            "Header If-Unmodified-Since non valido.",
            "validation_error",
        ) from e


@router.get("/{week_start}", response_model=WeeklyResponse)
async def get_weekly(
    week_start: str,
    user_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Plan 02-07 — accepts optional ``?user_id={partner}``.

    When the partner is in the same group, returns their week filtered to
    ``visibility=group_shared`` meals. Cross-group → 404 (V13).
    """
    ws = _parse_week_start(week_start)
    if user_id is not None and user_id != current_user.id:
        target = await get_user_with_group_access(user_id, current_user, session)
        payload = await weekly_service.build_weekly_payload(session, user=target, week_start=ws)
        for d in payload["days"]:
            d["meals"] = [m for m in d["meals"] if m.get("visibility") == "group_shared"]
        return payload
    return await weekly_service.build_weekly_payload(session, user=current_user, week_start=ws)


@router.get("/{week_start}/summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    week_start: str,
    user_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    if user_id is not None and user_id != current_user.id:
        target = await get_user_with_group_access(user_id, current_user, session)
        # Plan 02-07 — partner summary aggregates only group_shared meals.
        # Build the full weekly payload (already filtered above), then
        # recompute totals/day-level kcal so the summary stays internally
        # consistent (private meals removed from numerator).
        payload = await weekly_service.build_weekly_payload(session, user=target, week_start=ws)
        for d in payload["days"]:
            d["meals"] = [m for m in d["meals"] if m.get("visibility") == "group_shared"]
        return _summary_from_filtered(payload)
    return await weekly_service.build_weekly_summary(session, user=current_user, week_start=ws)


def _summary_from_filtered(payload: dict) -> dict:
    """Build a WeeklySummaryResponse-shaped dict from a filtered weekly payload.

    Mirrors :func:`weekly_service.build_weekly_summary` but starts from the
    already-filtered ``days`` so the partner's private meals are not counted
    toward the cross-user kcal totals.
    """

    def _macro(meal: dict, key: str) -> float:
        macros = meal.get("macros") or {}
        if not isinstance(macros, dict):
            return 0
        val = macros.get(key, 0)
        try:
            return float(val) if val is not None else 0
        except (TypeError, ValueError):
            return 0

    days = [
        {
            "date": d["date"],
            "kcal": sum(_macro(m, "kcal") for m in d["meals"]),
            "protein_g": sum(_macro(m, "protein_g") for m in d["meals"]),
            "carbs_g": sum(_macro(m, "carbs_g") for m in d["meals"]),
            "fat_g": sum(_macro(m, "fat_g") for m in d["meals"]),
        }
        for d in payload["days"]
    ]
    return {
        "week_start": payload["week_start"],
        "kcal_total": sum(d["kcal"] for d in days),
        "protein_g": sum(d["protein_g"] for d in days),
        "carbs_g": sum(d["carbs_g"] for d in days),
        "fat_g": sum(d["fat_g"] for d in days),
        "days": days,
    }


@router.patch("/{week_start}/variant", response_model=VariantResponse)
async def patch_variant(
    week_start: str,
    payload: PatchVariantPayload,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    parsed_ius = _parse_if_unmodified_since(if_unmodified_since)

    try:
        plan_uuid = UUID(payload.plan_id)
    except (ValueError, AttributeError) as e:
        raise AppException(422, "plan_id non valido.", "validation_error") from e

    visibility_enum: Visibility | None = None
    if payload.visibility:
        try:
            visibility_enum = Visibility(payload.visibility)
        except ValueError as e:
            raise AppException(422, "visibility non valida.", "validation_error") from e

    row = await variant_service.upsert_variant(
        session,
        user=user,
        plan_id=plan_uuid,
        week_start=ws,
        day_of_week=payload.day_of_week,
        meal_type=payload.meal_type,
        variant_key=payload.variant_key,
        visibility=visibility_enum,
        if_unmodified_since=parsed_ius,
    )
    return {
        "id": str(row.id),
        "user_id": str(row.user_id),
        "week_start": row.week_start.isoformat(),
        "day_of_week": row.day_of_week,
        "meal_type": row.meal_type,
        "variant_key": row.variant_key,
        "visibility": row.visibility.value,
        "version": row.version,
        "updated_at": row.updated_at.isoformat(),
        "completed": row.completed,
    }
