"""FastAPI app factory + lifespan.

CO-MODIFIED FILE — Plan 02a + Plan 02b.

This file was originally scoped to Plan 02a (which creates the FastAPI backbone:
configure_logging, request-id middleware, CORS, error handlers, models, etc).
Plan 02b extends it to bind the AI provider singleton at lifespan startup and
register the AI + stub routers.

WORKTREE-RACE NOTE: At Plan 02b execution time Plan 02a had NOT yet landed in
this worktree. We therefore created a minimal lifespan + router include loop
sufficient for Plan 02b acceptance criteria. Wave 2 merge will reconcile with
Plan 02a's richer scaffolding (DB engine bind, structlog wiring, version/health
routers, error handlers). The two changes are designed to be additive:

  * Plan 02a adds: configure_logging(), request-id middleware, CORS, exception
    handlers, app.state.engine, health.router, version.router, errors.router.
  * Plan 02b adds (this file's contribution): app.state.ai_provider = build_provider(),
    auth/plans/today/weekly/workout/weight/shopping/ai/admin routers.

The lifespan body and the router include loop are the merge points. See
01-02b-SUMMARY.md "Co-modification" section for reconcile guidance.

Sources: D-31, D-32, AI-03, RESEARCH Pattern 11.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ai.factory import build_provider
from app.api import (
    admin,
    ai,
    auth,
    plans,
    shopping,
    today,
    weekly,
    weight,
    workout,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """App startup/shutdown.

    Plan 02b binds the AI provider singleton (D-32). Plan 02a will add
    configure_logging() and the SQLAlchemy async engine alongside.
    """
    # Plan 02a will insert: configure_logging() here
    app.state.ai_provider = build_provider()
    # Plan 02a will insert: app.state.engine = create_async_engine(settings.DATABASE_URL, ...)
    yield
    # Plan 02a will insert: await app.state.engine.dispose()


app = FastAPI(
    title="Wellness Buddy API",
    version="0.1.0",
    lifespan=lifespan,
)

# Plan 02a will add: CORSMiddleware, RequestIDMiddleware, exception handlers,
# health.router, version.router, errors.router

for r in (
    auth.router,
    plans.router,
    today.router,
    weekly.router,
    workout.router,
    weight.router,
    shopping.router,
    ai.router,
    admin.router,
):
    app.include_router(r)
