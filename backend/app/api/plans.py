"""Plans router — Plan 04 implementation (PLAN-01, PLAN-07..PLAN-09).

Endpoints (all auth-gated via `Depends(get_current_user)`):
  POST   /api/plans/upload        multipart .md → parse + persist (201)
  GET    /api/plans               list current user's plans (desc by uploaded_at)
  POST   /api/plans/{id}/activate atomic deactivate-prev → activate-this
  GET    /api/plans/{id}/diff     section-level diff vs active plan
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.plan import (
    PlanDiffResponse,
    PlanListItem,
    PlanResponse,
    PlanUploadResponse,
)
from app.services import plan_service

router = APIRouter(prefix="/api/plans", tags=["plans"])

_MSG_BAD_FILE_TYPE = "Solo file .md sono supportati."


@router.post("/upload", response_model=PlanUploadResponse, status_code=201)
async def upload(
    file: UploadFile = File(...),
    name: str = Form(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PlanUploadResponse:
    """Upload markdown nutrition plan (PLAN-01).

    Validation:
      * filename must end with `.md` (case-insensitive)
      * size cap enforced inside the service (`MAX_FILE_BYTES = 1 MB`)

    Returns the freshly-persisted plan + parser diagnostics (warnings + unrecognized
    headings — non-blocking per PLAN-05).
    """
    filename = (file.filename or "").lower()
    if not filename.endswith(".md"):
        raise AppException(400, _MSG_BAD_FILE_TYPE, "bad_file_type")

    raw = await file.read()
    plan, report = await plan_service.upload_plan(
        session, user_id=user.id, name=name, raw_bytes=raw
    )
    return PlanUploadResponse(
        id=str(plan.id),
        name=plan.name,
        uploaded_at=plan.uploaded_at.isoformat(),
        is_active=plan.is_active,
        parse_warnings=list(report.warnings),
        unrecognized_headings=list(report.unrecognized_headings),
    )


@router.get("", response_model=list[PlanListItem])
async def list_plans(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[PlanListItem]:
    """List the current user's plans, latest first (PLAN-07)."""
    plans = await plan_service.list_plans(session, user_id=user.id)
    return [
        PlanListItem(
            id=str(p.id),
            name=p.name,
            uploaded_at=p.uploaded_at.isoformat(),
            is_active=p.is_active,
        )
        for p in plans
    ]


@router.post("/{plan_id}/activate", response_model=PlanResponse)
async def activate(
    plan_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PlanResponse:
    """Activate a plan (PLAN-08). Service deactivates previous active plan first."""
    plan = await plan_service.activate_plan(
        session, user_id=user.id, plan_id=plan_id
    )
    return PlanResponse(id=str(plan.id), name=plan.name, is_active=plan.is_active)


@router.get("/{plan_id}/diff", response_model=PlanDiffResponse)
async def diff(
    plan_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PlanDiffResponse:
    """Section-level diff of plan vs the user's active plan (PLAN-09)."""
    result = await plan_service.diff_against_active(
        session, user_id=user.id, candidate_plan_id=plan_id
    )
    return PlanDiffResponse(**result)
