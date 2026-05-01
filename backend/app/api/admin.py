"""Admin router — Plan 02b stub; Plan 04 implements assign-plan + admin tools."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/admin", tags=["admin"])

_NOT_IMPL = {"detail": "Plan 04 implementa", "code": "not_implemented"}


@router.post("/users/{user_id}/assign-plan")
async def assign_plan(user_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
