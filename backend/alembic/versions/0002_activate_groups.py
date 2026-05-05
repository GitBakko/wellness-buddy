"""Activate groups for all existing users (D-22, D-23, FAM-01).

Phase 1 baseline 0000_baseline.py created the ``groups`` table + ``users.group_id`` FK.
Plan 02-04 (revision ``8137b2e24001``) added the per-day variant unique constraint.
Plan 02-07 backfills: for each User without a ``group_id``, create a personal
household Group named ``"{username} · household"`` and link them.

Idempotent — re-running this migration is a no-op once every user has a group.

Revision ID: 0002
Revises: 8137b2e24001
Create Date: 2026-05-05
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "8137b2e24001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Backfill personal household group for every user without one."""
    bind = op.get_bind()
    # Reflective SQL — DOES NOT import app.models so the migration stays stable
    # if the User/Group ORM shape evolves later.
    users_t = sa.table(
        "users",
        sa.column("id", sa.UUID()),
        sa.column("username", sa.String()),
        sa.column("group_id", sa.UUID()),
    )
    groups_t = sa.table(
        "groups",
        sa.column("id", sa.UUID()),
        sa.column("name", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )

    # Idempotency: only operate on users without a group.
    rows = bind.execute(
        sa.select(users_t.c.id, users_t.c.username).where(users_t.c.group_id.is_(None))
    ).fetchall()

    if not rows:
        return  # All users already have a group — migration is already applied.

    now = datetime.now(UTC)
    for user_id, username in rows:
        new_group_id = uuid.uuid4()
        bind.execute(
            groups_t.insert().values(
                id=new_group_id,
                name=f"{username} · household",
                created_at=now,
            )
        )
        bind.execute(
            users_t.update()
            .where(users_t.c.id == user_id)
            .values(group_id=new_group_id)
        )


def downgrade() -> None:
    """Reverse: null out users.group_id, delete personal households.

    NOTE: Destructive — only safe when no shared resources have been written
    yet (Phase 2 is the first phase using group_id at all).
    """
    bind = op.get_bind()
    users_t = sa.table("users", sa.column("group_id", sa.UUID()))
    groups_t = sa.table("groups", sa.column("name", sa.String()))
    # Null out user.group_id pointers
    bind.execute(users_t.update().values(group_id=None))
    # Delete only "% · household" personal groups (manually-created groups untouched)
    bind.execute(groups_t.delete().where(groups_t.c.name.like("% · household")))
