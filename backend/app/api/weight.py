"""Weight router — Plan 02b stub; Plan 07 implements log CRUD + chart feed."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/weight", tags=["weight"])

_NOT_IMPL = {"detail": "Plan 07 implementa", "code": "not_implemented"}


@router.post("")
async def create_weight() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.get("")
async def list_weights() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.patch("/{weight_id}")
async def update_weight(weight_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.delete("/{weight_id}")
async def delete_weight(weight_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
