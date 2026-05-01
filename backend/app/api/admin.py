"""Admin router — Plan 04 implements PLAN-10 assign-plan endpoint.

All endpoints gated by `Depends(require_admin)` so non-admin requests return a
403 forbidden envelope before any handler runs.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.plan import AssignPlanRequest, PlanResponse
from app.services import plan_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/users/{user_id}/assign-plan", response_model=PlanResponse)
async def assign_plan(
    user_id: UUID,
    body: AssignPlanRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> PlanResponse:
    """Reassign an existing nutrition plan to another user (PLAN-10).

    Admin-only. The plan's `is_active` flag is reset to False on reassignment so
    the new owner explicitly activates it (avoids partial-unique-index conflict
    if the new owner already has an active plan).
    """
    plan = await plan_service.admin_assign_plan(
        session,
        admin_id=admin.id,
        target_user_id=user_id,
        plan_id=UUID(body.plan_id),
    )
    return PlanResponse(id=str(plan.id), name=plan.name, is_active=plan.is_active)
