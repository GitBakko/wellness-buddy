"""Unit tests for PdfExporter factory + ABC contract (Plan 02-01, DEP-06).

Verifies:
- ABC contract — `PdfExporter()` cannot be instantiated (abstractmethod enforcement)
- Factory returns WeasyPrintExporter when settings.PDF_BACKEND == 'weasyprint' (default, D-11)
- Factory returns ReportLabExporter when settings.PDF_BACKEND == 'reportlab' (D-14 fallback)
- Unknown backend value falls through to WeasyPrint (forgiving — never crashes startup, T-02-01-05)
- ReportLab smoke renders a minimal payload to non-empty PDF bytes
  (test runs in env without GTK3 → verifies fallback path is intact independent of WeasyPrint).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.pdf_export import (
    PdfExporter,
    ReportLabExporter,
    WeasyPrintExporter,
    get_pdf_exporter,
)


def test_pdf_exporter_is_abstract() -> None:
    """Cannot instantiate the ABC — render_shopping_list is @abstractmethod."""
    with pytest.raises(TypeError):
        PdfExporter()  # type: ignore[abstract]


def test_factory_returns_weasyprint_by_default() -> None:
    """Default settings.PDF_BACKEND == 'weasyprint' returns WeasyPrintExporter."""
    with patch("app.services.pdf_export.settings") as mock_settings:
        mock_settings.PDF_BACKEND = "weasyprint"
        exporter = get_pdf_exporter()
        assert isinstance(exporter, WeasyPrintExporter)


def test_factory_returns_reportlab_when_env_says_so() -> None:
    """settings.PDF_BACKEND == 'reportlab' returns ReportLabExporter."""
    with patch("app.services.pdf_export.settings") as mock_settings:
        mock_settings.PDF_BACKEND = "reportlab"
        exporter = get_pdf_exporter()
        assert isinstance(exporter, ReportLabExporter)


def test_factory_unknown_backend_falls_through_to_weasyprint() -> None:
    """Unknown PDF_BACKEND falls through to WeasyPrint (T-02-01-05 — never crashes startup)."""
    with patch("app.services.pdf_export.settings") as mock_settings:
        mock_settings.PDF_BACKEND = "ghostscript"  # unknown
        exporter = get_pdf_exporter()
        assert isinstance(exporter, WeasyPrintExporter)


@pytest.mark.asyncio
async def test_reportlab_smoke_renders_minimal_payload() -> None:
    """ReportLabExporter renders a minimal 1-category 1-item payload to non-empty bytes.

    Test runs in env without GTK3 — verifies fallback path is intact even if WeasyPrint
    cannot load on this host.
    """
    exporter = ReportLabExporter()
    pdf = await exporter.render_shopping_list(
        week_start="2026-05-04",
        week_start_long_it="4 maggio 2026",
        domain="wellness-buddy.epartner.it",
        categories=[
            {
                "name": "Frigo & Freschi",
                "items": [{"name": "Yogurt greco", "quantity_it": "200 g"}],
            },
        ],
    )
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000  # any valid PDF is >1KB
    assert pdf[:4] == b"%PDF"  # PDF magic bytes
