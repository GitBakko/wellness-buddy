"""Frontend error sink (D-18).

Sprint 1 keeps it dumb: just log structured warnings. Sprint 4 may forward to Sentry.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

log = structlog.get_logger()
router = APIRouter(tags=["errors"])


class ErrorReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    stack: str | None = None
    url: str | None = None
    user_agent: str | None = None


@router.post("/api/errors", status_code=204)
async def log_error(report: ErrorReport) -> None:
    log.warning("frontend_error", **report.model_dump())
