"""Auth router — Plan 02b stub; Plan 03 implements full JWT + refresh rotation."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/auth", tags=["auth"])

_NOT_IMPL = {"detail": "Plan 03 implementa", "code": "not_implemented"}


@router.post("/login")
async def login() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/logout")
async def logout() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/refresh")
async def refresh() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.get("/me")
async def me() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/invite")
async def invite() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.post("/register")
async def register() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
