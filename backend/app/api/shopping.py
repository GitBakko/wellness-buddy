"""Shopping API (SHOP-01..SHOP-06; SHOP-07 PDF endpoint scaffold — Plan 02-06 wires).

Plan 02-05 implements:
  * GET    /api/shopping/{week_start}            — categorized aggregated list
  * PATCH  /api/shopping/{week_start}/check      — LWW checkbox toggle
  * POST   /api/shopping/{week_start}/reset      — clear all check state
  * POST   /api/shopping/{week_start}/export-pdf — 501 scaffold (Plan 02-06)

All endpoints are own-user only Phase 2 (T-02-05-02 Information disclosure
mitigation). Plan 02-07 wires ``get_user_with_group_access`` for cross-user
reads with the 404 V13 contract.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.shopping import (
    CheckPayload,
    ResetResponse,
    ShoppingResponse,
)
from app.services import shopping_service

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


def _parse_week_start(week_start: str) -> date:
    try:
        return date.fromisoformat(week_start)
    except ValueError as exc:
        raise AppException(422, "Formato data non valido.", "invalid_week_start") from exc


@router.get("/{week_start}", response_model=ShoppingResponse)
async def get_shopping(
    week_start: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    return await shopping_service.aggregate_for_week(session, user=user, week_start=ws)


@router.patch("/{week_start}/check", response_model=ShoppingResponse)
async def patch_check(
    week_start: str,
    payload: CheckPayload,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    return await shopping_service.toggle_check(
        session,
        user=user,
        week_start=ws,
        canonical_name=payload.canonical_name,
        unit=payload.unit,
        checked=payload.checked,
    )


@router.post("/{week_start}/reset", response_model=ResetResponse)
async def post_reset(
    week_start: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    ws = _parse_week_start(week_start)
    await shopping_service.reset_shopping_list_for_user(session, user_id=user.id, week_start=ws)
    return {"week_start": ws.isoformat(), "reset_at": datetime.now(UTC).isoformat()}


@router.post("/{week_start}/export-pdf")
async def export_pdf(
    week_start: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Plan 02-06 wires this with PdfExporter from Plan 02-01.

    Phase 2 wave order: this plan (02-05) ships the data layer + UI button
    that calls this endpoint. Plan 02-06 then replaces the body with the
    actual ``PdfExporter.render_shopping_list`` call.
    """
    raise AppException(501, "Esportazione PDF non ancora attiva.", "not_implemented")
