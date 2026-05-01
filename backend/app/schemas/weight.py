"""Weight log schemas — Plan 07.

Source: WEIGHT-01, WEIGHT-02. Decimal(5,2) matches the model column.
"""

from __future__ import annotations

from datetime import date as date_t
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeightLogIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date_t
    weight_kg: Decimal = Field(
        ...,
        gt=0,
        lt=Decimal("999.99"),
        description="kg with up to 2 decimal precision",
    )

    @field_validator("weight_kg", mode="before")
    @classmethod
    def _quantize(cls, v: object) -> object:
        """Coerce input to Decimal with 2-decimal precision (CONV: server canonical)."""
        if v is None:
            return v
        try:
            d = Decimal(str(v))
        except Exception:
            return v
        return d.quantize(Decimal("0.01"))


class WeightLogPatch(BaseModel):
    """Partial update — `weight_kg` is the only mutable field; `date` is immutable
    (per WEIGHT-02 — to change date, delete + recreate)."""

    model_config = ConfigDict(extra="forbid")

    weight_kg: Decimal | None = Field(
        None, gt=0, lt=Decimal("999.99")
    )
    # Allow `date` echo from the frontend so PATCH stays symmetrical with POST shape;
    # backend ignores it.
    date: date_t | None = None

    @field_validator("weight_kg", mode="before")
    @classmethod
    def _quantize(cls, v: object) -> object:
        if v is None:
            return v
        try:
            d = Decimal(str(v))
        except Exception:
            return v
        return d.quantize(Decimal("0.01"))


class WeightLogOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    date: date_t
    weight_kg: Decimal
