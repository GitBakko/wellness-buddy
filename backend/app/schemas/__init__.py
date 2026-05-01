"""Pydantic v2 schemas — request/response DTOs.

Phase 1 (Plan 02a) ships base shapes (user, group, plan, common); Plan 02b adds
ai schemas plus minimal placeholders for auth/today/weight/workout/invite.
Plans 03/04/07 own the real strict schemas (StrictModel + extra='forbid').
"""
