"""Auth schemas — minimal placeholders. Plan 03 owns real impl."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 — OAuth2 token-type literal, not a credential


class MeResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
    group_id: str | None = None
    timezone: str
