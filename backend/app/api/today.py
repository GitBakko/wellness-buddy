"""Today router — Plan 07 implementation (replaces 02b's 501 stub).

Endpoints:
  * GET  /api/today                                — aggregator (greeting + meals + weight + workout)
  * POST /api/today/meal/{meal_type}/complete      — mark today's meal as completed

All endpoints scope to the authenticated user (T-API-02 — User B never sees User A's data).

Source: TODAY-01..TODAY-08, AUTH-12, UI-SPEC §7.2.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.today import MealCompleteResponse, TodayResponse
from app.services import today_service

router = APIRouter(prefix="/api/today", tags=["today"])


@router.get("", response_model=TodayResponse)
async def get_today(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TodayResponse:
    """Aggregated /today payload — greeting + meals + today's weight/workout."""
    return await today_service.build_today_payload(session, user)


@router.post("/meal/{meal_type}/complete", response_model=MealCompleteResponse)
async def complete_meal(
    meal_type: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MealCompleteResponse:
    """Mark today's meal_type as completed. Persists via WeeklyPlanVariant."""
    variant = await today_service.complete_meal(
        session, user=user, meal_type=meal_type
    )
    return MealCompleteResponse(
        meal_type=variant.meal_type,
        completed=variant.completed,
        version=variant.version,
    )
