"""Auth service: login, logout, rotate refresh (with 10s idempotent grace + family
revocation), invite generation, register-with-invite.

Source: AUTH-01..AUTH-12, RESEARCH Pattern 9, PITFALLS#4 (iPhone resume race),
V13 (login enumeration mitigation).

Key invariants:
  * Access JWT lifespan: 15 minutes (config-driven)
  * Refresh JWT lifespan: 7 days (config-driven)
  * Rotation: every successful refresh issues a new pair AND revokes the old jti
  * Grace window: 10s after `replaced_at`, the same old refresh returns the
    cached new pair (idempotent — handles iPhone resume race)
  * Reuse outside grace: revokes the entire family_id (defense against stolen tokens)
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.invite import InviteToken
from app.models.refresh import RefreshToken
from app.models.user import User
from app.services.audit_service import write_audit
from app.services.group_service import ensure_personal_group

# PITFALLS#4 — within this window after rotation, replaying the OLD refresh
# returns the cached new pair instead of triggering family revocation.
GRACE_WINDOW = timedelta(seconds=10)

# AUTH-09 — invite tokens valid 24h
INVITE_EXPIRY = timedelta(hours=24)

# Italian copy lifted into backend errors per AUTH-12 envelope contract.
_MSG_INVALID_CREDS = "Email o password non corretti. Riprova."
_MSG_SESSION_EXPIRED = "Sessione scaduta dopo 7 giorni di inattività. Accedi di nuovo."
_MSG_TOKEN_INVALID = "Questo invito non è valido. Chiedi all'amministratore un nuovo link."  # noqa: S105
_MSG_TOKEN_EXPIRED = "Questo invito è scaduto. Chiedi all'amministratore un nuovo link."  # noqa: S105
_MSG_FAMILY_REVOKED = "Sessione invalidata per sicurezza. Accedi di nuovo."
_MSG_EMAIL_TAKEN = "Email già registrata."


# ──────────────────────────────────────────────────────────────────────────────
# Login + token issuance
# ──────────────────────────────────────────────────────────────────────────────


async def authenticate(session: AsyncSession, email: str, password: str) -> User:
    """Look up the user by email and verify password.

    V13: identical envelope returned for unknown email and wrong password — no enumeration.
    """
    user = (await session.scalars(select(User).where(User.email == email.lower()))).first()
    if not user or not verify_password(password, user.hashed_password):
        raise AppException(401, _MSG_INVALID_CREDS, "invalid_credentials")
    return user


async def issue_token_pair(session: AsyncSession, user: User) -> tuple[str, str, datetime]:
    """Issue a fresh access+refresh pair anchored to a brand-new family_id.

    Returns (access, refresh, refresh_expires_at). Caller is responsible for shaping
    the cookie + JSON response.
    """
    family_id = uuid4()
    jti = uuid4()
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id, family_id, jti)
    session.add(
        RefreshToken(
            jti=jti,
            family_id=family_id,
            user_id=user.id,
            issued_at=now,
            expires_at=expires_at,
        )
    )
    await session.commit()
    return access, refresh, expires_at


# ──────────────────────────────────────────────────────────────────────────────
# Refresh rotation + grace window + family revocation
# ──────────────────────────────────────────────────────────────────────────────


async def rotate_refresh(session: AsyncSession, refresh_jwt: str) -> tuple[str, str, datetime]:
    """Rotate a refresh token.

    Outcomes:
      * Token valid + not yet rotated: issue new pair, mark old revoked + cache new pair.
      * Token already rotated within GRACE_WINDOW: return cached pair (idempotent).
      * Token already rotated outside GRACE_WINDOW: revoke entire family + raise.
      * Token unknown / malformed / expired: raise expired/invalid_token.
    """
    try:
        payload = decode_token(refresh_jwt)
    except Exception as e:
        raise AppException(401, _MSG_SESSION_EXPIRED, "expired") from e

    if payload.get("type") != "refresh":
        raise AppException(401, "Token non valido", "invalid_token")

    user_id = UUID(payload["sub"])
    family_id = UUID(payload["family"])
    jti = UUID(payload["jti"])

    row = (await session.scalars(select(RefreshToken).where(RefreshToken.jti == jti))).first()
    if not row:
        raise AppException(401, _MSG_SESSION_EXPIRED, "expired")

    if row.revoked:
        # Reuse path
        now = datetime.now(UTC)
        if (
            row.replaced_at is not None
            and (now - row.replaced_at) < GRACE_WINDOW
            and row.cached_access
            and row.cached_refresh
        ):
            # PITFALLS#4 — idempotent grace: return cached pair
            return row.cached_access, row.cached_refresh, row.expires_at
        # Real reuse → revoke entire family (defense in depth)
        await session.execute(
            update(RefreshToken).where(RefreshToken.family_id == family_id).values(revoked=True)
        )
        await session.commit()
        raise AppException(401, _MSG_FAMILY_REVOKED, "family_revoked")

    # Issue new pair, attach to same family
    new_jti = uuid4()
    now = datetime.now(UTC)
    new_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id, family_id, new_jti)

    session.add(
        RefreshToken(
            jti=new_jti,
            family_id=family_id,
            user_id=user_id,
            issued_at=now,
            expires_at=new_expires,
        )
    )
    # Mark old revoked + cache new pair so concurrent retries within grace stay idempotent
    row.revoked = True
    row.replaced_at = now
    row.cached_access = new_access
    row.cached_refresh = new_refresh
    await session.commit()
    return new_access, new_refresh, new_expires


async def revoke_family(session: AsyncSession, refresh_jwt: str) -> None:
    """Revoke every refresh row sharing the family_id encoded in this JWT.

    Logout is forgiving: malformed/expired tokens silently succeed (idempotent client UX).
    """
    try:
        payload = decode_token(refresh_jwt)
        family_id = UUID(payload["family"])
    except Exception:
        return
    await session.execute(
        update(RefreshToken).where(RefreshToken.family_id == family_id).values(revoked=True)
    )
    await session.commit()


# ──────────────────────────────────────────────────────────────────────────────
# Invite generation + register
# ──────────────────────────────────────────────────────────────────────────────


def _generate_invite_token() -> str:
    """256-bit URL-safe random token (~43 chars)."""
    return secrets.token_urlsafe(32)


async def create_invite(session: AsyncSession, *, created_by: UUID) -> InviteToken:
    """Admin-only — generate a single-use 24h invite token. Audit-logged."""
    token = _generate_invite_token()
    expires_at = datetime.now(UTC) + INVITE_EXPIRY
    invite = InviteToken(token=token, created_by=created_by, expires_at=expires_at)
    session.add(invite)
    await session.flush()  # populate invite.id for audit row
    await write_audit(
        session,
        actor_id=created_by,
        action="invite_create",
        target_type="invite_token",
        target_id=invite.id,
        payload={"expires_at": expires_at.isoformat()},
    )
    await session.commit()
    await session.refresh(invite)
    return invite


async def consume_invite_and_register(
    session: AsyncSession,
    *,
    token: str,
    email: str,
    username: str,
    password: str,
) -> User:
    """Validate an invite token, create the new user, mark invite consumed."""
    invite = (await session.scalars(select(InviteToken).where(InviteToken.token == token))).first()
    if not invite:
        raise AppException(400, _MSG_TOKEN_INVALID, "token_invalid")
    if invite.revoked or invite.used_by is not None:
        raise AppException(400, _MSG_TOKEN_INVALID, "token_invalid")
    if invite.expires_at < datetime.now(UTC):
        raise AppException(400, _MSG_TOKEN_EXPIRED, "token_expired")

    # Email/username uniqueness (DB constraint will catch races, but pre-check for nicer error)
    existing = (await session.scalars(select(User).where(User.email == email.lower()))).first()
    if existing:
        raise AppException(400, _MSG_EMAIL_TAKEN, "email_taken")

    user = User(
        email=email.lower(),
        username=username,
        hashed_password=hash_password(password),
        role="user",
        timezone="Europe/Rome",
    )
    session.add(user)
    await session.flush()  # populate user.id
    # PITFALL #16 mitigation — every new user gets a personal household group at
    # registration time so users.group_id is never NULL post-Phase-2 deploy.
    await ensure_personal_group(session, user)
    invite.used_by = user.id
    await write_audit(
        session,
        actor_id=user.id,
        action="user_register",
        target_type="user",
        target_id=user.id,
        payload={"invite_id": str(invite.id)},
    )
    await session.commit()
    await session.refresh(user)
    return user
