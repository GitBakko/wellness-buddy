"""Audit log helper (D-23).

Caller passes the active session; we add the row but DO NOT commit — letting the caller
batch with the rest of the request transaction. Phase 1 wires this on Group/User/NutritionPlan
mutations; Phase 4 expands.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def write_audit(
    session: AsyncSession,
    *,
    actor_id: UUID | None,
    action: str,
    target_type: str,
    target_id: UUID | None,
    payload: dict | None = None,
) -> None:
    """Append an audit row to the current transaction. Caller is responsible for commit/rollback."""
    session.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=payload or {},
        )
    )
