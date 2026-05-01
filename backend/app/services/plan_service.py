"""Plan service: upload, list, activate, diff, admin-assign.

Source: PLAN-07..PLAN-10, T-PLAN-01, V11 (partial unique index "one active per user"),
RESEARCH Pattern 10.

Key invariants:
  * `MAX_FILE_BYTES` = 1 MB cap at the API boundary (V12 / DoS guard)
  * Activation is atomic within a single transaction:
        UPDATE … SET is_active=false WHERE user_id=$1 AND is_active=true;
        UPDATE … SET is_active=true  WHERE id=$2 AND user_id=$1;
    This sequencing avoids the partial unique index conflict that would otherwise
    fire on a naive "set new=true first" path.
  * All user-scoped queries filter `WHERE user_id == current_user.id` — cross-user
    activation/diff returns 404 (invisible) instead of 403 (visible). The frontend
    code maps both to the same italian copy.
  * `admin_assign_plan` does NOT scope by user_id (admin can reassign any plan).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.plan import NutritionPlan
from app.parsers.plan_parser import ParseReport, parse_and_validate
from app.services.audit_service import write_audit

# V12 — at most 1 MB markdown blob accepted at the API boundary.
MAX_FILE_BYTES = 1 * 1024 * 1024

# Italian copy — surfaced to the frontend via AUTH-12 envelope (`detail`).
_MSG_TOO_LARGE = "Il file supera il limite di 1 MB."
_MSG_PARSE_FAILED = (
    "Non sono riuscito a leggere il piano. Verifica che il formato sia corretto."
)
_MSG_NOT_FOUND = "Piano non trovato."


# ──────────────────────────────────────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────────────────────────────────────


async def upload_plan(
    session: AsyncSession,
    *,
    user_id: UUID,
    name: str,
    raw_bytes: bytes,
) -> tuple[NutritionPlan, ParseReport]:
    """Validate size, parse markdown, persist NutritionPlan row, audit-log."""
    if len(raw_bytes) > MAX_FILE_BYTES:
        raise AppException(400, _MSG_TOO_LARGE, "too_large")

    try:
        schema, report = parse_and_validate(raw_bytes)
    except Exception as e:
        raise AppException(400, _MSG_PARSE_FAILED, "parse_failed") from e

    plan = NutritionPlan(
        user_id=user_id,
        name=name,
        # Decode with utf-8-sig to drop any BOM (the normalizer also handles this,
        # but raw_md is stored as the source-of-truth — we want a clean string).
        raw_md=raw_bytes.decode("utf-8-sig", errors="replace"),
        parsed_json=schema.model_dump(),
        is_active=False,
    )
    session.add(plan)
    await session.flush()  # populate plan.id for audit row
    await write_audit(
        session,
        actor_id=user_id,
        action="plan_upload",
        target_type="nutrition_plan",
        target_id=plan.id,
        payload={"name": name, "warnings": list(report.warnings)},
    )
    await session.commit()
    await session.refresh(plan)
    return plan, report


# ──────────────────────────────────────────────────────────────────────────────
# List
# ──────────────────────────────────────────────────────────────────────────────


async def list_plans(
    session: AsyncSession, *, user_id: UUID
) -> list[NutritionPlan]:
    """Return current user's plans, latest first."""
    rows = (
        await session.scalars(
            select(NutritionPlan)
            .where(NutritionPlan.user_id == user_id)
            .order_by(NutritionPlan.uploaded_at.desc())
        )
    ).all()
    return list(rows)


# ──────────────────────────────────────────────────────────────────────────────
# Activate (atomic deactivate-then-activate)
# ──────────────────────────────────────────────────────────────────────────────


async def activate_plan(
    session: AsyncSession, *, user_id: UUID, plan_id: UUID
) -> NutritionPlan:
    """Activate `plan_id` and deactivate the previously active plan in a single tx.

    V11 partial unique index requires the previous active row to be set false BEFORE
    the new row is set true; we issue the UPDATE before the assignment to be safe.
    """
    plan = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.id == plan_id, NutritionPlan.user_id == user_id
            )
        )
    ).first()
    if not plan:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")

    # Deactivate previous active plan(s) — idempotent if already false.
    await session.execute(
        update(NutritionPlan)
        .where(
            NutritionPlan.user_id == user_id,
            NutritionPlan.is_active.is_(True),
            NutritionPlan.id != plan.id,
        )
        .values(is_active=False)
    )
    plan.is_active = True

    await write_audit(
        session,
        actor_id=user_id,
        action="plan_activate",
        target_type="nutrition_plan",
        target_id=plan.id,
        payload={},
    )
    await session.commit()
    await session.refresh(plan)
    return plan


# ──────────────────────────────────────────────────────────────────────────────
# Diff (section-level)
# ──────────────────────────────────────────────────────────────────────────────


def _section_present(value: object) -> bool:
    """A section is "present" if it carries non-empty content."""
    if value is None:
        return False
    if isinstance(value, list | dict | str) and len(value) == 0:
        return False
    if isinstance(value, dict):
        # Phase 1 macros default-factory yields {kcal:0, protein_g:0, ...} — treat as absent.
        if all(v in (0, None, "", [], {}) for v in value.values()):
            return False
    return True


async def diff_against_active(
    session: AsyncSession, *, user_id: UUID, candidate_plan_id: UUID
) -> dict[str, list[str]]:
    """Compute section-level diff of `candidate_plan_id` vs the user's active plan."""
    candidate = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.id == candidate_plan_id,
                NutritionPlan.user_id == user_id,
            )
        )
    ).first()
    if not candidate:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")

    active = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.user_id == user_id,
                NutritionPlan.is_active.is_(True),
            )
        )
    ).first()

    c = candidate.parsed_json or {}
    if not active:
        # First plan: every present section is "added".
        present = [k for k, v in c.items() if _section_present(v)]
        return {"added": sorted(present), "removed": [], "changed": []}

    a = active.parsed_json or {}
    added: list[str] = []
    removed: list[str] = []
    changed: list[str] = []
    for key in set(a.keys()) | set(c.keys()):
        in_a = _section_present(a.get(key))
        in_c = _section_present(c.get(key))
        if in_c and not in_a:
            added.append(key)
        elif in_a and not in_c:
            removed.append(key)
        elif in_a and in_c and a.get(key) != c.get(key):
            changed.append(key)
    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "changed": sorted(changed),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Admin: assign existing plan to another user (PLAN-10)
# ──────────────────────────────────────────────────────────────────────────────


async def admin_assign_plan(
    session: AsyncSession,
    *,
    admin_id: UUID,
    target_user_id: UUID,
    plan_id: UUID,
) -> NutritionPlan:
    """Reassign an existing plan's `user_id`. Audit-logged.

    No user-scope filter — admin (gated by `Depends(require_admin)` upstream) can
    move any plan. The new owner must exist (FK on nutrition_plans.user_id will
    raise IntegrityError if the target user is missing — surface as 400).
    """
    plan = (
        await session.scalars(
            select(NutritionPlan).where(NutritionPlan.id == plan_id)
        )
    ).first()
    if not plan:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")

    plan.user_id = target_user_id
    # Reassigning a plan resets its is_active flag — the new owner will activate
    # explicitly (otherwise the partial unique index could collide if the new
    # owner already has an active plan).
    plan.is_active = False
    await write_audit(
        session,
        actor_id=admin_id,
        action="plan_assign",
        target_type="nutrition_plan",
        target_id=plan.id,
        payload={"target_user_id": str(target_user_id)},
    )
    await session.commit()
    await session.refresh(plan)
    return plan
