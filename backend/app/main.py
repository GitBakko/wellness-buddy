"""FastAPI application factory.

Lifespan stub here — Plan 02b extends it to bind `app.state.ai_provider`
(per AI-03, D-32). Co-mod boundary: this file is owned by both 02a (skeleton)
and 02b (AI provider binding). 02a establishes structure + middlewares + routers;
02b adds the provider construction inside `lifespan`.

Routers wired in 02a: health, version, errors. Auth/plans/today/etc. land later.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import errors, health, version
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import IdempotentGraceMiddleware, RequestIDMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """App startup/shutdown hook.

    Plan 02b extends:
        from app.ai.factory import build_provider
        _app.state.ai_provider = build_provider()
    """
    configure_logging(settings.LOG_LEVEL)
    # Plan 02b extends: _app.state.ai_provider = build_provider()
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

for r in (health.router, version.router, errors.router):
    app.include_router(r)
