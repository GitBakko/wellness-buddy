"""Custom exceptions ensuring all API errors return JSON `{detail: string, code: string}`.

Source: AUTH-12, D-20. Frontend translates `code` -> Italian copy via `copy.it.ts`.
Backend `detail` stays machine-readable (e.g. `INVALID_CREDENTIALS`); frontend localizes.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(StarletteHTTPException):
    """Application-level HTTP exception that always carries a machine code.

    Use this in route handlers to guarantee the AUTH-12 envelope shape:
        raise AppException(401, "INVALID_CREDENTIALS", "invalid_credentials")
    """

    def __init__(self, status_code: int, detail: str, code: str) -> None:
        super().__init__(status_code=status_code, detail={"detail": detail, "code": code})


def _envelope(status: int, detail: str, code: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": detail, "code": code})


def register_exception_handlers(app: FastAPI) -> None:
    """Wire FastAPI exception handlers that enforce `{detail, code}` for ALL responses."""

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        # AppException carries a dict already shaped {detail, code}
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            payload: dict[str, Any] = dict(exc.detail)
            return JSONResponse(status_code=exc.status_code, content=payload)
        # Fallback for raw HTTPException without code
        return _envelope(exc.status_code, str(exc.detail), f"http_{exc.status_code}")

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        # 422 from Pydantic validation — frontend code 'validation_error' maps to italian copy
        return _envelope(422, "validation_error", "validation_error")

    @app.exception_handler(Exception)
    async def fallback_handler(_: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        # Catch-all so 500s never leak stack traces to clients
        return _envelope(500, "internal_error", "internal_error")
