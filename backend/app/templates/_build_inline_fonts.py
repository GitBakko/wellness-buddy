"""One-off helper: emit base64 strings for woff2 embedding in shopping_list.html.

Run once during Plan 02-06 setup; output goes into the template's @font-face blocks.
Re-run only when the woff2 binaries are replaced.

Usage:
    cd backend
    .venv/Scripts/python.exe -m app.templates._build_inline_fonts > /tmp/font-fragments.txt

The fragments emitted here are pasted verbatim into ``shopping_list.html``.
This intentionally is NOT executed at request time — base64 expansion happens
once and is committed into the template source so PDF generation has zero
runtime file-system dependency.
"""

from __future__ import annotations

import base64
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"

EXPECTED_FONTS = [
    ("plus-jakarta-sans-variable.woff2", "Plus Jakarta Sans", "400 800", "normal"),
    ("geist-mono-variable.woff2", "Geist Mono", "400 600", "normal"),
    ("instrument-serif-italic.woff2", "Instrument Serif", "400", "italic"),
]


def main() -> None:
    # CLI helper — print to stdout is intentional (developer pipes into a file).
    for filename, family, weight, style in EXPECTED_FONTS:
        path = FONT_DIR / filename
        if not path.exists():
            print(f"WARN: missing {filename} — copy into backend/app/static/fonts/")  # noqa: T201
            continue
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        print(f"--- {filename} ({len(encoded)} bytes base64) ---")  # noqa: T201
        print("@font-face {")  # noqa: T201
        print(f'  font-family: "{family}";')  # noqa: T201
        print(f'  src: url(data:font/woff2;base64,{encoded}) format("woff2");')  # noqa: T201
        print(f"  font-weight: {weight};")  # noqa: T201
        print(f"  font-style: {style};")  # noqa: T201
        print("  font-display: block;")  # noqa: T201
        print("}")  # noqa: T201
        print()  # noqa: T201


if __name__ == "__main__":
    main()
