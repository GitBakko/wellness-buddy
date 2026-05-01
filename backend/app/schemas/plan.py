"""NutritionPlan response schemas. Plan 04 extends with upload/diff/parsed-tree shapes."""

from __future__ import annotations

from app.schemas.common import StrictModel


class PlanResponse(StrictModel):
    id: str
    name: str
    is_active: bool


class PlanListItem(PlanResponse):
    uploaded_at: str
