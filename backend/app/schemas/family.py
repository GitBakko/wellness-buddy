"""Family API schemas (FAM-02, FAM-03, D-15).

Pydantic v2 strict bodies for ``PATCH /api/family/share/{variant_id}``. The
``visibility`` field accepts only the locked enum values; anything else
collapses to a 400 validation error so the client can show
``copy.family.sharePerMealError``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ShareTogglePayload(BaseModel):
    """PATCH body — owner sets a meal's visibility."""

    model_config = ConfigDict(extra="forbid")

    visibility: Literal["private", "group_shared"]


class VariantShareResponse(BaseModel):
    """Response shape for the share toggle — frontend mirrors this in services/family.ts."""

    model_config = ConfigDict(extra="forbid")

    id: str
    visibility: str
    version: int
    updated_at: str
