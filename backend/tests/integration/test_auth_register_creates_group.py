"""Test that the register flow auto-creates a personal household group (PITFALL #16).

Plan 02-07 patches ``auth_service.consume_invite_and_register`` to call
``ensure_personal_group`` immediately after the user is flushed. Without this
patch, every user registered POST-Phase-2-deploy would have ``group_id=NULL``
indefinitely (the Alembic 0002 migration only backfills users that existed
BEFORE deploy).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.invite import InviteToken
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


@pytest_asyncio.fixture
async def admin_with_invite(db_session: AsyncSession) -> dict:
    """Admin + valid invite token. Returns dict with `token` ready for /api/auth/register."""
    admin = User(
        id=uuid4(),
        email="register-admin@test.example.com",
        username="register_admin",
        hashed_password=hash_password("Admin1234!"),
        role="admin",
        timezone="Europe/Rome",
    )
    db_session.add(admin)
    await db_session.flush()

    invite = InviteToken(
        token="register-test-token-1234567890abcdef",
        created_by=admin.id,
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db_session.add(invite)
    await db_session.commit()
    return {"admin": admin, "token": invite.token}


async def test_register_creates_personal_group(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_with_invite: dict,
) -> None:
    """New user via POST /api/auth/register must end up linked to a household group."""
    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": admin_with_invite["token"],
            "email": "newuser@test.example.com",
            "username": "newuser",
            "password": "Password123!",
        },
    )
    assert r.status_code == 201, r.text

    rows = (
        await db_session.execute(
            sa.text(
                "SELECT u.username, g.name "
                "FROM users u JOIN groups g ON u.group_id = g.id "
                "WHERE u.username = 'newuser'"
            )
        )
    ).all()
    assert len(rows) == 1, f"expected exactly 1 newuser+group join, got {rows}"
    assert rows[0][1] == "newuser · household", rows[0][1]


async def test_register_group_id_not_null_on_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_with_invite: dict,
) -> None:
    """The user row itself must carry a non-null group_id (FK linked) post-register."""
    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": admin_with_invite["token"],
            "email": "linked@test.example.com",
            "username": "linkeduser",
            "password": "Password123!",
        },
    )
    assert r.status_code == 201, r.text

    user = (await db_session.scalars(sa.select(User).where(User.username == "linkeduser"))).first()
    assert user is not None
    assert user.group_id is not None, "PITFALL #16 mitigation missing — group_id is NULL"
