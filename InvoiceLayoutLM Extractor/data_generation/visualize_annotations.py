"""Debug script: draws BIO-labeled bounding boxes on invoice images."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_OUTPUT_DIR = Path(__file__).parent / "output"

# Color per entity label (R, G, B)
_ENTITY_COLORS: dict[str, tuple[int, int, int]] = {
    "item_description": (52,  152, 219),   # blue
    "quantity":         (39,  174,  96),   # green
    "unit_price":       (230, 126,  34),   # orange
    "line_total":       (231,  76,  60),   # red
    "tax":              (155,  89, 182),   # purple
    "position":         (26,  188, 156),   # teal
    "article_number":   (241, 196,  15),   # yellow
}
_FALLBACK_COLOR = (127, 140, 141)          # grey for unknown labels
_BOX_ALPHA = 80                            # fill transparency (0-255)
_FONT_SIZE = 11


def _entity_from_tag(tag: str) -> str | None:
    """Extract entity name from a BIO tag, e.g. 'B-unit_price' → 'unit_price'."""
    if tag.startswith("B-") or tag.startswith("I-"):
        return tag[2:]
    return None


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def visualize(annotation_path: Path, images_dir: Path, out_path: Path) -> None:
    annotation = json.loads(annotation_path.read_text(encoding="utf-8"))

    image_path = images_dir / Path(annotation["image_path"]).name
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_main = ImageDraw.Draw(overlay)

    font = _load_font(_FONT_SIZE)

    words: list[str] = annotation["words"]
    bboxes: list[list[int]] = annotation["bboxes"]
    ner_tags: list[str] = annotation["ner_tags"]

    for word, bbox, tag in zip(words, bboxes, ner_tags):
        entity = _entity_from_tag(tag)
        if entity is None:
            continue

        color = _ENTITY_COLORS.get(entity, _FALLBACK_COLOR)
        r, g, b = color

        # Denormalize bbox from 0-1000 to pixel coordinates
        x0 = round(bbox[0] / 1000 * width)
        y0 = round(bbox[1] / 1000 * height)
        x1 = round(bbox[2] / 1000 * width)
        y1 = round(bbox[3] / 1000 * height)

        # Semi-transparent fill
        draw_overlay.rectangle([x0, y0, x1, y1], fill=(r, g, b, _BOX_ALPHA))
        # Solid border
        draw_main.rectangle([x0, y0, x1, y1], outline=(r, g, b, 255), width=1)

        # Label above the box (only for B- tags to avoid clutter)
        if tag.startswith("B-"):
            label_text = entity
            text_bbox = font.getbbox(label_text)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            label_x = x0
            label_y = max(0, y0 - text_h - 2)
            # Small background pill for readability
            draw_main.rectangle(
                [label_x, label_y, label_x + text_w + 4, label_y + text_h + 2],
                fill=(r, g, b, 220),
            )
            draw_main.text((label_x + 2, label_y + 1), label_text, fill=(255, 255, 255, 255), font=font)

    # Merge overlay onto image
    combined = Image.alpha_composite(image, overlay).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(str(out_path))


def visualize_batch(output_dir: Path, invoice_ids: list[str] | None = None) -> None:
    annotations_dir = output_dir / "annotations"
    images_dir = output_dir / "images"
    debug_dir = output_dir / "debug"

    paths = sorted(annotations_dir.glob("invoice_*.json"))
    if invoice_ids:
        paths = [p for p in paths if p.stem in invoice_ids]

    if not paths:
        print(f"No annotation files found in {annotations_dir}")
        return

    for i, ann_path in enumerate(paths):
        out_path = debug_dir / ann_path.name.replace(".json", ".png")
        visualize(ann_path, images_dir, out_path)
        print(f"[{i + 1}/{len(paths)}] {ann_path.stem} -> {out_path}")

    print(f"\nDone. Debug images saved to {debug_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualize BIO annotations by drawing labeled bounding boxes on invoice images"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        metavar="INVOICE_ID",
        help="Only visualize specific invoice IDs, e.g. --ids invoice_0000 invoice_0001",
    )
    args = parser.parse_args()
    visualize_batch(output_dir=args.output, invoice_ids=args.ids)


if __name__ == "__main__":
    main()
