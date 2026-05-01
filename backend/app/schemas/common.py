"""Strict-mode base for every Pydantic v2 schema.

`extra='forbid'` rejects unknown keys at validation — mismatches between client and server
fail fast at the boundary instead of silently dropping fields. Every request DTO inherits this.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Pydantic v2 base with `extra='forbid'` — reject unknown keys at the boundary."""

    model_config = ConfigDict(extra="forbid")
