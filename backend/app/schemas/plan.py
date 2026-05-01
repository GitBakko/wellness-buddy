"""NutritionPlan response/request schemas. Plan 04 ships upload/diff/assign shapes.

The original `PlanResponse` and `PlanListItem` from Plan 02 are kept as the
authoritative shapes; Plan 04 extends with `PlanUploadResponse` (parser report fields),
`PlanDiffResponse` (section-level), and `AssignPlanRequest` (admin payload).
"""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import StrictModel


class PlanResponse(StrictModel):
    id: str
    name: str
    is_active: bool


class PlanListItem(PlanResponse):
    uploaded_at: str


class PlanUploadResponse(PlanListItem):
    """Returned by POST /api/plans/upload — extends list item with parser diagnostics."""

    parse_warnings: list[str] = Field(default_factory=list)
    unrecognized_headings: list[str] = Field(default_factory=list)


class PlanDiffResponse(StrictModel):
    """Section-level diff (PLAN-09)."""

    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)


class AssignPlanRequest(StrictModel):
    """Body for POST /api/admin/users/{user_id}/assign-plan (PLAN-10)."""

    plan_id: str
