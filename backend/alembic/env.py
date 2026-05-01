"""Alembic async migration env.

Source: D-30, RESEARCH.md Pattern 8.

This module references `app.core.config` and `app.models.base.Base` which are
created by Plan 02a (backend-core). Until that plan lands, running Alembic
commands will fail with ImportError — that is expected and confirms ordering.
Plan 01 ships the scaffolding only.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings  # type: ignore[import-not-found]  # provided by Plan 02a
from app.models.base import Base  # type: ignore[import-not-found]  # provided by Plan 02a
import app.models  # type: ignore[import-not-found]  # noqa: F401 — register all models

config = context.config
# alembic.ini uses configparser interpolation; '%' in DATABASE_URL (e.g. URL-encoded chars
# like %40 for '@') triggers InterpolationSyntaxError unless escaped as '%%'.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
