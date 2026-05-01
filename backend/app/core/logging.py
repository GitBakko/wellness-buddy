"""structlog JSON config + sensitive-key redaction.

Source: D-21 (structured logging), V7 (mask password/Authorization/cookie).
Request ID is bound by RequestIDMiddleware (see middleware.py) via `contextvars`,
which structlog includes automatically through `merge_contextvars`.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

# V7 (RESEARCH §Threats): never log secrets — redact known sensitive keys before serialization.
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "hashed_password",
        "secret",
        "secret_key",
        "authorization",
        "cookie",
        "set-cookie",
        "token",
        "refresh_token",
        "access_token",
        "api_key",
    }
)


def _redact_sensitive(_logger: Any, _name: str, event: dict[str, Any]) -> dict[str, Any]:
    """structlog processor: replace sensitive values with '***REDACTED***'."""
    for key in list(event.keys()):
        if key.lower() in _SENSITIVE_KEYS:
            event[key] = "***REDACTED***"
    return event


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog + stdlib logging to emit JSON to stdout.

    Idempotent — safe to call multiple times (e.g. tests reload the app).
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # picks up request_id bound by middleware
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _redact_sensitive,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
