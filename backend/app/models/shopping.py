"""ShoppingListState model (MOD-07).

Phase 2 generates the shopping list; Phase 1 ships the table only so the migration
graph is stable. `items_json` stores the serialized checklist (per-item checked state).
`version` enables LWW conflict resolution.
"""

from __future__ import annotations

from datetime import date as DateType
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class ShoppingListState(Base):
    __tablename__ = "shopping_list_state"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    week_start: Mapped[DateType] = mapped_column(Date, nullable=False)
    items_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[TimestampTZ]
    updated_at: Mapped[TimestampTZ]

    __table_args__ = (UniqueConstraint("user_id", "week_start", name="uq_shopping_user_week"),)
