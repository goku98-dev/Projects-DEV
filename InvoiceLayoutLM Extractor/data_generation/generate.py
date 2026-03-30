"""Main entry point for generating synthetic invoices."""

import argparse
import itertools
import json
import random
from pathlib import Path

from data_generator import generate_invoice
from models.invoice import Invoice
from renderer import (
    Column, PdfRenderer, FIELD_TO_ENTITY_LABEL,
    format_cell_value, render_html, select_columns, TEMPLATES_DIR,
)


DEFAULT_OUTPUT_DIR = Path(__file__).parent / "output"


def _get_layout_templates() -> list[str]:
    """Discover all layout template files."""
    templates = sorted(p.name for p in TEMPLATES_DIR.glob("layout_*.html"))
    if not templates:
        raise FileNotFoundError(
            f"No layout templates found in {TEMPLATES_DIR}. "
            "Run template_generator.py first."
        )
    return templates


def _build_template_schedule(templates: list[str], count: int, seed: int) -> list[str]:
    """Build a template assignment list ensuring even distribution.

    Cycles through all templates, then shuffles so the order isn't
    predictable but every template is used equally (±1).
    """
    rng = random.Random(seed)
    # Repeat templates enough times to cover count, then trim
    full_cycles = list(itertools.islice(itertools.cycle(templates), count))
    # Shuffle to avoid sequential pattern
    rng.shuffle(full_cycles)
    return full_cycles


def _build_invoice_metadata(
    invoice: Invoice,
    columns: list[Column],
    invoice_id: str,
    template_name: str,
) -> dict:
    """Build a metadata dict capturing ground truth cell values for annotation."""
    col_meta = [
        {
            "field": col.field,
            "label": col.label,
            "entity_label": FIELD_TO_ENTITY_LABEL.get(col.field),
            "format": col.format,
        }
        for col in columns
    ]
    line_items = [
        {col.field: format_cell_value(item, col, invoice.number_format) for col in columns}
        for item in invoice.line_items
    ]
    return {
        "invoice_id": invoice_id,
        "locale": invoice.locale,
        "template": template_name,
        "columns": col_meta,
        "line_items": line_items,
    }


def generate_batch(count: int, output_dir: Path, locale: str = "de_DE",
                   seed: int = 42) -> None:
    """Generate a batch of synthetic invoices as PDF files."""
    pdf_dir = output_dir / "pdfs"
    html_dir = output_dir / "html"
    metadata_dir = output_dir / "metadata"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    templates = _get_layout_templates()
    template_schedule = _build_template_schedule(templates, count, seed)
    pdf_renderer = PdfRenderer()

    try:
        for i in range(count):
            invoice = generate_invoice(locale=locale, seed=i)
            columns = select_columns(invoice, seed=i)
            template_name = template_schedule[i]

            html_content = render_html(invoice, columns, template_name=template_name)

            invoice_id = f"invoice_{i:04d}"

            # Save HTML for debugging
            html_path = html_dir / f"{invoice_id}.html"
            html_path.write_text(html_content, encoding="utf-8")

            # Render PDF
            pdf_path = pdf_dir / f"{invoice_id}.pdf"
            pdf_renderer.render(html_content, pdf_path)

            # Save ground truth metadata for annotation
            metadata = _build_invoice_metadata(invoice, columns, invoice_id, template_name)
            metadata_path = metadata_dir / f"{invoice_id}.json"
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            print(f"[{i + 1}/{count}] Generated {pdf_path.name} (template: {template_name})")
    finally:
        pdf_renderer.close()

    print(f"\nDone. {count} invoices saved to {output_dir}")
    print(f"Templates used: {len(templates)}, ~{count // len(templates)} invoices each")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic invoices")
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Number of invoices to generate (default: 10)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--locale",
        type=str,
        default="random",
        help="Faker locale (default: random). Use 'random' for mixed locales, or e.g. 'de_DE'",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    args = parser.parse_args()

    generate_batch(count=args.count, output_dir=args.output, locale=args.locale,
                   seed=args.seed)


if __name__ == "__main__":
    main()
