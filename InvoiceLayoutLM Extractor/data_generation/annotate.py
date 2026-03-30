"""Generates word-level BIO annotations for synthetic invoices (LayoutLMv3 format).

Words and bounding boxes are extracted directly from the embedded PDF text via
PyMuPDF rather than OCR. This gives perfect coverage — OCR misses many table
cells in narrow columns, while PDF text extraction is 100% reliable for
programmatically generated documents.
"""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


DEFAULT_OUTPUT_DIR = Path(__file__).parent / "output"
DEFAULT_DPI = 300


@dataclass
class _Token:
    text: str
    bbox: list[int]   # [x0, y0, x1, y1] normalized to 0-1000
    label: str = "O"


@dataclass
class InvoiceAnnotation:
    id: str
    image_path: str
    words: list[str]
    bboxes: list[list[int]]
    ner_tags: list[str]


def _open_pdf_page(pdf_path: Path) -> tuple[fitz.Document, fitz.Page]:
    doc = fitz.open(str(pdf_path))
    return doc, doc[0]


def pdf_to_image(page: fitz.Page, dpi: int = DEFAULT_DPI) -> Image.Image:
    """Render a PDF page as a PIL image."""
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def _merge_hyphen_splits(tokens: list[_Token]) -> list[_Token]:
    """Merge tokens that were split at a line-wrapping hyphen.

    In narrow table cells, a word like '(100-pack)' can be broken across two
    lines by the PDF renderer as '(100-' on line 1 and 'pack)' on line 2.
    PyMuPDF returns them as separate tokens, which breaks exact matching against
    the metadata. We detect this by checking for tokens that end with '-' and
    merge them with the immediately following token, spanning both bboxes.
    """
    merged: list[_Token] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.text.endswith("-") and i + 1 < len(tokens):
            nxt = tokens[i + 1]
            merged.append(_Token(
                text=token.text + nxt.text,
                bbox=[
                    min(token.bbox[0], nxt.bbox[0]),
                    min(token.bbox[1], nxt.bbox[1]),
                    max(token.bbox[2], nxt.bbox[2]),
                    max(token.bbox[3], nxt.bbox[3]),
                ],
            ))
            i += 2
        else:
            merged.append(token)
            i += 1
    return merged


def extract_words(page: fitz.Page) -> list[_Token]:
    """Extract embedded words from a PDF page with bboxes normalized to 0-1000.

    Uses PyMuPDF text extraction instead of OCR. Since the PDFs are generated
    programmatically, every word is perfectly embedded — no tokens are missed.
    PyMuPDF returns (x0, y0, x1, y1, word, block, line, word_no) tuples.
    Hyphen-split tokens (line-wrapping artefacts) are merged back into one token.
    """
    pw = page.rect.width
    ph = page.rect.height
    tokens: list[_Token] = []
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        word = word.strip()
        if not word:
            continue
        tokens.append(_Token(
            text=word,
            bbox=[
                round(x0 / pw * 1000),
                round(y0 / ph * 1000),
                round(x1 / pw * 1000),
                round(y1 / ph * 1000),
            ],
        ))
    return _merge_hyphen_splits(tokens)


_ROW_Y_TOLERANCE = 15  # in normalized 0-1000 units (~half a table row height)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _find_sequence(
    needle: list[str],
    tokens: list[_Token],
    skip: set[int],
    y_band: tuple[int, int] | None = None,
) -> list[int] | None:
    """Return indices of the first occurrence of needle in tokens,
    skipping already-labeled positions.

    When y_band=(y_min, y_max) is given, only considers tokens whose vertical
    center falls within [y_min - tolerance, y_max + tolerance]. This prevents
    matching a number like '3' in the invoice header instead of the table row.
    """
    n = len(needle)
    for i in range(len(tokens) - n + 1):
        if any((i + j) in skip for j in range(n)):
            continue
        if y_band is not None:
            y_min, y_max = y_band
            in_band = all(
                y_min - _ROW_Y_TOLERANCE
                <= (tokens[i + j].bbox[1] + tokens[i + j].bbox[3]) / 2
                <= y_max + _ROW_Y_TOLERANCE
                for j in range(n)
            )
            if not in_band:
                continue
        if all(_normalize(tokens[i + j].text) == _normalize(needle[j]) for j in range(n)):
            return list(range(i, i + n))
    return None


def _apply_labels(
    tokens: list[_Token],
    indices: list[int],
    entity_label: str,
    labeled: set[int],
) -> None:
    for j, idx in enumerate(indices):
        tokens[idx].label = f"{'B' if j == 0 else 'I'}-{entity_label}"
        labeled.add(idx)


def _label_tokens(tokens: list[_Token], metadata: dict) -> None:
    """Assign BIO labels to tokens in-place using ground truth metadata.

    Strategy: for each line item row, the description is matched first (globally,
    as it is unique). Its y-coordinates then define a row-level y-band. All other
    columns (quantity, unit_price, etc.) are matched only within that band, so a
    number like '3' or '19%' that also appears in the invoice header or totals
    section is never incorrectly labeled.

    If a description cannot be matched (OCR failure), all columns for that row
    fall back to unconstrained matching so we still recover as many labels as
    possible.
    """
    labeled: set[int] = set()
    columns: list[dict] = metadata["columns"]
    desc_col = next((c for c in columns if c["field"] == "description"), None)

    for item_row in metadata["line_items"]:
        y_band: tuple[int, int] | None = None

        # ── Step 1: anchor the row via the description ──────────────────────
        if desc_col and desc_col.get("entity_label"):
            desc_value = item_row.get("description", "").strip()
            if desc_value:
                desc_seq = desc_value.split()
                desc_indices = _find_sequence(desc_seq, tokens, labeled)
                if desc_indices is not None:
                    y_min = min(tokens[i].bbox[1] for i in desc_indices)
                    y_max = max(tokens[i].bbox[3] for i in desc_indices)
                    y_band = (y_min, y_max)
                    _apply_labels(tokens, desc_indices, desc_col["entity_label"], labeled)

        # ── Step 2: match remaining columns, constrained to the row's y-band ─
        for col in columns:
            if col["field"] == "description":
                continue
            entity_label: str | None = col.get("entity_label")
            if not entity_label:
                continue
            cell_value: str = item_row.get(col["field"], "").strip()
            if not cell_value:
                continue

            word_seq = cell_value.split()
            indices = _find_sequence(word_seq, tokens, labeled, y_band=y_band)
            if indices is not None:
                _apply_labels(tokens, indices, entity_label, labeled)


def annotate_invoice(
    invoice_id: str,
    pdf_path: Path,
    metadata_path: Path,
    images_dir: Path,
    annotations_dir: Path,
    output_dir: Path,
    dpi: int = DEFAULT_DPI,
) -> InvoiceAnnotation:
    """Run the full annotation pipeline for a single invoice."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    doc, page = _open_pdf_page(pdf_path)
    try:
        # Render PDF page to image
        image = pdf_to_image(page, dpi=dpi)
        image_path = images_dir / f"{invoice_id}.png"
        image.save(str(image_path))

        # Extract words + bboxes from embedded PDF text (no OCR)
        tokens = extract_words(page)
    finally:
        doc.close()

    # BIO labeling
    _label_tokens(tokens, metadata)

    # Build and save annotation
    annotation = InvoiceAnnotation(
        id=invoice_id,
        image_path=str(image_path.relative_to(output_dir)).replace("\\", "/"),
        words=[t.text for t in tokens],
        bboxes=[t.bbox for t in tokens],
        ner_tags=[t.label for t in tokens],
    )
    out_path = annotations_dir / f"{invoice_id}.json"
    out_path.write_text(
        json.dumps(asdict(annotation), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return annotation


def annotate_batch(output_dir: Path = DEFAULT_OUTPUT_DIR, dpi: int = DEFAULT_DPI) -> None:
    """Annotate all invoices that have both a PDF and a metadata JSON."""
    pdf_dir = output_dir / "pdfs"
    metadata_dir = output_dir / "metadata"
    images_dir = output_dir / "images"
    annotations_dir = output_dir / "annotations"
    images_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    invoice_ids = sorted(p.stem for p in pdf_dir.glob("invoice_*.pdf"))
    total = len(invoice_ids)
    if total == 0:
        print(f"No PDFs found in {pdf_dir}")
        return

    skipped = 0
    for i, invoice_id in enumerate(invoice_ids):
        pdf_path = pdf_dir / f"{invoice_id}.pdf"
        metadata_path = metadata_dir / f"{invoice_id}.json"

        if not metadata_path.exists():
            print(f"[{i + 1}/{total}] SKIP {invoice_id}: no metadata (re-run generate.py)")
            skipped += 1
            continue

        annotation = annotate_invoice(
            invoice_id=invoice_id,
            pdf_path=pdf_path,
            metadata_path=metadata_path,
            images_dir=images_dir,
            annotations_dir=annotations_dir,
            output_dir=output_dir,
            dpi=dpi,
        )
        n_labeled = sum(1 for tag in annotation.ner_tags if tag != "O")
        print(f"[{i + 1}/{total}] {invoice_id}: {len(annotation.ner_tags)} tokens, "
              f"{n_labeled} labeled")

    print(f"\nDone. {total - skipped} invoices annotated -> {annotations_dir}")
    if skipped:
        print(f"  {skipped} skipped (missing metadata — re-run generate.py to regenerate)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Annotate synthetic invoices with BIO tags for LayoutLMv3 training"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"DPI for PDF-to-image rendering (default: {DEFAULT_DPI})",
    )
    args = parser.parse_args()
    annotate_batch(output_dir=args.output, dpi=args.dpi)


if __name__ == "__main__":
    main()
