"""Family API — share toggle (FAM-02, FAM-03, D-15).

Endpoints:
  * PATCH /api/family/share/{variant_id} — owner sets visibility per-meal

Owner-only. Non-owner attempts return 404 (V13 envelope) — never reveal
that the variant exists when the caller is not its owner.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.family import ShareTogglePayload, VariantShareResponse
from app.services import family_service

router = APIRouter(prefix="/api/family", tags=["family"])


@router.patch("/share/{variant_id}", response_model=VariantShareResponse)
async def patch_share(
    variant_id: UUID,
    payload: ShareTogglePayload,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    row = await family_service.toggle_share(
        session,
        user=user,
        variant_id=variant_id,
        visibility=payload.visibility,
    )
    return {
        "id": str(row.id),
        "visibility": row.visibility.value,
        "version": row.version,
        "updated_at": row.updated_at.isoformat() if row.updated_at else "",
    }
