"""Integration tests for /api/auth/* — Plan 01-03 (auth system).

Coverage matrix per Plan 03 <behavior>:
  - login (success + invalid creds + AUTH-12 envelope)
  - refresh (rotation + 10s grace idempotent + reuse outside grace revokes family)
  - logout (revokes family server-side)
  - /me (valid token + missing token envelope)
  - validation errors return AUTH-12 envelope

Source: AUTH-01..AUTH-12, RESEARCH Pattern 9, PITFALLS#4, V13 (login enumeration mitigation).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.refresh import RefreshToken
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Seed a known user with a known password (cleaned up via session rollback)."""
    user = User(
        id=uuid4(),
        email="user@test.example.com",
        username="user1",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Seed an admin user for /invite tests."""
    user = User(
        id=uuid4(),
        email="admin@test.example.com",
        username="admin",
        hashed_password=hash_password("Admin1234!"),
        role="admin",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


# ──────────────────────────────────────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────────────────────────────────────


async def test_login_success_returns_access_and_sets_refresh_cookie(
    async_client: AsyncClient, test_user: User
) -> None:
    r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body and isinstance(body["access_token"], str)
    assert body["token_type"] == "bearer"
    # Cookie attributes
    set_cookie = r.headers.get("set-cookie", "")
    assert "wb_refresh=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "lax" in set_cookie.lower()
    assert "Path=/api/auth" in set_cookie


async def test_login_invalid_creds_returns_envelope(
    async_client: AsyncClient, test_user: User
) -> None:
    r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "WRONG"},
    )
    assert r.status_code == 401
    body = r.json()
    assert body == {
        "detail": "Email o password non corretti. Riprova.",
        "code": "invalid_credentials",
    }


async def test_login_unknown_email_same_envelope(async_client: AsyncClient) -> None:
    """V13: identical envelope for unknown email vs wrong password (no enumeration)."""
    r = await async_client.post(
        "/api/auth/login",
        json={"email": "nope@test.example.com", "password": "whatever"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "invalid_credentials"


async def test_login_validation_error_envelope(async_client: AsyncClient) -> None:
    r = await async_client.post(
        "/api/auth/login",
        json={"email": "not-an-email", "password": ""},
    )
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body and "code" in body
    assert body["code"] == "validation_error"


# ──────────────────────────────────────────────────────────────────────────────
# Refresh
# ──────────────────────────────────────────────────────────────────────────────


async def test_refresh_rotation_issues_new_pair(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    cookie = login_r.cookies.get("wb_refresh")
    assert cookie

    r = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r.status_code == 200, r.text
    new_cookie = r.cookies.get("wb_refresh")
    assert new_cookie is not None
    assert new_cookie != cookie  # rotation issued a different token


async def test_refresh_grace_window_returns_cached_pair(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    """PITFALLS#4: reusing the same old refresh token within 10s returns cached new pair."""
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    cookie = login_r.cookies.get("wb_refresh")

    r1 = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r1.status_code == 200
    access1 = r1.json()["access_token"]

    # Re-use OLD cookie within grace window — must return cached pair (idempotent)
    r2 = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r2.status_code == 200
    access2 = r2.json()["access_token"]
    assert access1 == access2  # cached path returned same token


async def test_refresh_reuse_outside_grace_revokes_family(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    """Reuse beyond 10s grace window → 401 + family revoked."""
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    cookie = login_r.cookies.get("wb_refresh")

    r1 = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r1.status_code == 200

    # Backdate the original token's replaced_at to push it OUTSIDE the 10s grace window
    # Find the row corresponding to the original refresh (revoked=true after rotation)
    rows = (
        await db_session.scalars(
            select(RefreshToken).where(RefreshToken.user_id == test_user.id)
        )
    ).all()
    revoked_row = next((row for row in rows if row.revoked), None)
    assert revoked_row is not None
    family_id_value = revoked_row.family_id  # capture before expiration
    revoked_row.replaced_at = datetime.now(UTC) - timedelta(seconds=30)
    await db_session.commit()

    r2 = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r2.status_code == 401
    body = r2.json()
    assert body["code"] == "family_revoked"

    # All tokens in the family should be revoked now — re-query fresh
    family_rows = (
        await db_session.scalars(
            select(RefreshToken).where(RefreshToken.family_id == family_id_value)
        )
    ).all()
    # Refresh state from DB explicitly via session.refresh per row
    for row in family_rows:
        await db_session.refresh(row)
    assert all(row.revoked for row in family_rows)


async def test_refresh_no_cookie_returns_envelope(async_client: AsyncClient) -> None:
    r = await async_client.post("/api/auth/refresh")
    assert r.status_code == 401
    body = r.json()
    assert "code" in body


# ──────────────────────────────────────────────────────────────────────────────
# Logout
# ──────────────────────────────────────────────────────────────────────────────


async def test_logout_revokes_family(
    async_client: AsyncClient, test_user: User
) -> None:
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    cookie = login_r.cookies.get("wb_refresh")

    r = await async_client.post("/api/auth/logout", cookies={"wb_refresh": cookie})
    assert r.status_code == 204

    # Subsequent refresh should fail
    r2 = await async_client.post("/api/auth/refresh", cookies={"wb_refresh": cookie})
    assert r2.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# /me
# ──────────────────────────────────────────────────────────────────────────────


async def test_me_returns_profile(
    async_client: AsyncClient, test_user: User
) -> None:
    login_r = await async_client.post(
        "/api/auth/login",
        json={"email": "user@test.example.com", "password": "Password123!"},
    )
    access = login_r.json()["access_token"]

    r = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "user@test.example.com"
    assert body["username"] == "user1"
    assert body["role"] == "user"
    assert body["timezone"] == "Europe/Rome"
    assert "id" in body
    assert "group_id" in body  # nullable but always present


async def test_me_without_token_returns_envelope(async_client: AsyncClient) -> None:
    r = await async_client.get("/api/auth/me")
    assert r.status_code == 401
    body = r.json()
    assert "detail" in body and "code" in body


async def test_me_with_garbage_token_returns_envelope(async_client: AsyncClient) -> None:
    r = await async_client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert r.status_code == 401
    assert r.json()["code"] in {"expired", "invalid_token", "no_token"}
