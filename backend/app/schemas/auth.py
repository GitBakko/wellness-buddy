"""Auth schemas — Plan 03 real impl.

Source: AUTH-01..AUTH-12, RESEARCH Pattern 9.
The `password` field caps at 200 chars to fit bcrypt's 72-byte working limit comfortably
even after UTF-8 expansion; minimum 8 enforced for register.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 — OAuth2 token-type literal, not a credential
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


class MeResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
    group_id: str | None = None
    timezone: str


class RegisterRequest(BaseModel):
    """POST /api/auth/register — invite-token-gated signup."""

    token: str = Field(min_length=8, max_length=128)
    email: EmailStr
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=200)
