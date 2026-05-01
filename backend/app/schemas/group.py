"""Group request/response schemas (Phase 1 placeholder; Phase 2 family sync extends)."""

from __future__ import annotations

from app.schemas.common import StrictModel


class GroupBase(StrictModel):
    name: str


class GroupOut(GroupBase):
    id: str
