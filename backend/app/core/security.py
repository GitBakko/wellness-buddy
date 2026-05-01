"""JWT encode/decode + password hash primitives.

Source: RESEARCH Pattern 9, AUTH-04..AUTH-05.
Plan 03 extends with refresh rotation + family revocation + 10s grace window.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(p: str) -> str:
    """Bcrypt-hash a plaintext password (cost 12)."""
    return pwd_context.hash(p)


def verify_password(p: str, h: str) -> bool:
    """Constant-time verify a plaintext password against a stored hash."""
    return pwd_context.verify(p, h)


def create_access_token(user_id: UUID, expires_in: timedelta | None = None) -> str:
    """Issue a short-lived (default 15min) access JWT bound to a user UUID."""
    expires_in = expires_in or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + expires_in,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    family_id: UUID,
    jti: UUID,
    expires_in: timedelta | None = None,
) -> str:
    """Issue a refresh JWT carrying family/jti for rotation + reuse detection."""
    expires_in = expires_in or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "family": str(family_id),
        "jti": str(jti),
        "iat": now,
        "exp": now + expires_in,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode + verify a JWT. Raises `jose.JWTError` on tamper/expiry/sig-mismatch."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
