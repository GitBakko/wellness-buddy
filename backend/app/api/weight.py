"""Weight router — Plan 07 implementation (replaces 02b's 501 stub).

Endpoints (all auth-gated):
  * POST   /api/weight                — upsert by (user_id, date)
  * GET    /api/weight                — current user's log, desc by date
  * PATCH  /api/weight/{weight_id}    — update kg (cross-user 404)
  * DELETE /api/weight/{weight_id}    — remove (cross-user 404)

Source: WEIGHT-01, WEIGHT-02, T-API-03, V13.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.weight import WeightLogIn, WeightLogOut, WeightLogPatch
from app.services import weight_service

router = APIRouter(prefix="/api/weight", tags=["weight"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WeightLogOut)
async def post_weight(
    body: WeightLogIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WeightLogOut:
    row = await weight_service.upsert_weight(
        session, user_id=user.id, on_date=body.date, weight_kg=body.weight_kg
    )
    return WeightLogOut(id=str(row.id), date=row.date, weight_kg=row.weight_kg)


@router.get("", response_model=list[WeightLogOut])
async def list_weights(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[WeightLogOut]:
    rows = await weight_service.list_weights(session, user_id=user.id)
    return [
        WeightLogOut(id=str(r.id), date=r.date, weight_kg=r.weight_kg)
        for r in rows
    ]


@router.patch("/{weight_id}", response_model=WeightLogOut)
async def patch_weight(
    weight_id: UUID,
    body: WeightLogPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WeightLogOut:
    if body.weight_kg is None:
        raise AppException(400, "Indica un peso valido.", "missing_weight")
    row = await weight_service.update_weight(
        session,
        user_id=user.id,
        weight_id=weight_id,
        weight_kg=body.weight_kg,
    )
    return WeightLogOut(id=str(row.id), date=row.date, weight_kg=row.weight_kg)


@router.delete("/{weight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weight(
    weight_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await weight_service.delete_weight(
        session, user_id=user.id, weight_id=weight_id
    )
