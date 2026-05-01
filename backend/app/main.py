"""FastAPI application factory.

CO-MODIFIED FILE — Plan 02a + Plan 02b (resolved on Wave 2 merge).

Plan 02a establishes the FastAPI backbone: lifespan, configure_logging,
RequestIDMiddleware, IdempotentGraceMiddleware, CORS, register_exception_handlers,
and the health/version/errors routers.

Plan 02b extends it by:
  * binding `app.state.ai_provider = build_provider()` inside lifespan (D-32, AI-03)
  * registering the AI router + 7 stub routers (auth, plans, today, weekly,
    workout, weight, shopping, admin) — all return 501 envelopes until their
    owning plans (03/04/07) implement them.

Sources: D-21, D-31, D-32, AI-03, AUTH-12, V14, RESEARCH Pattern 11.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.factory import build_provider
from app.api import (
    admin,
    ai,
    auth,
    errors,
    health,
    plans,
    shopping,
    today,
    version,
    weekly,
    weight,
    workout,
)
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import IdempotentGraceMiddleware, RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """App startup/shutdown hook.

    Plan 02a: configure logging at boot.
    Plan 02b: bind the AI provider singleton (D-32, AI-03).
    """
    configure_logging(settings.LOG_LEVEL)
    app.state.ai_provider = build_provider()
    yield


app = FastAPI(
    title="Wellness Buddy API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(IdempotentGraceMiddleware)

register_exception_handlers(app)

for r in (
    # Plan 02a infra routers
    health.router,
    version.router,
    errors.router,
    # Plan 02b stub routers (replaced as Plans 03/04/07 ship)
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
