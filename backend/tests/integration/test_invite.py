"""Integration tests for /api/auth/invite + /api/auth/register — Plan 01-03 (auth).

Coverage matrix per Plan 03 <behavior>:
  - invite create requires admin role (403 for non-admin)
  - admin invite returns token + 24h expires_at
  - register with valid token creates user + auto-login
  - register with expired/revoked/reused token rejected with AUTH-12 envelope codes

Source: AUTH-09, AUTH-10, D-17, V13.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.invite import InviteToken
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="user2@test.local",
        username="user2",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="admin2@test.local",
        username="admin2",
        hashed_password=hash_password("Admin1234!"),
        role="admin",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


# ──────────────────────────────────────────────────────────────────────────────
# Invite create
# ──────────────────────────────────────────────────────────────────────────────


async def test_invite_create_admin_only_403_for_non_admin(
    async_client: AsyncClient, test_user: User
) -> None:
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user2@test.local", "password": "Password123!"},
    )
    access = login_r.json()["access_token"]
    r = await async_client.post(
        "/api/auth/invite", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 403
    assert r.json()["code"] == "forbidden"


async def test_invite_create_admin_succeeds(
    async_client: AsyncClient, admin_user: User
) -> None:
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "admin2@test.local", "password": "Admin1234!"},
    )
    access = login_r.json()["access_token"]
    r = await async_client.post(
        "/api/auth/invite", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "token" in body and len(body["token"]) >= 32
    assert "expires_at" in body
    expires_at = datetime.fromisoformat(body["expires_at"])
    delta = expires_at - datetime.now(UTC)
    assert timedelta(hours=23) < delta <= timedelta(hours=24, minutes=1)


# ──────────────────────────────────────────────────────────────────────────────
# Register flow
# ──────────────────────────────────────────────────────────────────────────────


async def test_register_with_valid_token_creates_user_and_logs_in(
    async_client: AsyncClient, db_session: AsyncSession, admin_user: User
) -> None:
    # Admin generates an invite
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "admin2@test.local", "password": "Admin1234!"},
    )
    access = login_r.json()["access_token"]
    invite_r = await async_client.post(
        "/api/auth/invite", headers={"Authorization": f"Bearer {access}"}
    )
    token = invite_r.json()["token"]

    # New user registers using token
    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": token,
            "email": "new@test.local",
            "username": "newuser",
            "password": "NewPwd123!",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert "access_token" in body
    set_cookie = r.headers.get("set-cookie", "")
    assert "wb_refresh=" in set_cookie


async def test_register_expired_token(
    async_client: AsyncClient, db_session: AsyncSession, admin_user: User
) -> None:
    invite = InviteToken(
        token="expired-token-1234567890abcdefghij",
        created_by=admin_user.id,
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    db_session.add(invite)
    await db_session.commit()

    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": invite.token,
            "email": "expired@test.local",
            "username": "expireduser",
            "password": "Password123!",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "token_expired"


async def test_register_revoked_token(
    async_client: AsyncClient, db_session: AsyncSession, admin_user: User
) -> None:
    invite = InviteToken(
        token="revoked-token-1234567890abcdefghij",
        created_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(hours=24),
        revoked=True,
    )
    db_session.add(invite)
    await db_session.commit()

    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": invite.token,
            "email": "revoked@test.local",
            "username": "revokeduser",
            "password": "Password123!",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "token_invalid"


async def test_register_reuse_blocked(
    async_client: AsyncClient, db_session: AsyncSession, admin_user: User
) -> None:
    """Once an invite is used, second use must fail."""
    used_user_id = uuid4()
    used_user = User(
        id=used_user_id,
        email="used@test.local",
        username="useduser",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(used_user)

    invite = InviteToken(
        token="used-token-1234567890abcdefghij1234",
        created_by=admin_user.id,
        used_by=used_user_id,
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db_session.add(invite)
    await db_session.commit()

    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": invite.token,
            "email": "another@test.local",
            "username": "anotheruser",
            "password": "Password123!",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "token_invalid"


async def test_register_unknown_token(async_client: AsyncClient) -> None:
    r = await async_client.post(
        "/api/auth/register",
        json={
            "token": "completely-bogus-token-not-in-db-12345",
            "email": "ghost@test.local",
            "username": "ghost",
            "password": "Password123!",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "token_invalid"
