"""Italian shopping category mapper (D-07 — 5 fixed categories).

Lookup ordered by specificity: longer / more specific keywords first so e.g.
``"olio evo"`` lands in ``Condimenti`` instead of being shadowed by a generic
``"olio"`` match. Default category for unknown ingredients is ``"Dispensa"``
per D-07 fallback contract.

The 5 categories are LOCKED (D-07):

    Frigo & Freschi  / Frutta & Verdura  / Dispensa  / Condimenti  / Integratori

``CATEGORY_ORDER`` exposes the canonical render order used by the UI and the
PDF template; it must NEVER be permuted.
"""

from __future__ import annotations

# Order matters — longer keywords first (e.g. "olio evo" must come before
# "olio"). Insertion order is preserved by Python 3.7+ dict literals; lookup
# is a sequential ``in`` scan so the first match wins.
_KEYWORD_TO_CATEGORY: dict[str, str] = {
    # ───── Frigo & Freschi ─────
    "yogurt greco": "Frigo & Freschi",
    "yogurt": "Frigo & Freschi",
    "latte": "Frigo & Freschi",
    "uova": "Frigo & Freschi",
    "uovo": "Frigo & Freschi",
    "salmone": "Frigo & Freschi",
    "tonno fresco": "Frigo & Freschi",
    "pesce bianco": "Frigo & Freschi",
    "pollo": "Frigo & Freschi",
    "tacchino": "Frigo & Freschi",
    "manzo": "Frigo & Freschi",
    "ricotta": "Frigo & Freschi",
    "mozzarella": "Frigo & Freschi",
    "parmigiano": "Frigo & Freschi",
    "feta": "Frigo & Freschi",
    "burro": "Frigo & Freschi",
    "panna": "Frigo & Freschi",
    # ───── Frutta & Verdura ─────
    "frutta secca": "Frutta & Verdura",
    "frutti di bosco": "Frutta & Verdura",
    "mirtilli": "Frutta & Verdura",
    "fragole": "Frutta & Verdura",
    "pomodorini": "Frutta & Verdura",
    "pomodoro": "Frutta & Verdura",
    "zucchine": "Frutta & Verdura",
    "carote": "Frutta & Verdura",
    "carota": "Frutta & Verdura",
    "spinaci": "Frutta & Verdura",
    "insalata": "Frutta & Verdura",
    "lattuga": "Frutta & Verdura",
    "rucola": "Frutta & Verdura",
    "basilico": "Frutta & Verdura",
    "prezzemolo": "Frutta & Verdura",
    "limone": "Frutta & Verdura",
    "mela": "Frutta & Verdura",
    "banana": "Frutta & Verdura",
    "arancia": "Frutta & Verdura",
    "noci": "Frutta & Verdura",
    "mandorle": "Frutta & Verdura",
    "patate": "Frutta & Verdura",
    "patata": "Frutta & Verdura",
    "broccoli": "Frutta & Verdura",
    "fagiolini": "Frutta & Verdura",
    "melanzane": "Frutta & Verdura",
    "peperoni": "Frutta & Verdura",
    "cipolla": "Frutta & Verdura",
    "aglio": "Frutta & Verdura",
    # ───── Dispensa ─────
    "pasta integrale": "Dispensa",
    "pasta": "Dispensa",
    "riso basmati": "Dispensa",
    "riso integrale": "Dispensa",
    "riso": "Dispensa",
    "avena": "Dispensa",
    "fiocchi d'avena": "Dispensa",
    "miele": "Dispensa",
    "farina": "Dispensa",
    "lenticchie": "Dispensa",
    "ceci": "Dispensa",
    "fagioli": "Dispensa",
    "tonno in scatola": "Dispensa",
    "tonno sott'olio": "Dispensa",
    "biscotti": "Dispensa",
    "pane": "Dispensa",
    "crackers": "Dispensa",
    # ───── Condimenti ─────
    # IMPORTANT: longer "olio evo"/"olio extravergine" entries MUST come
    # before bare "olio" so EVO matches Condimenti before any plain "olio"
    # alias would.
    "olio evo": "Condimenti",
    "olio extravergine": "Condimenti",
    "olio di oliva": "Condimenti",
    "olio": "Condimenti",
    "aceto": "Condimenti",
    "sale": "Condimenti",
    "pepe": "Condimenti",
    "salsa di soia": "Condimenti",
    "senape": "Condimenti",
    # ───── Integratori ─────
    "vitamina": "Integratori",
    "magnesio": "Integratori",
    "omega 3": "Integratori",
    "omega-3": "Integratori",
    "creatina": "Integratori",
    "proteine in polvere": "Integratori",
    "whey": "Integratori",
    "bcaa": "Integratori",
    "multivitaminico": "Integratori",
}


def lookup(name: str) -> str:
    """Resolve canonical ingredient name to one of 5 fixed categories.

    Lookup is case-insensitive and whitespace-tolerant. Default ``"Dispensa"``
    when no keyword matches (D-07 fallback) so the shopping list never has an
    ``"Altro"`` / ``"Sconosciuto"`` bucket.
    """
    norm = name.lower().strip()
    for keyword, category in _KEYWORD_TO_CATEGORY.items():
        if keyword in norm:
            return category
    return "Dispensa"


CATEGORY_ORDER: list[str] = [
    "Frigo & Freschi",
    "Frutta & Verdura",
    "Dispensa",
    "Condimenti",
    "Integratori",
]
"""Fixed render order for the shopping list (D-07). Never permute."""
