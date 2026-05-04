"""Shopping list schemas (SHOP-01..SHOP-06).

Strict ``extra="forbid"`` Pydantic v2 contracts at the API boundary so
malformed payloads from the client (or aggregation bugs) surface as 422
instead of being silently accepted (T-02-05-05 mitigation).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ShoppingItem(BaseModel):
    """Single aggregated row in the shopping list."""

    model_config = ConfigDict(extra="forbid")

    canonical_name: str  # lowercase aggregation key (``Pomodoro`` → ``pomodoro``)
    name_display: str  # human-friendly title-case for UI (``"Pomodoro"``)
    amount: float | None  # ``None`` for q.b. items
    unit: str | None  # ``g`` / ``kg`` / ``ml`` / ``pizzico`` / ``qb`` / ``None``
    quantity_it: str  # localized rendering (``"400 g"`` / ``"q.b."`` / ``"2 confezione"``)
    category: str  # one of the 5 fixed Italian categories
    checked: bool = False
    sources: list[str] = Field(default_factory=list)  # meal slots that contributed


class ShoppingCategorySection(BaseModel):
    """5-bucket section of the list. Categories render in ``CATEGORY_ORDER``."""

    model_config = ConfigDict(extra="forbid")

    name: str
    items: list[ShoppingItem]


class ShoppingResponse(BaseModel):
    """``GET /api/shopping/{week_start}`` payload."""

    model_config = ConfigDict(extra="forbid")

    week_start: str
    categories: list[ShoppingCategorySection]
    version: int


class CheckPayload(BaseModel):
    """``PATCH /api/shopping/{week_start}/check`` body — strict extra=forbid (T-02-05-05)."""

    model_config = ConfigDict(extra="forbid")

    canonical_name: str
    unit: str | None
    checked: bool


class ResetResponse(BaseModel):
    """``POST /api/shopping/{week_start}/reset`` payload."""

    model_config = ConfigDict(extra="forbid")

    week_start: str
    reset_at: str
