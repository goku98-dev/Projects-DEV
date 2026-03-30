# Data Generation

This folder contains the code for generating synthetic invoices. The goal is to produce a large number of realistic invoices with varying data and layouts.

## Setup

### Local (venv)

- Python 3.13
- create an environment for data generation and install the required packages

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Docker

```bash
docker build -t hcnlp-data-gen .
../scripts/run_data_gen_docker.sh python generate.py -n 500 -o /data
../scripts/run_data_gen_docker.sh python annotate.py -o /data
../scripts/run_data_gen_docker.sh python visualize_annotations.py -o /data
```

### Apptainer

Build and run directly on the cluster (run from `data_generation/`):

```bash
apptainer build --fakeroot data_gen.sif data_gen.def
apptainer run --bind /cluster/data:/data data_gen.sif generate.py -n 1000 -o /data
```

## How to Run

```bash
# Generate 10 invoices (default)
python generate.py

# Generate a specific number of invoices
python generate.py -n 500

# Use a specific locale
python generate.py -n 20 --locale en_US
```

Output is saved to:
- `output/pdfs/` — PDF files
- `output/html/` — HTML files (for debugging)
- `output/metadata/` — ground truth JSON per invoice (column layout + cell values)

```bash
# Annotate all generated invoices
python annotate.py
```

Annotation output:
- `output/images/` — PNG renders of each PDF page
- `output/annotations/` — BIO-tagged JSON per invoice (LayoutLMv3 format)

## Pipeline

### Generation (`generate.py`)

1. Selects a layout template from `templates/` and generates random invoice data
2. Renders to HTML via Jinja2, then to PDF via Playwright/Chromium
3. Saves a `metadata/invoice_XXXX.json` with the ground truth column layout and formatted cell values

### Annotation (`annotate.py`)

1. Renders the PDF to a PNG image (via PyMuPDF)
2. Extracts embedded word tokens with bounding boxes directly from the PDF (normalized 0–1000) — no OCR, so no tokens are ever missed
3. Matches tokens against the known cell values from metadata using exact matching
4. Assigns BIO labels; unmatched tokens get `O`
5. Saves `annotations/invoice_XXXX.json` in LayoutLMv3-compatible format

### Entity labels

Table cell values are labeled with BIO tags. Target entities:

| Field | Entity label |
|---|---|
| Description | `item_description` |
| Quantity | `quantity` |
| Unit price | `unit_price` |
| Line total | `line_total` |
| Tax rate | `tax` |
| Position | `position` |
| Article number | `article_number` |

All other tokens (invoice header, addresses, totals, footer) receive label `O`.
