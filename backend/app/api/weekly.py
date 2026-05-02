"""Weekly API — GET /, GET /summary, PATCH /variant (WEEK-01..05, FAM-04).

Replaces Plan 02b's 501 stub. All endpoints scope to `current_user` only —
cross-user paths arrive Plan 02-06 with `get_user_with_group_access` (V13).
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
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
        raise AppException(
            422, "Data settimana non valida.", "validation_error"
        ) from e


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
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    return await weekly_service.build_weekly_payload(
        session, user=user, week_start=ws
    )


@router.get("/{week_start}/summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    week_start: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    return await weekly_service.build_weekly_summary(
        session, user=user, week_start=ws
    )


@router.patch("/{week_start}/variant", response_model=VariantResponse)
async def patch_variant(
    week_start: str,
    payload: PatchVariantPayload,
    if_unmodified_since: str | None = Header(
        default=None, alias="If-Unmodified-Since"
    ),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    parsed_ius = _parse_if_unmodified_since(if_unmodified_since)

    try:
        plan_uuid = UUID(payload.plan_id)
    except (ValueError, AttributeError) as e:
        raise AppException(
            422, "plan_id non valido.", "validation_error"
        ) from e

    visibility_enum: Visibility | None = None
    if payload.visibility:
        try:
            visibility_enum = Visibility(payload.visibility)
        except ValueError as e:
            raise AppException(
                422, "visibility non valida.", "validation_error"
            ) from e

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
