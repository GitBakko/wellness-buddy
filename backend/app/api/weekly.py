"""Weekly router — Plan 02b stub; Phase 2 implements weekly aggregation."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/weekly", tags=["weekly"])

_NOT_IMPL = {"detail": "Phase 2 implementa", "code": "not_implemented"}


@router.get("/{week_start}")
async def get_weekly(week_start: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
