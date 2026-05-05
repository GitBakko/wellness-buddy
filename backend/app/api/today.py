"""Today router — Plan 07 implementation (replaces 02b's 501 stub).

Endpoints:
  * GET  /api/today                              — aggregator (greeting + meals + weight + workout)
  * POST /api/today/meal/{meal_type}/complete    — mark today's meal as completed

Plan 02-07 adds an optional ``?user_id={partner}`` query parameter on GET that
swaps the auth dependency to ``get_user_with_group_access`` so a partner in
the same group can read each other's group_shared meals (private meals are
filtered server-side — V13 information-disclosure mitigation).

Source: TODAY-01..TODAY-08, AUTH-12, UI-SPEC §7.2, FAM-06, FAM-07.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_user_with_group_access
from app.models.user import User
from app.schemas.today import MealCompleteResponse, TodayResponse
from app.services import today_service

router = APIRouter(prefix="/api/today", tags=["today"])


@router.get("", response_model=TodayResponse)
async def get_today(
    user_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TodayResponse:
    """Aggregated /today payload — greeting + meals + today's weight/workout.

    Plan 02-07 — when ``user_id`` is supplied AND it differs from the
    authenticated user, build the partner's payload and FILTER OUT every meal
    whose visibility is not ``group_shared``. Cross-group access raises 404
    via :func:`app.core.deps.get_user_with_group_access` (V13 envelope).
    """
    target = current_user
    if user_id is not None and user_id != current_user.id:
        target = await get_user_with_group_access(user_id, current_user, session)
        payload = await today_service.build_today_payload(session, user=target)
        # Cross-user view: only group_shared meals visible. Private meals
        # (breakfast/snack default) hidden — never reveal a partner's private items.
        payload.meals = [m for m in payload.meals if m.visibility == "group_shared"]
        # Cross-user view: weight + workout are ALWAYS private (CONV-14) — hide them.
        payload.weight_today = None
        payload.workout_today = None
        return payload
    return await today_service.build_today_payload(session, user=target)


@router.post("/meal/{meal_type}/complete", response_model=MealCompleteResponse)
async def complete_meal(
    meal_type: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MealCompleteResponse:
    """Mark today's meal_type as completed. Persists via WeeklyPlanVariant.

    Always operates on the authenticated user's own row — completing a partner's
    meal is meaningless and would violate the FAM-04 own-only mutation rule.
    """
    variant = await today_service.complete_meal(session, user=user, meal_type=meal_type)
    return MealCompleteResponse(
        meal_type=variant.meal_type,
        completed=variant.completed,
        version=variant.version,
    )
