"""WeasyPrint Jinja2 template assets (Plan 02-06).

Templates rendered server-side by ``app.services.pdf_export.WeasyPrintExporter``.
The ``shopping_list.html`` template embeds woff2 fonts as base64 data URLs to
guarantee Italian accent rendering on iPhone Safari + Mail.app preview without
relying on OS-installed fonts (D-13).
"""
