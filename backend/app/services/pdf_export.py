"""PDF export ABC + WeasyPrint primary + ReportLab fallback (D-11..D-14, DEP-06).

The `PdfExporter` ABC isolates the rendering backend from `shopping_service`.
Plan 02-01 GTK3 spike outcome → `PDF_BACKEND=weasyprint` (default) or `PDF_BACKEND=reportlab`.

Design notes:
- **Lazy imports** keep test envs without GTK3 healthy. The WeasyPrint HTML import lives
  inside the method body, NOT at module top — so this module imports cleanly even when
  Pango/Cairo DLLs are not installed (e.g. on dev box without MSYS2).
- **Forgiving factory**: unknown `PDF_BACKEND` values fall through to WeasyPrint instead of
  raising at boot. Mitigates T-02-01-05 (env-var tampering DoS) — endpoint surfaces a clear
  5xx if GTK3 is missing, but the app itself never fails to start.
- The `Phase 2 plan 02-05` PDF endpoint wires `Depends(get_pdf_exporter)` to obtain the
  active backend per request without picking the implementation in business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.core.config import settings


class PdfExporter(ABC):
    """Renders a structured shopping list payload to PDF bytes.

    Concrete subclasses: `WeasyPrintExporter` (D-11 primary) and `ReportLabExporter`
    (D-14 fallback). Plan 02-05 will compose payloads from `shopping_service` and stream
    the bytes to the client via `Response(media_type='application/pdf')`.
    """

    @abstractmethod
    async def render_shopping_list(
        self,
        *,
        week_start: str,           # YYYY-MM-DD
        week_start_long_it: str,   # "5 maggio 2026"
        domain: str,               # "wellness-buddy.epartner.it" — footer
        categories: list[dict[str, Any]],  # [{name, items: [{name, quantity_it}]}]
    ) -> bytes:
        """Return PDF bytes. Caller streams to client via Response(media_type='application/pdf')."""


class WeasyPrintExporter(PdfExporter):
    """Primary backend (D-11 lock). Renders Jinja2 template with embedded woff2 fonts.

    Lazy imports prevent test envs without GTK3/Pango from failing at module load.
    Plan 02-05 ships the `shopping_list.html` template + base64 woff2 fonts inline
    (D-13 — guarantees Italian accents render on iPhone Safari/Mail.app without external
    network dependency).
    """

    def __init__(self, template_dir: Path) -> None:
        # Lazy-import Jinja2 too — keeps the import surface defensive even though Jinja2
        # has no native dependency. Mirrors the pattern below for WeasyPrint.
        from jinja2 import Environment, FileSystemLoader  # noqa: PLC0415  (lazy by design)

        self._env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        self._template_dir = template_dir

    async def render_shopping_list(
        self,
        *,
        week_start: str,
        week_start_long_it: str,
        domain: str,
        categories: list[dict[str, Any]],
    ) -> bytes:
        # Lazy import — keeps test envs without GTK3 healthy. If Pango/Cairo DLLs are
        # missing the OSError surfaces here (caller wraps in 5xx with structured envelope
        # in Plan 02-05); module import + factory dispatch never crash regardless.
        from weasyprint import HTML  # noqa: PLC0415  (lazy by design — see module docstring)

        template = self._env.get_template("shopping_list.html")
        html_str = template.render(
            week_start=week_start,
            week_start_long_it=week_start_long_it,
            domain=domain,
            categories=categories,
        )
        # base_url so any relative paths in the template resolve; with woff2 base64 inline
        # (Plan 02-05 ships fonts inline) this is defensive only.
        # WeasyPrint's `write_pdf()` returns bytes when no `target` is supplied, but its
        # type stubs are not shipped (PLC0415-style ignore on the lazy import) so we cast.
        pdf_bytes: bytes = HTML(string=html_str, base_url=str(self._template_dir)).write_pdf()
        return pdf_bytes


class ReportLabExporter(PdfExporter):
    """Fallback backend (D-14). Activated only if Plan 02-01 spike fails 5xx >2% threshold.

    Pure-Python — no GTK3/Pango dependency, no DLL load surface. Output is a basic A4
    layout (less branded than the WeasyPrint template) but Italian accents render
    correctly via ReportLab's default Latin-1 fonts.
    """

    async def render_shopping_list(
        self,
        *,
        week_start: str,
        week_start_long_it: str,
        domain: str,
        categories: list[dict[str, Any]],
    ) -> bytes:
        # Lazy imports — keeps the optional fallback isolated. ReportLab is in the
        # baseline deps (Plan 02-01) so this only matters for symmetry with WeasyPrint.
        from io import BytesIO  # noqa: PLC0415

        from reportlab.lib.pagesizes import A4  # noqa: PLC0415
        from reportlab.lib.styles import getSampleStyleSheet  # noqa: PLC0415
        from reportlab.platypus import (  # noqa: PLC0415
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )

        buf = BytesIO()
        # 20 mm margins → ReportLab uses points; 1 mm ≈ 2.83 pt.
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            topMargin=20 * 2.83,
            bottomMargin=20 * 2.83,
            leftMargin=20 * 2.83,
            rightMargin=20 * 2.83,
        )
        styles = getSampleStyleSheet()
        flow: list[Any] = [
            Paragraph("<b>Lista spesa</b>", styles["Title"]),
            Paragraph(f"settimana del {week_start_long_it}", styles["Italic"]),
            Spacer(1, 12),
        ]
        for cat in categories:
            flow.append(Paragraph(f"<b>{cat['name']}</b>", styles["Heading2"]))
            for item in cat["items"]:
                flow.append(
                    Paragraph(
                        f"☐  {item['name']} — {item['quantity_it']}",
                        styles["Normal"],
                    )
                )
            flow.append(Spacer(1, 12))
        flow.append(Paragraph(f"Wellness Buddy · {domain}", styles["Italic"]))
        doc.build(flow)
        return buf.getvalue()


def get_pdf_exporter() -> PdfExporter:
    """FastAPI Depends() factory. Returns active backend per env (D-11 spike outcome).

    Forgiving on unknown values — falls through to WeasyPrint primary instead of raising
    at request time. Mitigates T-02-01-05 (env tampering DoS).
    """
    backend = (settings.PDF_BACKEND or "weasyprint").lower()
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    if backend == "reportlab":
        return ReportLabExporter()
    return WeasyPrintExporter(template_dir=template_dir)
