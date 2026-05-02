"""Unit tests for variant_service (LWW + visibility default).

Source: WEEK-04, FAM-02, FAM-04, D-17.
"""

from __future__ import annotations

import pytest

from app.models.variant import Visibility
from app.services.variant_service import default_visibility_for


@pytest.mark.parametrize(
    "meal_type,expected",
    [
        ("breakfast", Visibility.PRIVATE),
        ("snack", Visibility.PRIVATE),
        ("lunch", Visibility.GROUP_SHARED),
        ("dinner", Visibility.GROUP_SHARED),
    ],
)
def test_default_visibility(meal_type: str, expected: Visibility) -> None:
    """FAM-02: cene + pranzi default group_shared; colazione + spuntini default private."""
    assert default_visibility_for(meal_type) == expected


def test_default_visibility_unknown_meal_falls_back_private() -> None:
    """Defensive: unknown meal_type defaults to PRIVATE (least-disclosure)."""
    assert default_visibility_for("brunch") == Visibility.PRIVATE
    assert default_visibility_for("") == Visibility.PRIVATE
