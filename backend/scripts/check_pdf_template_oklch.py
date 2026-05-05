"""CI gate: ensure shopping_list.html OKLCH coords match frontend/src/styles/theme.css.

D-12 contract: PDF brand template MUST mirror frontend OKLCH coords; drift impossible.
Run in CI before merge — exit 1 on mismatch. Plan 02-06 ships the gate.

Why a separate script (not inline in pytest)? The integration test suite imports the
script via importlib so the same logic enforces the contract in both ``pytest`` runs
and CI ``python backend/scripts/check_pdf_template_oklch.py``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Canonical OKLCH coords sourced from frontend/src/styles/theme.css. Adding/removing
# entries requires updating the template and this script in lockstep — that is the
# contract. Drift fails the build.
REQUIRED_OKLCH: dict[str, str] = {
    "--color-text": "22% 0.015 240",
    "--color-neutral-700": "38% 0.015 240",
    "--color-neutral-600": "50% 0.015 240",
    "--color-neutral-800": "28% 0.015 240",
    "--color-leaf-700": "48% 0.13 150",
    "--color-border": "89% 0.012 85",
}


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    template = repo_root / "backend" / "app" / "templates" / "shopping_list.html"
    theme_css = repo_root / "frontend" / "src" / "styles" / "theme.css"

    if not template.exists():
        print(f"FAIL: template missing at {template}", file=sys.stderr)
        return 1
    if not theme_css.exists():
        print(f"FAIL: theme.css missing at {theme_css}", file=sys.stderr)
        return 1

    template_body = template.read_text(encoding="utf-8")
    theme_body = theme_css.read_text(encoding="utf-8")

    missing_in_template: list[str] = []
    missing_in_theme: list[str] = []

    for name, coords in REQUIRED_OKLCH.items():
        # Template carries the coord literally inside an ``oklch(...)`` function call.
        pattern_template = re.escape(f"oklch({coords})")
        if not re.search(pattern_template, template_body):
            missing_in_template.append(f"{name} → expected oklch({coords})")

        # theme.css declares the coord on its CSS variable line. We accept either
        # exact ``oklch(<coords>)`` form to confirm the source-of-truth coords.
        pattern_theme = re.escape(name) + r"\s*:\s*" + re.escape(f"oklch({coords})")
        if not re.search(pattern_theme, theme_body):
            missing_in_theme.append(f"{name} → expected oklch({coords})")

    if missing_in_template or missing_in_theme:
        print(
            "FAIL: OKLCH drift detected — shopping_list.html / theme.css out of sync",
            file=sys.stderr,
        )
        for m in missing_in_template:
            print(f"  template: {m}", file=sys.stderr)
        for m in missing_in_theme:
            print(f"  theme.css: {m}", file=sys.stderr)
        return 1

    n = len(REQUIRED_OKLCH)
    print(f"OK: {n}/{n} OKLCH coords match theme.css canonical values")
    return 0


if __name__ == "__main__":
    sys.exit(main())
