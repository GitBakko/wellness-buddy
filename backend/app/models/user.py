"""User model (MOD-01, MOD-09).

`timezone` defaults to `Europe/Rome` (IANA) — frontend uses this for date math
that must be timezone-aware (workout/weight logs, push reminders DST-aware).
`role` is a freeform string ('admin' | 'user') — Phase 1 keeps it simple; Phase 4 may
introduce enum + RBAC table.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampTZ

if TYPE_CHECKING:
    from app.models.group import Group


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    group_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    # MOD-09: IANA tz default Europe/Rome — used for DST-aware notifications + date math
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Rome", nullable=False)
    created_at: Mapped[TimestampTZ]

    group: Mapped[Group | None] = relationship(back_populates="users")
