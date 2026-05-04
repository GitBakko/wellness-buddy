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


@router.get("/api/_debug/parser-introspect")
async def parser_introspect() -> dict:
    """TEMP DIAGNOSTIC — confirm running parser has Plan 02-04 fixes."""
    from app.parsers import plan_parser as pp

    return {
        "module_file": pp.__file__,
        "has_is_ignored_advisory": hasattr(pp, "_is_ignored_advisory"),
        "section_stems_ignored": list(getattr(pp, "SECTION_STEMS_IGNORED", ())),
        "check_idratazione": (
            pp._is_ignored_advisory("idratazione") if hasattr(pp, "_is_ignored_advisory") else None
        ),
    }
