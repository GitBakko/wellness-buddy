"""Invite schemas — Plan 03 real impl. Admin generates 24h single-use tokens."""

from __future__ import annotations

from pydantic import BaseModel


class InviteCreateResponse(BaseModel):
    """POST /api/auth/invite returns the freshly generated token + ISO expiry."""

    token: str
    expires_at: str  # ISO datetime (timezone-aware)
