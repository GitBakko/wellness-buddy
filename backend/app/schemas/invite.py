"""Invite schemas — minimal placeholders. Plan 03 owns real impl."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class InviteCreateRequest(BaseModel):
    email: EmailStr
    role: str = "user"
    group_id: str | None = None


class InviteResponse(BaseModel):
    token: str
    expires_at: str  # ISO datetime
