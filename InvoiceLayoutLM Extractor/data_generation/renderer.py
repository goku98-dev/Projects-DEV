"""Renders Invoice models to HTML using Jinja2, then to PDF via Playwright."""

import random
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

from models.invoice import Invoice
from models.number_format import NumberFormat


TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass
class Column:
    """Defines a column in the invoice table."""
    field: str
    label: str
    align: str = "left"
    format: str = "text"


# Mapping from Faker locale to internal language key
_LOCALE_TO_LANGUAGE: dict[str, str] = {
    "en_US": "en",
    "en_GB": "en",
    "de_DE": "de",
    "de_AT": "de",
    "de_CH": "de",
    "fr_FR": "fr",
}

# Label variants per language with realistic synonyms from real invoices
_COLUMN_LABELS_BY_LANGUAGE: dict[str, dict[str, list[str]]] = {
    "en": {
        "position":       ["#", "Pos", "Pos.", "No.", "Item", "Line"],
        "article_number": ["Article No.", "Art. No.", "SKU", "Item No.", "Product No.",
                           "Part No.", "Catalog No."],
        "description":    ["Description", "Item Description", "Product", "Item",
                           "Designation", "Details", "Service / Product"],
        "quantity":       ["Qty", "Quantity", "Qty.", "Units", "Pcs", "Count"],
        "unit_price":     ["Unit Price", "Price", "Rate", "Price/Unit", "Unit Cost", "Each"],
        "tax_rate":       ["Tax %", "Tax", "VAT %", "Tax Rate", "VAT", "GST %"],
        "line_total":     ["Total", "Line Total", "Amount", "Ext. Price", "Net Amount",
                           "Extended"],
    },
    "de": {
        "position":       ["Pos.", "Nr.", "Lfd. Nr.", "Pos", "#"],
        "article_number": ["Artikel-Nr.", "Art.-Nr.", "Artikelnummer", "Bestellnr.",
                           "Produkt-Nr.", "Teilenr."],
        "description":    ["Beschreibung", "Bezeichnung", "Artikel", "Leistung",
                           "Produkt", "Position"],
        "quantity":       ["Menge", "Anzahl", "Stück", "Anz.", "Stk.", "Einheiten"],
        "unit_price":     ["Einzelpreis", "E-Preis", "Preis/Einheit", "EP",
                           "Stückpreis", "Netto-EP"],
        "tax_rate":       ["MwSt. %", "MwSt.", "USt. %", "USt.", "Steuersatz",
                           "MwSt.-Satz"],
        "line_total":     ["Gesamtpreis", "Gesamt", "Betrag", "Summe", "Nettobetrag",
                           "Gesamtbetrag"],
    },
    "fr": {
        "position":       ["N°", "Pos.", "Réf.", "#", "Ligne", "No."],
        "article_number": ["Réf. article", "Code article", "Référence", "N° article",
                           "Code produit", "Réf."],
        "description":    ["Description", "Désignation", "Libellé", "Article",
                           "Prestation", "Produit"],
        "quantity":       ["Quantité", "Qté", "Nombre", "Qté.", "Nb", "Unités"],
        "unit_price":     ["Prix unitaire", "P.U.", "Prix/unité", "Tarif unitaire",
                           "Prix U.", "PU HT"],
        "tax_rate":       ["TVA %", "TVA", "Taux TVA", "% TVA", "Taxe", "Taux"],
        "line_total":     ["Montant HT", "Total HT", "Montant", "Total", "Prix total",
                           "Sous-total"],
    },
}


def _get_column_labels(locale: str) -> dict[str, list[str]]:
    """Return the column label variants for the given Faker locale."""
    lang = _LOCALE_TO_LANGUAGE.get(locale, "en")
    return _COLUMN_LABELS_BY_LANGUAGE.get(lang, _COLUMN_LABELS_BY_LANGUAGE["en"])


# Column definitions (label will be randomized at selection time)
COLUMN_DEFS: dict[str, dict[str, str]] = {
    "position": {"align": "right", "format": "int"},
    "article_number": {"align": "left", "format": "text"},
    "description": {"align": "left", "format": "text"},
    "quantity": {"align": "right", "format": "int"},
    "unit_price": {"align": "right", "format": "currency"},
    "tax_rate": {"align": "right", "format": "percent"},
    "line_total": {"align": "right", "format": "currency"},
}

# Columns that must always be present
REQUIRED_FIELDS: set[str] = {"description", "quantity", "unit_price", "line_total"}

# Maps each column field to its BIO entity label
FIELD_TO_ENTITY_LABEL: dict[str, str] = {
    "position": "position",
    "article_number": "article_number",
    "description": "item_description",
    "quantity": "quantity",
    "unit_price": "unit_price",
    "tax_rate": "tax",
    "line_total": "line_total",
}


def format_cell_value(item: object, column: "Column", number_format: NumberFormat) -> str:
    """Format a line item cell value exactly as rendered in the invoice HTML."""
    value = getattr(item, column.field)
    if column.format == "currency":
        return number_format.format_number(float(value))  # type: ignore[arg-type]
    elif column.format == "percent":
        return f"{float(value) * 100:.0f}%"  # type: ignore[arg-type]
    elif column.format == "int":
        return str(int(value))  # type: ignore[arg-type]
    return str(value)


from models.number_format import NumberFormat

# Module-level reference set per render call
_active_number_format: NumberFormat | None = None


def _get_attr(obj: object, name: str) -> object:
    """Jinja2 filter: get attribute or property from an object."""
    return getattr(obj, name)


def _format_value(value: object, fmt: str) -> str:
    """Jinja2 filter: format a value based on column format type."""
    nf = _active_number_format
    if fmt == "currency" and nf is not None:
        return nf.format_number(float(value))  # type: ignore[arg-type]
    elif fmt == "currency":
        return f"{float(value):.2f}"  # type: ignore[arg-type]
    elif fmt == "percent":
        return f"{float(value) * 100:.0f}%"  # type: ignore[arg-type]
    elif fmt == "int":
        return str(int(value))  # type: ignore[arg-type]
    return str(value)


def _format_currency(value: float) -> str:
    """Jinja2 filter: format a value as full currency string (number + symbol)."""
    nf = _active_number_format
    if nf is not None:
        return nf.format_currency(value)
    return f"{value:.2f}"


def _build_jinja_env() -> Environment:
    """Create a Jinja2 environment with custom filters."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    env.filters["attr"] = _get_attr
    env.filters["format_value"] = _format_value
    env.filters["format_currency"] = _format_currency
    return env


def _make_column(field: str, locale: str = "en_US") -> Column:
    """Create a Column with a randomly chosen label variant for the given locale."""
    definition = COLUMN_DEFS[field]
    labels = _get_column_labels(locale)
    label = random.choice(labels[field])
    return Column(
        field=field,
        label=label,
        align=definition["align"],
        format=definition["format"],
    )


def select_columns(invoice: Invoice, seed: int | None = None) -> list[Column]:
    """Select and optionally shuffle columns for variety.

    Always includes required columns, randomly adds optional ones,
    randomizes column labels (in the invoice's locale language), and
    shuffles column order. Excludes article_number when the invoice
    has no article numbers.
    """
    if seed is not None:
        random.seed(seed)

    has_article_numbers = any(
        item.article_number is not None for item in invoice.line_items
    )

    # Always include required columns
    fields = list(REQUIRED_FIELDS)

    # Randomly include optional columns
    optional_fields = [f for f in COLUMN_DEFS if f not in REQUIRED_FIELDS]
    for field in optional_fields:
        if field == "article_number" and not has_article_numbers:
            continue
        if random.random() > 0.3:
            fields.append(field)

    # Build columns with locale-appropriate random labels and shuffle order
    columns = [_make_column(f, invoice.locale) for f in fields]
    random.shuffle(columns)

    return columns


def render_html(invoice: Invoice, columns: list[Column],
                template_name: str = "layout_000.html") -> str:
    """Render an invoice to an HTML string."""
    global _active_number_format
    _active_number_format = invoice.number_format

    env = _build_jinja_env()
    template = env.get_template(template_name)

    return template.render(
        invoice=invoice,
        columns=columns,
        style=invoice.style,
    )


class PdfRenderer:
    """Manages a Playwright browser instance for rendering HTML to PDF."""

    def __init__(self) -> None:
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()

    def render(self, html_content: str, output_path: Path) -> None:
        """Convert HTML string to a PDF file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        page = self._browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        page.close()

    def close(self) -> None:
        self._browser.close()
        self._pw.stop()
