"""ASGI middleware: per-request ID injection + idempotency-grace passthrough.

Source: D-21 (structlog request-ID), AUTH-07/PITFALLS#4 (10s grace owned by service layer Plan 03).
The middleware here only stamps `X-Request-ID` and binds it to structlog contextvars so every
log line emitted during a request inherits the same request_id.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generate or propagate `X-Request-ID` and bind it to structlog contextvars."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        # Bind for structlog (merge_contextvars processor picks it up)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        finally:
            # Always clear so contextvars don't leak to the next request handler
            structlog.contextvars.clear_contextvars()
        response.headers["X-Request-ID"] = request_id
        return response


class IdempotentGraceMiddleware(BaseHTTPMiddleware):
    """Passthrough placeholder for the auth refresh 10s grace window.

    Plan 03 implements actual grace logic in `services/auth_service.py` (per RESEARCH Pattern 9).
    Keeping the middleware in main.py wiring stable means Plan 03 can extend service-side without
    touching app factory.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        return await call_next(request)
