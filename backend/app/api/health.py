"""Health probe endpoint (FND-03).

Returns 200 with `{status, version, build_hash}` so reverse proxy + uptime checks
can verify the app is alive without hitting authenticated paths.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "build_hash": settings.BUILD_HASH,
    }
