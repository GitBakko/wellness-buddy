"""Today router — Plan 02b stub; Plan 07 implements landing aggregator."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/today", tags=["today"])

_NOT_IMPL = {"detail": "Plan 07 implementa", "code": "not_implemented"}


@router.get("")
async def get_today() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/meal/{meal_type}/complete")
async def complete_meal(meal_type: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
