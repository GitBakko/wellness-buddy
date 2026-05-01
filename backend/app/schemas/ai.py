"""AI request/response schemas. Plan 02b ships shapes; Sprint 5 wires real fields.

Sources: AI-01, AI-02, AI-03 — establishes contract for downstream Sprint 5
provider implementations even though Sprint 1 endpoints return 501.
"""

from __future__ import annotations

from pydantic import BaseModel


class AIRequest(BaseModel):
    """Generic AI request envelope. Sprint 5 will narrow per-endpoint."""

    prompt: str | None = None
    context: dict[str, object] = {}


class AIResponse(BaseModel):
    """Generic AI response envelope. Sprint 5 will narrow per-endpoint."""

    text: str
    provider: str
