"""Plans router — Plan 02b stub; Plan 04 implements upload/activate/diff."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/plans", tags=["plans"])

_NOT_IMPL = {"detail": "Plan 04 implementa", "code": "not_implemented"}


@router.post("/upload")
async def upload() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.get("")
async def list_plans() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/{plan_id}/activate")
async def activate(plan_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.get("/{plan_id}/diff")
async def diff(plan_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
