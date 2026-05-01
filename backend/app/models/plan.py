"""NutritionPlan model (MOD-03, MOD-10, V11).

`raw_md` stores the user-uploaded markdown verbatim. `parsed_json` stores the structured
output from the tolerant MD parser (Plan 04). `is_active` marks the currently in-use plan;
the partial unique index enforces "only one active plan per user" at the DB layer (V11).
"""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_md: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    uploaded_at: Mapped[TimestampTZ]

    __table_args__ = (
        # V11: at most ONE active plan per user — partial unique index.
        Index(
            "ix_nutrition_plans_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=is_active.is_(True),
        ),
    )
