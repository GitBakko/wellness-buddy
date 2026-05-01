"""AIProvider ABC. Source: AI-01, RESEARCH Pattern 11."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base class for all AI providers (Sprint 1: NullProvider only)."""

    @abstractmethod
    async def generate_meal_suggestion(self, **kwargs: object) -> str: ...

    @abstractmethod
    async def analyze_week_progress(self, **kwargs: object) -> str: ...

    @abstractmethod
    async def generate_shopping_tips(self, **kwargs: object) -> str: ...

    @abstractmethod
    async def chat(self, **kwargs: object) -> str: ...

    @property
    @abstractmethod
    def is_available(self) -> bool: ...
