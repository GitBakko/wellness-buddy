"""Model registry. Import order matters for Alembic autogenerate.

Importing this package guarantees `Base.metadata` knows about every table — required by
both runtime (`get_session()`) and the Alembic env.py (`target_metadata = Base.metadata`).
"""

from app.models.audit import AuditLog
from app.models.base import Base
from app.models.group import Group
from app.models.invite import InviteToken
from app.models.plan import NutritionPlan
from app.models.refresh import RefreshToken
from app.models.shopping import ShoppingListState
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant
from app.models.weight import WeightLog
from app.models.workout import WorkoutLog

__all__ = [
    "AuditLog",
    "Base",
    "Group",
    "InviteToken",
    "NutritionPlan",
    "RefreshToken",
    "ShoppingListState",
    "User",
    "Visibility",
    "WeeklyPlanVariant",
    "WeightLog",
    "WorkoutLog",
]
