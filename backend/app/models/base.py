"""DeclarativeBase + TIMESTAMPTZ alias.

Source: SQLAlchemy 2.0 docs, MOD-09 (TIMESTAMPTZ + UTC storage).
Every model that needs a timestamp uses `Mapped[TimestampTZ]`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 2 declarative base shared by every Wellness Buddy model."""


# Type alias for TIMESTAMPTZ columns with UTC default.
# Default is a callable so each instance gets its own datetime.now() at insert time.
TimestampTZ = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    ),
]
