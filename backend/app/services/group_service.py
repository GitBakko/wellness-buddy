"""Group service — household creation + cross-user authz helpers (FAM-01, Pitfall #16).

``ensure_personal_group`` is called from the auth register flow so every new
user lands in a personal household Group from creation. Mitigation for
PITFALL #16 (group migration race): the Alembic 0002 migration backfills
users that existed BEFORE Phase 2 deploy; this helper handles users
registered AFTER the deploy, so ``users.group_id`` never stays NULL.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.models.user import User


async def ensure_personal_group(session: AsyncSession, user: User) -> Group:
    """Auto-create a personal household group for ``user`` when missing.

    Behaviour:
      * If ``user.group_id`` already points to a real Group → return it (no-op).
      * If ``user.group_id`` is set but the row is gone (FK cascade) → create
        a fresh household and re-link.
      * If ``user.group_id`` is None → create ``"{username} · household"``
        and link via ``user.group_id``.

    The caller commits the surrounding transaction; this helper only
    ``flush()`` so ``user.id`` and ``group.id`` are visible.
    """
    if user.group_id is not None:
        existing = (await session.scalars(select(Group).where(Group.id == user.group_id))).first()
        if existing:
            return existing

    group = Group(
        name=f"{user.username} · household",
        created_at=datetime.now(UTC),
    )
    session.add(group)
    await session.flush()
    user.group_id = group.id
    await session.flush()
    return group
