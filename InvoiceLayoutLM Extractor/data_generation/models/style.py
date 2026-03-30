from dataclasses import dataclass


@dataclass
class Style:
    """Visual styling parameters for an invoice template."""
    font_family: str
    font_size_pt: int
    header_bg_color: str
    header_text_color: str
    border_color: str
    row_alt_bg_color: str
    table_border_style: str  # e.g. "solid", "none", "dotted"
