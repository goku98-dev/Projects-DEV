# HCNLP-Project: What It Currently Does

## High-Level Summary

This repository currently implements a synthetic invoice data generation and annotation pipeline. Its working code is concentrated in `data_generation/`. The project can:

- generate fake but structured invoice data,
- render that data into visually varied invoice PDFs via HTML templates,
- save exact ground-truth metadata for the line-item table,
- extract word tokens and bounding boxes directly from the generated PDFs,
- assign BIO tags for table-related entities, and
- optionally draw the labels back onto page images for debugging.

The second half of the stated project goal, fine-tuning LayoutLMv3 on the generated data, is not implemented yet in this repository. `model_finetuning/` currently contains only a short README describing the intended direction.

## Repository Structure

- `README.md`
  Brief top-level project summary.
- `docs/proposal.md`
  Research/project proposal describing the intended LayoutLMv3 study and robustness evaluation.
- `data_generation/`
  The actual implemented system.
- `model_finetuning/`
  Placeholder folder with no training code yet.

## What The Implemented System Is For

The implemented pipeline is designed to create training data for invoice table extraction. Instead of annotating real invoices by hand, it programmatically creates invoices and keeps the exact source values used in each table cell. That lets the project generate token-level labels automatically after rendering.

The emphasis is on line-item extraction, not full-document extraction. The annotations target tokens inside the invoice table such as:

- `item_description`
- `quantity`
- `unit_price`
- `line_total`
- `tax`
- `position`
- `article_number`

All non-table content such as seller information, invoice header fields, totals labels, and footer text stays labeled as `O`.

## Current End-to-End Workflow

The implemented workflow has three main stages plus one debugging helper:

1. Create invoice templates.
2. Generate invoices as HTML, PDF, and metadata.
3. Annotate PDF tokens with BIO labels.
4. Visualize annotations on top of rendered images.

In practice, the repository already contains 30 generated templates in `data_generation/templates/`, so template generation is a preparation step rather than a required runtime step for normal use.

## Stage 1: Template Generation

`data_generation/template_generator.py` creates invoice layout templates as Jinja2 HTML files.

### What it varies

The generator builds templates by combining reusable layout components:

- header style,
- address block arrangement,
- table style,
- table vertical position,
- table width,
- totals section layout,
- footer style.

The combinations are assembled into complete HTML templates with inline CSS. The resulting files are written as:

- `data_generation/templates/layout_000.html`
- ...
- `data_generation/templates/layout_029.html`

### Why this matters

This is how the project introduces layout diversity. The invoices are not rendered from one fixed design. Instead, the code varies major structural features so later models do not only see one table shape or one page composition.

### Important implementation detail

`generate_templates(count=30, seed=42)` randomly samples from a large Cartesian product of layout components and writes 30 templates. The repository currently already contains those 30 generated template files.

## Stage 2: Synthetic Invoice Generation

`data_generation/generate.py` is the main batch entry point for creating invoices.

### What it does per invoice

For each invoice, the script:

1. creates fake invoice content,
2. chooses a subset and order of line-item table columns,
3. chooses one template from the template inventory,
4. renders the invoice as HTML,
5. converts the HTML to PDF using Playwright + Chromium,
6. saves the HTML for inspection, and
7. saves metadata describing the exact rendered table values.

### Files it produces

By default it writes into `data_generation/output/`:

- `pdfs/` for final PDF invoices,
- `html/` for debug HTML,
- `metadata/` for ground-truth JSON per invoice.

There is currently no `data_generation/output/` directory checked into the repo, which means the repository contains code and templates but not generated sample datasets.

### How invoice content is synthesized

The fake data is built in `data_generation/data_generator.py`.

#### Locale support

The generator supports these locale profiles:

- `de_DE`
- `en_US`
- `en_GB`
- `fr_FR`
- `de_CH`
- `de_AT`

Each locale profile controls:

- Faker locale,
- invoice date formatting,
- invoice currency,
- allowed tax rates.

If the user passes `--locale random`, the code randomly selects one of those locale configurations for each generated invoice.

#### Invoice structure

Each invoice contains:

- invoice number,
- invoice date,
- due date,
- seller address,
- buyer address,
- 3 to 8 line items,
- currency and locale,
- a randomized visual style,
- a randomized number-formatting scheme,
- payment information such as bank, IBAN, BIC, and payment terms.

#### Line items

Each line item contains:

- `position`
- `description`
- `quantity`
- `unit_price`
- `tax_rate`
- optional `article_number`

From these, computed properties derive:

- `line_total = quantity * unit_price`
- `tax_amount = line_total * tax_rate`

These computed values are not stored separately in the line-item dataclass fields, but they are used during rendering and metadata creation.

#### Style randomization

The generator also randomizes presentation details such as:

- font family,
- base font size,
- header color,
- border color,
- alternating row background color,
- table border style.

This style object is passed into the HTML template so the same structural template can still look different between invoices.

#### Number formatting

Currency and numeric formatting are not hardcoded. `NumberFormat` controls:

- decimal separator,
- thousands separator,
- currency symbol,
- whether the currency symbol appears before or after the number.

That means the same numeric value may be rendered differently depending on locale/format choice, for example with `,` vs `.` decimals or with the currency symbol before vs after the amount.

### How columns are chosen

Column selection logic lives in `data_generation/renderer.py`.

The table always includes these required fields:

- `description`
- `quantity`
- `unit_price`
- `line_total`

Optional fields may also be included:

- `position`
- `tax_rate`
- `article_number`

The optional columns are added probabilistically, and then the final column order is shuffled. `article_number` is excluded if the generated invoice has no article numbers in its line items.

This means the table schema itself changes across documents, not only the styling.

### How column headers vary

The code uses locale-aware synonym lists for each field. For example, `description` might appear as variants such as `Description`, `Item`, `Beschreibung`, or `Désignation` depending on the invoice language and random selection.

This improves semantic diversity by preventing the training data from using one fixed header name for each concept.

### Template scheduling across a batch

`generate.py` does not choose templates completely independently each time. It first builds a schedule that cycles through all templates enough times to cover the requested invoice count, then shuffles that schedule.

The effect is:

- all templates are used roughly equally,
- the sequence still looks random,
- there is no strong bias toward early template files.

### Metadata output

For each generated invoice, the code writes a metadata JSON file containing:

- invoice id,
- invoice locale,
- chosen template name,
- selected columns with labels and entity labels,
- formatted line-item cell values exactly as rendered.

This metadata is the core ground truth used later for annotation. Importantly, it stores already formatted cell strings, not just raw numbers. That matters because the labeler later matches PDF tokens against the rendered strings.

## Stage 3: Annotation

`data_generation/annotate.py` converts generated PDFs into LayoutLMv3-style token annotations.

### Main idea

Because the PDFs are generated programmatically, the script does not run OCR. Instead, it extracts embedded text directly from the PDF using PyMuPDF.

This is a major design decision in the current implementation:

- it avoids OCR errors,
- it keeps word coverage effectively perfect for these synthetic documents,
- it gives bounding boxes directly from the PDF text layer.

### What the annotation step produces

For each invoice PDF with matching metadata, the script writes:

- a rendered PNG image of the PDF page into `images/`,
- an annotation JSON into `annotations/`.

The annotation JSON contains:

- `id`
- `image_path`
- `words`
- `bboxes`
- `ner_tags`

This structure is compatible with token-classification training workflows for LayoutLMv3-style models.

### Bounding box format

The code normalizes PDF word coordinates into the 0 to 1000 box convention commonly used by LayoutLM-family models:

- `[x0, y0, x1, y1]`

### Token extraction details

`extract_words()` reads words from `page.get_text("words")`, trims blanks, normalizes their coordinates, and then applies one cleanup step:

- `_merge_hyphen_splits()`

This merges cases where a token was visually broken across lines at a hyphen, such as a wrapped word fragment in a narrow table cell. Without this, exact string matching against metadata would fail more often.

### How labeling works

The labeler uses metadata-driven exact matching rather than layout heuristics alone.

For each line item row:

1. It tries to find the description tokens first.
2. If found, it uses the description’s vertical position to define a row-specific `y` band.
3. It then searches for the remaining cell values only within that row band.
4. Matching tokens are tagged with BIO labels.

This is a smart constraint in the current implementation because values like `3`, `19%`, or `100.00` might also appear elsewhere in the document, such as in headers or totals. The row anchor reduces accidental matches outside the table.

### Matching behavior

Matching is based on:

- tokenized word sequences,
- lowercased normalized text,
- exact sequence comparison,
- skipping tokens that were already labeled.

If the description cannot be matched, the code falls back to unconstrained matching for the remaining fields. That makes the annotator more tolerant even if the row anchor fails.

### Output semantics

The current annotation system labels only table cell content. It does not label:

- invoice number,
- dates,
- seller or buyer fields,
- subtotal/tax/total summary values,
- footer bank/payment text.

Those tokens remain `O`.

## Stage 4: Annotation Visualization

`data_generation/visualize_annotations.py` is a debugging utility.

It reads an annotation JSON and corresponding page image, then draws:

- semi-transparent colored boxes over labeled tokens,
- solid box outlines,
- entity names above `B-` tokens.

Each entity type has a distinct color. The output is saved to `output/debug/`.

This script is useful for visually checking whether the automatic labeling aligned with the rendered table as expected.

## Data Models

The repository uses small dataclasses under `data_generation/models/` to represent invoice content cleanly:

- `Address`
- `LineItem`
- `Invoice`
- `NumberFormat`
- `PaymentInfo`
- `Style`

These dataclasses keep the generation and rendering code readable and make the flow explicit:

- `data_generator.py` creates instances,
- `renderer.py` formats them into HTML/PDF,
- `generate.py` serializes selected ground truth,
- `annotate.py` turns rendered pages back into token labels.

## Current Runtime Dependencies

The data-generation pipeline depends mainly on:

- `Faker` for synthetic business data,
- `Jinja2` for template rendering,
- `playwright` for HTML-to-PDF rendering in Chromium,
- `PyMuPDF` for PDF text extraction and page rendering,
- `Pillow` for image handling and debug overlays.

The code is set up for local Python usage and containerized execution via Docker or Apptainer.

## What Is Implemented Versus Planned

### Implemented now

- synthetic invoice content generation,
- locale variation,
- style variation,
- structural layout variation through template files,
- randomized column subsets and column orders,
- HTML rendering,
- PDF rendering,
- metadata export,
- token extraction from PDFs,
- automatic BIO annotation,
- annotation visualization.

### Planned but not implemented here yet

- LayoutLMv3 fine-tuning code,
- dataset loading/training scripts,
- evaluation scripts,
- baseline BERT NER implementation,
- robustness experiments on unseen layouts/column orders,
- any real-invoice annotation workflow.

The proposal and README describe those later stages, but the current repository contents stop at dataset creation and annotation.

## Important Design Characteristics Of The Current System

### 1. It is synthetic-first

The pipeline is fully synthetic. It does not currently ingest or process real invoices.

### 2. It relies on perfect text extraction

Because the documents are machine-generated PDFs, the annotation step assumes direct PDF text extraction is available and reliable. This is appropriate for synthetic data generation, but it is not the same problem as OCR on scanned real documents.

### 3. It targets table semantics, not full invoice understanding

The labels are focused on line-item table content. The rest of the document is mainly context and visual diversity.

### 4. It intentionally varies both content and layout

The diversity comes from several independent sources:

- fake business content,
- locale differences,
- numeric formatting differences,
- optional columns,
- shuffled column order,
- multiple template structures,
- randomized styling.

### 5. It preserves exact ground truth through metadata

The key mechanism making auto-annotation possible is that the generator saves the exact rendered values for every selected line-item field. The annotator then matches PDF tokens back to that ground truth.

## What Running The Project Would Do Today

If you run the implemented pipeline today, the practical result is:

1. generate a batch of synthetic invoices as PDFs and HTML,
2. save per-invoice metadata containing table ground truth,
3. render invoice pages to images,
4. create token-level BIO annotations for line-item entities,
5. optionally render labeled debug images.

That means the repository currently functions as a dataset factory for invoice table extraction experiments.

## Current Limitations

Based on the code currently present, some notable limitations are:

- only a single-page invoice page is assumed during annotation (`doc[0]`),
- annotation is based on exact matching of rendered strings,
- only line-item table entities are labeled,
- templates themselves are generated ahead of time and then reused,
- no training, evaluation, or inference pipeline exists yet,
- no generated sample dataset is committed in the repository right now.

## Bottom Line

Right now, this project is best understood as a synthetic invoice dataset generation and auto-annotation system intended to feed a later LayoutLMv3 fine-tuning workflow.

The repository already does the difficult upstream work of:

- creating diverse invoice layouts,
- rendering them into realistic PDFs,
- preserving exact table ground truth, and
- converting that into LayoutLMv3-style BIO annotations.

What it does not yet do is train or evaluate a model. The current implementation ends at producing the training-ready synthetic dataset.
