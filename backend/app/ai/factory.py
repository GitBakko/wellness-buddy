"""AI provider factory. Source: D-31, D-32.

`build_provider()` reads `settings.AI_PROVIDER` and returns the matching AIProvider
implementation. Sprint 1 only supports `'null'` -> NullProvider; Sprint 5 will add
`'ollama'`, `'openai'`, `'anthropic'`. Unknown values raise ValueError at boot —
defense against typos / mis-deployed envs.
"""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.null_provider import NullProvider
from app.core.config import settings


def build_provider() -> AIProvider:
    """Return the AIProvider implementation matching settings.AI_PROVIDER."""
    kind = settings.AI_PROVIDER
    if kind == "null":
        return NullProvider()
    # Phase 5 adds: ollama / openai / anthropic
    raise ValueError(f"Unknown AI_PROVIDER={kind!r}; only 'null' supported in Phase 1")
