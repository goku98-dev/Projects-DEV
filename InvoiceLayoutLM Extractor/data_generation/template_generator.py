"""Generates structurally diverse invoice Jinja2 templates.

Each template is a unique combination of layout components:
- Header style (title + invoice meta positioning)
- Address layout (seller/buyer block arrangement)
- Table style (borders, header, row styling)
- Table position (vertical spacing before the table)
- Table width (full width vs narrower)
- Totals style (summary section layout)
- Footer (optional payment/bank info section)
"""

import itertools
import random
from dataclasses import dataclass
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


# ---------------------------------------------------------------------------
# Layout component definitions
# ---------------------------------------------------------------------------

@dataclass
class LayoutVariant:
    name: str
    css: str
    html: str


# ---- Header Variants ----

HEADER_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(
        name="header_left_meta_right",
        css="""
        .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; }
        .invoice-title { font-size: {{ style.font_size_pt * 2 }}pt; font-weight: bold; color: {{ style.header_bg_color }}; margin-bottom: 8px; }
        .invoice-meta { text-align: right; }
        .invoice-meta p { margin-bottom: 4px; }
        """,
        html="""
    <div class="header">
        <div>
            <div class="invoice-title">INVOICE</div>
            <p>{{ invoice.seller.name }}</p>
        </div>
        <div class="invoice-meta">
            <p><strong>Invoice #:</strong> {{ invoice.invoice_number }}</p>
            <p><strong>Date:</strong> {{ invoice.invoice_date }}</p>
            <p><strong>Due Date:</strong> {{ invoice.due_date }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="header_centered",
        css="""
        .header { text-align: center; margin-bottom: 30px; }
        .invoice-title { font-size: {{ style.font_size_pt * 2.5 }}pt; font-weight: bold; color: {{ style.header_bg_color }}; margin-bottom: 10px; }
        .invoice-meta { margin-top: 10px; }
        .invoice-meta span { margin: 0 15px; }
        """,
        html="""
    <div class="header">
        <div class="invoice-title">INVOICE</div>
        <p>{{ invoice.seller.name }}</p>
        <div class="invoice-meta">
            <span><strong>Invoice #:</strong> {{ invoice.invoice_number }}</span>
            <span><strong>Date:</strong> {{ invoice.invoice_date }}</span>
            <span><strong>Due Date:</strong> {{ invoice.due_date }}</span>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="header_banner",
        css="""
        .header { background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; padding: 20px 25px; margin: -20mm -20mm 30px -20mm; display: flex; justify-content: space-between; align-items: center; }
        .invoice-title { font-size: {{ style.font_size_pt * 2 }}pt; font-weight: bold; }
        .invoice-meta { text-align: right; }
        .invoice-meta p { margin-bottom: 4px; }
        """,
        html="""
    <div class="header">
        <div>
            <div class="invoice-title">INVOICE</div>
            <p>{{ invoice.seller.name }}</p>
        </div>
        <div class="invoice-meta">
            <p>Invoice #: {{ invoice.invoice_number }}</p>
            <p>Date: {{ invoice.invoice_date }}</p>
            <p>Due: {{ invoice.due_date }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="header_minimal",
        css="""
        .header { border-bottom: 2px solid {{ style.header_bg_color }}; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end; }
        .invoice-title { font-size: {{ style.font_size_pt * 1.5 }}pt; font-weight: bold; color: {{ style.header_bg_color }}; }
        .invoice-meta { text-align: right; font-size: {{ style.font_size_pt - 1 }}pt; }
        .invoice-meta p { margin-bottom: 2px; }
        """,
        html="""
    <div class="header">
        <div class="invoice-title">{{ invoice.seller.name }}</div>
        <div class="invoice-meta">
            <p>{{ invoice.invoice_number }}</p>
            <p>{{ invoice.invoice_date }}</p>
            <p>Due: {{ invoice.due_date }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="header_right_aligned",
        css="""
        .header { text-align: right; margin-bottom: 30px; }
        .invoice-title { font-size: {{ style.font_size_pt * 2 }}pt; font-weight: bold; color: {{ style.header_bg_color }}; margin-bottom: 5px; }
        .invoice-meta p { margin-bottom: 3px; }
        .company-name { font-size: {{ style.font_size_pt + 2 }}pt; margin-bottom: 10px; }
        """,
        html="""
    <div class="header">
        <div class="invoice-title">INVOICE</div>
        <div class="company-name">{{ invoice.seller.name }}</div>
        <div class="invoice-meta">
            <p>Invoice No: {{ invoice.invoice_number }}</p>
            <p>Invoice Date: {{ invoice.invoice_date }}</p>
            <p>Payment Due: {{ invoice.due_date }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="header_two_tone",
        css="""
        .header { margin: -20mm -20mm 30px -20mm; }
        .header-top { background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; padding: 15px 25px; }
        .header-bottom { background-color: #f5f5f5; padding: 10px 25px; display: flex; justify-content: space-between; border-bottom: 1px solid #ddd; }
        .invoice-title { font-size: {{ style.font_size_pt * 2 }}pt; font-weight: bold; }
        .invoice-meta span { margin-right: 20px; font-size: {{ style.font_size_pt - 1 }}pt; }
        """,
        html="""
    <div class="header">
        <div class="header-top">
            <div class="invoice-title">{{ invoice.seller.name }}</div>
        </div>
        <div class="header-bottom">
            <span>Invoice {{ invoice.invoice_number }}</span>
            <span>Date: {{ invoice.invoice_date }}</span>
            <span>Due: {{ invoice.due_date }}</span>
        </div>
    </div>
        """,
    ),
]

# ---- Address Layout Variants ----

ADDRESS_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(
        name="addr_side_by_side",
        css="""
        .addresses { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .address-block { width: 45%; }
        .address-block .label { font-weight: bold; text-transform: uppercase; color: #777; margin-bottom: 6px; font-size: {{ style.font_size_pt - 1 }}pt; }
        .address-block p { margin-bottom: 2px; }
        """,
        html="""
    <div class="addresses">
        <div class="address-block">
            <div class="label">From</div>
            <p>{{ invoice.seller.name }}</p>
            <p>{{ invoice.seller.street }}</p>
            <p>{{ invoice.seller.postal_code }} {{ invoice.seller.city }}</p>
            <p>{{ invoice.seller.country }}</p>
        </div>
        <div class="address-block">
            <div class="label">Bill To</div>
            <p>{{ invoice.buyer.name }}</p>
            <p>{{ invoice.buyer.street }}</p>
            <p>{{ invoice.buyer.postal_code }} {{ invoice.buyer.city }}</p>
            <p>{{ invoice.buyer.country }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="addr_reversed",
        css="""
        .addresses { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .address-block { width: 45%; }
        .address-block .label { font-weight: bold; text-transform: uppercase; color: #777; margin-bottom: 6px; font-size: {{ style.font_size_pt - 1 }}pt; }
        .address-block p { margin-bottom: 2px; }
        """,
        html="""
    <div class="addresses">
        <div class="address-block">
            <div class="label">Bill To</div>
            <p>{{ invoice.buyer.name }}</p>
            <p>{{ invoice.buyer.street }}</p>
            <p>{{ invoice.buyer.postal_code }} {{ invoice.buyer.city }}</p>
            <p>{{ invoice.buyer.country }}</p>
        </div>
        <div class="address-block">
            <div class="label">From</div>
            <p>{{ invoice.seller.name }}</p>
            <p>{{ invoice.seller.street }}</p>
            <p>{{ invoice.seller.postal_code }} {{ invoice.seller.city }}</p>
            <p>{{ invoice.seller.country }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="addr_stacked",
        css="""
        .addresses { margin-bottom: 30px; }
        .address-block { margin-bottom: 15px; }
        .address-block .label { font-weight: bold; text-transform: uppercase; color: #777; margin-bottom: 4px; font-size: {{ style.font_size_pt - 1 }}pt; }
        .address-block p { margin-bottom: 2px; }
        """,
        html="""
    <div class="addresses">
        <div class="address-block">
            <div class="label">Seller</div>
            <p>{{ invoice.seller.name }}</p>
            <p>{{ invoice.seller.street }}, {{ invoice.seller.postal_code }} {{ invoice.seller.city }}, {{ invoice.seller.country }}</p>
        </div>
        <div class="address-block">
            <div class="label">Buyer</div>
            <p>{{ invoice.buyer.name }}</p>
            <p>{{ invoice.buyer.street }}, {{ invoice.buyer.postal_code }} {{ invoice.buyer.city }}, {{ invoice.buyer.country }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="addr_boxed",
        css="""
        .addresses { display: flex; justify-content: space-between; margin-bottom: 30px; gap: 20px; }
        .address-block { width: 45%; border: 1px solid {{ style.border_color }}; padding: 12px 15px; }
        .address-block .label { font-weight: bold; color: {{ style.header_bg_color }}; margin-bottom: 8px; font-size: {{ style.font_size_pt }}pt; }
        .address-block p { margin-bottom: 2px; }
        """,
        html="""
    <div class="addresses">
        <div class="address-block">
            <div class="label">Sender</div>
            <p>{{ invoice.seller.name }}</p>
            <p>{{ invoice.seller.street }}</p>
            <p>{{ invoice.seller.postal_code }} {{ invoice.seller.city }}</p>
            <p>{{ invoice.seller.country }}</p>
        </div>
        <div class="address-block">
            <div class="label">Recipient</div>
            <p>{{ invoice.buyer.name }}</p>
            <p>{{ invoice.buyer.street }}</p>
            <p>{{ invoice.buyer.postal_code }} {{ invoice.buyer.city }}</p>
            <p>{{ invoice.buyer.country }}</p>
        </div>
    </div>
        """,
    ),
    LayoutVariant(
        name="addr_buyer_right_only",
        css="""
        .addresses { display: flex; justify-content: flex-end; margin-bottom: 30px; }
        .address-block { width: 45%; }
        .address-block .label { font-weight: bold; text-transform: uppercase; color: #777; margin-bottom: 6px; font-size: {{ style.font_size_pt - 1 }}pt; }
        .address-block p { margin-bottom: 2px; }
        """,
        html="""
    <div class="addresses">
        <div class="address-block">
            <div class="label">Invoice To</div>
            <p>{{ invoice.buyer.name }}</p>
            <p>{{ invoice.buyer.street }}</p>
            <p>{{ invoice.buyer.postal_code }} {{ invoice.buyer.city }}</p>
            <p>{{ invoice.buyer.country }}</p>
        </div>
    </div>
        """,
    ),
]

# ---- Table Style Variants ----

TABLE_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(
        name="table_full_borders",
        css="""
        thead th { background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; padding: 8px 10px; text-align: left; border: 1px solid {{ style.border_color }}; }
        thead th.num { text-align: right; }
        tbody td { padding: 6px 10px; border: 1px solid {{ style.border_color }}; }
        tbody td.num { text-align: right; }
        {% if style.row_alt_bg_color != "#ffffff" %}
        tbody tr:nth-child(even) { background-color: {{ style.row_alt_bg_color }}; }
        {% endif %}
        """,
        html="",
    ),
    LayoutVariant(
        name="table_horizontal_lines",
        css="""
        thead th { padding: 8px 10px; text-align: left; border-bottom: 2px solid {{ style.header_bg_color }}; color: {{ style.header_bg_color }}; font-weight: bold; }
        thead th.num { text-align: right; }
        tbody td { padding: 8px 10px; border-bottom: 1px solid #e0e0e0; }
        tbody td.num { text-align: right; }
        """,
        html="",
    ),
    LayoutVariant(
        name="table_striped_no_borders",
        css="""
        thead th { padding: 10px; text-align: left; background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; }
        thead th.num { text-align: right; }
        tbody td { padding: 8px 10px; }
        tbody td.num { text-align: right; }
        tbody tr:nth-child(odd) { background-color: {{ style.row_alt_bg_color }}; }
        """,
        html="",
    ),
    LayoutVariant(
        name="table_minimal",
        css="""
        thead th { padding: 6px 10px; text-align: left; font-weight: normal; text-transform: uppercase; font-size: {{ style.font_size_pt - 2 }}pt; color: #999; letter-spacing: 0.5px; border-bottom: 1px solid #ccc; }
        thead th.num { text-align: right; }
        tbody td { padding: 8px 10px; }
        tbody td.num { text-align: right; }
        tbody tr:last-child td { border-bottom: 1px solid #ccc; }
        """,
        html="",
    ),
    LayoutVariant(
        name="table_boxed",
        css="""
        .table-wrapper table { border: 2px solid {{ style.header_bg_color }}; }
        thead th { padding: 10px; text-align: left; background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; border-right: 1px solid rgba(255,255,255,0.2); }
        thead th:last-child { border-right: none; }
        thead th.num { text-align: right; }
        tbody td { padding: 8px 10px; border-right: 1px solid #eee; }
        tbody td:last-child { border-right: none; }
        tbody td.num { text-align: right; }
        tbody tr:nth-child(even) { background-color: {{ style.row_alt_bg_color }}; }
        """,
        html="",
    ),
    LayoutVariant(
        name="table_dotted",
        css="""
        thead th { padding: 8px 10px; text-align: left; border-bottom: 2px dotted {{ style.header_bg_color }}; color: {{ style.header_bg_color }}; }
        thead th.num { text-align: right; }
        tbody td { padding: 7px 10px; border-bottom: 1px dotted #ccc; }
        tbody td.num { text-align: right; }
        """,
        html="",
    ),
]

# ---- Table Position Variants (vertical spacing before table) ----

TABLE_POSITION_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(name="tpos_normal", css=".table-wrapper { margin-top: 0; }", html=""),
    LayoutVariant(name="tpos_pushed_down", css=".table-wrapper { margin-top: 40px; }", html=""),
    LayoutVariant(name="tpos_far_down", css=".table-wrapper { margin-top: 80px; }", html=""),
]

# ---- Table Width Variants ----

TABLE_WIDTH_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(name="twidth_full", css=".table-wrapper table { width: 100%; }", html=""),
    LayoutVariant(name="twidth_95", css=".table-wrapper table { width: 95%; }", html=""),
    LayoutVariant(name="twidth_90", css=".table-wrapper table { width: 90%; }", html=""),
]

# ---- Totals Style Variants (using format_currency filter) ----

TOTALS_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(
        name="totals_right_table",
        css="""
        .totals { width: 280px; margin-left: auto; }
        .totals table { margin-bottom: 0; }
        .totals td { padding: 4px 10px; border: none !important; }
        .totals .total-row { font-weight: bold; font-size: {{ style.font_size_pt + 2 }}pt; }
        .totals .total-row td { border-top: 2px solid {{ style.header_bg_color }} !important; }
        """,
        html="""
    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td class="num">{{ invoice.subtotal | format_currency }}</td>
            </tr>
            <tr>
                <td>Tax:</td>
                <td class="num">{{ invoice.total_tax | format_currency }}</td>
            </tr>
            <tr class="total-row">
                <td>Total:</td>
                <td class="num">{{ invoice.total | format_currency }}</td>
            </tr>
        </table>
    </div>
        """,
    ),
    LayoutVariant(
        name="totals_boxed",
        css="""
        .totals { width: 300px; margin-left: auto; border: 1px solid {{ style.border_color }}; padding: 10px; }
        .totals table { margin-bottom: 0; width: 100%; }
        .totals td { padding: 4px 8px; border: none !important; }
        .totals .total-row { font-weight: bold; font-size: {{ style.font_size_pt + 2 }}pt; background-color: {{ style.header_bg_color }}; color: {{ style.header_text_color }}; }
        """,
        html="""
    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td class="num">{{ invoice.subtotal | format_currency }}</td>
            </tr>
            <tr>
                <td>Tax:</td>
                <td class="num">{{ invoice.total_tax | format_currency }}</td>
            </tr>
            <tr class="total-row">
                <td>Total:</td>
                <td class="num">{{ invoice.total | format_currency }}</td>
            </tr>
        </table>
    </div>
        """,
    ),
    LayoutVariant(
        name="totals_inline_right",
        css="""
        .totals { text-align: right; margin-bottom: 20px; }
        .totals .line { margin-bottom: 4px; }
        .totals .total-line { font-weight: bold; font-size: {{ style.font_size_pt + 3 }}pt; color: {{ style.header_bg_color }}; border-top: 2px solid {{ style.header_bg_color }}; padding-top: 6px; display: inline-block; }
        """,
        html="""
    <div class="totals">
        <div class="line">Subtotal: {{ invoice.subtotal | format_currency }}</div>
        <div class="line">Tax: {{ invoice.total_tax | format_currency }}</div>
        <div class="total-line">Total: {{ invoice.total | format_currency }}</div>
    </div>
        """,
    ),
    LayoutVariant(
        name="totals_full_width",
        css="""
        .totals { border-top: 1px solid {{ style.border_color }}; padding-top: 10px; }
        .totals table { width: 100%; margin-bottom: 0; }
        .totals td { padding: 4px 10px; border: none !important; }
        .totals td:first-child { text-align: right; width: 80%; }
        .totals td:last-child { text-align: right; width: 20%; }
        .totals .total-row { font-weight: bold; font-size: {{ style.font_size_pt + 2 }}pt; }
        .totals .total-row td { border-top: 2px solid {{ style.header_bg_color }} !important; }
        """,
        html="""
    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td>{{ invoice.subtotal | format_currency }}</td>
            </tr>
            <tr>
                <td>Tax:</td>
                <td>{{ invoice.total_tax | format_currency }}</td>
            </tr>
            <tr class="total-row">
                <td>Total:</td>
                <td>{{ invoice.total | format_currency }}</td>
            </tr>
        </table>
    </div>
        """,
    ),
]

# ---- Footer Variants ----

FOOTER_VARIANTS: list[LayoutVariant] = [
    LayoutVariant(
        name="footer_none",
        css="",
        html="",
    ),
    LayoutVariant(
        name="footer_payment_info",
        css="""
        .footer { margin-top: 40px; padding-top: 15px; border-top: 1px solid #ddd; font-size: {{ style.font_size_pt - 2 }}pt; color: #666; }
        .footer p { margin-bottom: 3px; }
        """,
        html="""
    <div class="footer">
        <p><strong>Payment Terms:</strong> {{ invoice.payment_info.payment_terms }}</p>
        <p><strong>Bank:</strong> {{ invoice.payment_info.bank_name }} | IBAN: {{ invoice.payment_info.iban }} | BIC: {{ invoice.payment_info.bic }}</p>
        <p>Thank you for your business.</p>
    </div>
        """,
    ),
    LayoutVariant(
        name="footer_bank_and_notes",
        css="""
        .footer { margin-top: 40px; padding: 12px 15px; background-color: #f8f8f8; font-size: {{ style.font_size_pt - 1 }}pt; color: #555; }
        .footer .footer-title { font-weight: bold; margin-bottom: 5px; }
        .footer p { margin-bottom: 3px; }
        """,
        html="""
    <div class="footer">
        <div class="footer-title">Payment Information</div>
        <p>{{ invoice.payment_info.bank_name }}</p>
        <p>IBAN: {{ invoice.payment_info.iban }}</p>
        <p>BIC: {{ invoice.payment_info.bic }}</p>
        <p style="margin-top: 8px;">{{ invoice.payment_info.payment_terms }}</p>
    </div>
        """,
    ),
    LayoutVariant(
        name="footer_terms_only",
        css="""
        .footer { margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee; font-size: {{ style.font_size_pt - 1 }}pt; color: #666; }
        """,
        html="""
    <div class="footer">
        <p>{{ invoice.payment_info.payment_terms }}</p>
    </div>
        """,
    ),
    LayoutVariant(
        name="footer_compact",
        css="""
        .footer { margin-top: 30px; font-size: {{ style.font_size_pt - 2 }}pt; color: #999; text-align: center; }
        .footer p { margin-bottom: 2px; }
        """,
        html="""
    <div class="footer">
        <p>{{ invoice.seller.name }} | {{ invoice.seller.street }}, {{ invoice.seller.postal_code }} {{ invoice.seller.city }} | {{ invoice.seller.country }}</p>
        <p>{{ invoice.payment_info.bank_name }} | IBAN: {{ invoice.payment_info.iban }}</p>
    </div>
        """,
    ),
]


# ---- Table HTML (shared across all table style variants) ----

TABLE_HTML = """
    <div class="table-wrapper">
    <table>
        <thead>
            <tr>
                {% for col in columns %}
                <th{% if col.align == "right" %} class="num"{% endif %}>{{ col.label }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for item in invoice.line_items %}
            <tr>
                {% for col in columns %}
                <td{% if col.align == "right" %} class="num"{% endif %}>{{ item | attr(col.field) | format_value(col.format) }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    </div>
"""


# ---------------------------------------------------------------------------
# Template assembly
# ---------------------------------------------------------------------------

def _assemble_template(
    header: LayoutVariant,
    address: LayoutVariant,
    table_style: LayoutVariant,
    table_position: LayoutVariant,
    table_width: LayoutVariant,
    totals: LayoutVariant,
    footer: LayoutVariant,
) -> str:
    """Assemble a full Jinja2 HTML template from layout components."""
    css_parts = [
        header.css, address.css,
        # Table CSS: combine style, position, and width
        "table { border-collapse: collapse; margin-bottom: 30px; }",
        table_style.css, table_position.css, table_width.css,
        totals.css, footer.css,
    ]
    combined_css = "\n".join(css_parts)

    footer_html = footer.html if footer.html else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: {{{{ style.font_family }}}};
            font-size: {{{{ style.font_size_pt }}}}pt;
            color: #333333;
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
        }}
{combined_css}
    </style>
</head>
<body>
{header.html}
{address.html}
{TABLE_HTML}
{totals.html}
{footer_html}
</body>
</html>
"""


def generate_templates(count: int = 30, seed: int = 42) -> list[str]:
    """Generate a set of unique template combinations.

    Picks from the most impactful variation dimensions (header, address,
    table style, totals, footer) and randomly assigns table position
    and width to each.
    """
    random.seed(seed)

    # Primary structural combinations (header × address × table × totals × footer)
    all_combos = list(itertools.product(
        HEADER_VARIANTS, ADDRESS_VARIANTS, TABLE_VARIANTS,
        TOTALS_VARIANTS, FOOTER_VARIANTS,
    ))

    random.shuffle(all_combos)
    selected = all_combos[:count]

    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    filenames: list[str] = []

    for i, (header, address, table_style, totals, footer) in enumerate(selected):
        # Randomly assign secondary variations
        table_pos = random.choice(TABLE_POSITION_VARIANTS)
        table_width = random.choice(TABLE_WIDTH_VARIANTS)

        template_content = _assemble_template(
            header, address, table_style, table_pos, table_width, totals, footer,
        )
        filename = f"layout_{i:03d}.html"
        filepath = TEMPLATES_DIR / filename
        filepath.write_text(template_content, encoding="utf-8")
        filenames.append(filename)

        parts = [header.name, address.name, table_style.name,
                 table_pos.name, table_width.name, totals.name, footer.name]
        print(f"  [{i + 1}/{count}] {filename}: {' | '.join(parts)}")

    return filenames


if __name__ == "__main__":
    print("Generating invoice templates...")
    names = generate_templates(count=30)
    print(f"\nDone. {len(names)} templates created in {TEMPLATES_DIR}")
