"""User request/response schemas.

Plan 03 extends with login/register/me endpoints; Phase 1 ships the read shape so other
plans can `from app.schemas.user import UserOut` without circular dependencies.
"""

from __future__ import annotations

from pydantic import EmailStr

from app.schemas.common import StrictModel


class UserBase(StrictModel):
    email: EmailStr
    username: str
    role: str = "user"
    timezone: str = "Europe/Rome"


class UserOut(UserBase):
    id: str
    group_id: str | None = None
