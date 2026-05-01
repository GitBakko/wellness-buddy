"""Shopping router — Plan 02b stub; Phase 2 implements list generator."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/shopping", tags=["shopping"])

_NOT_IMPL = {"detail": "Phase 2 implementa", "code": "not_implemented"}


@router.get("/{week_start}")
async def get_shopping(week_start: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
