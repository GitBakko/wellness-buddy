"""Auth endpoints — Plan 03 real impl (replaces 02b's 501 stubs).

Source: AUTH-01..AUTH-12, RESEARCH Pattern 9, UI-SPEC §7.2 italian copy contract.

Endpoints:
  * POST /api/auth/login    — email+password → access JWT + Set-Cookie wb_refresh
  * POST /api/auth/refresh  — rotate via wb_refresh cookie → new access + new wb_refresh
  * POST /api/auth/logout   — revoke family server-side, clear cookie
  * GET  /api/auth/me       — return current user profile (Bearer access JWT)
  * POST /api/auth/invite   — admin-only, generate 24h single-use invite token
  * POST /api/auth/register — invite-gated signup → auto-login

Cookie shape (AUTH-04, V14):
  Name:     wb_refresh
  Path:     /api/auth     (browser sends only on auth endpoints)
  HttpOnly: true          (JS can't read — XSS isolation)
  Secure:   true          (TLS-only — IIS reverse proxy terminates HTTPS)
  SameSite: Lax           (sufficient against CSRF for top-level POST)
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.schemas.invite import InviteCreateResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "wb_refresh"
REFRESH_COOKIE_PATH = "/api/auth"

_MSG_SESSION_EXPIRED = "Sessione scaduta dopo 7 giorni di inattività. Accedi di nuovo."


def _set_refresh_cookie(response: Response, refresh: str, expires_at: datetime) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
        expires=expires_at,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    user = await auth_service.authenticate(session, body.email, body.password)
    access, refresh, expires_at = await auth_service.issue_token_pair(session, user)
    response = JSONResponse(content=TokenResponse(access_token=access).model_dump())
    _set_refresh_cookie(response, refresh, expires_at)
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if not cookie:
        raise AppException(401, _MSG_SESSION_EXPIRED, "no_refresh_cookie")
    access, new_refresh, expires_at = await auth_service.rotate_refresh(session, cookie)
    response = JSONResponse(content=TokenResponse(access_token=access).model_dump())
    _set_refresh_cookie(response, new_refresh, expires_at)
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request, session: AsyncSession = Depends(get_session)
) -> Response:
    cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if cookie:
        await auth_service.revoke_family(session, cookie)
    response = Response(status_code=204)
    _clear_refresh_cookie(response)
    return response


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
        group_id=str(user.group_id) if user.group_id else None,
        timezone=user.timezone,
    )


@router.post("/invite", response_model=InviteCreateResponse)
async def create_invite(
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> InviteCreateResponse:
    invite = await auth_service.create_invite(session, created_by=admin.id)
    return InviteCreateResponse(
        token=invite.token, expires_at=invite.expires_at.isoformat()
    )


@router.post("/register", status_code=201, response_model=TokenResponse)
async def register(
    body: RegisterRequest, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    user = await auth_service.consume_invite_and_register(
        session,
        token=body.token,
        email=body.email,
        username=body.username,
        password=body.password,
    )
    access, refresh, expires_at = await auth_service.issue_token_pair(session, user)
    response = JSONResponse(
        status_code=201, content=TokenResponse(access_token=access).model_dump()
    )
    _set_refresh_cookie(response, refresh, expires_at)
    return response
