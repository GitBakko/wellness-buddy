"""Version endpoint (FND-06).

Frontend polls this to detect deploys and prompt SW update; intentionally
excluded from OpenAPI schema since it's an operational concern, not API surface.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["version"])


@router.get("/version.json", include_in_schema=False)
async def version() -> dict[str, str]:
    return {"version": settings.APP_VERSION, "build_hash": settings.BUILD_HASH}
