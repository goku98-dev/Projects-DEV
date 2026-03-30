# Fine-Tuning LayoutLMv3 for Table Entity Extraction in Invoices Using Synthetic Data

## Problem Statement

Most work on automated invoice processing deals with extracting header-level fields — things like the invoice number, date, vendor name, or total amount. While this is useful, it ignores a large part of what makes an invoice informative: the table of individual line items. These tables contain item descriptions, quantities, unit prices, tax rates, and line totals, all of which are needed for tasks like automated bookkeeping or procurement matching. The challenge is that invoice tables differ a lot in practice. Columns can appear in different orders, tables can sit anywhere on the page, and the number of columns varies. A model that simply memorises where things tend to appear spatially will fail when faced with an unfamiliar layout. What we need is a model that actually understands the semantics of table content.

## Current Research

Limam et al. (2023) recently published FATURA, a synthetic invoice dataset with 10,000 images spread across 50 different layouts. The dataset includes bounding-box annotations for 24 semantic classes and has become a useful benchmark for document layout analysis and key-value extraction on invoices. The authors showed that generating invoices synthetically from templates is a viable way to build large, privacy-compliant training sets. That said, FATURA focuses on document-level fields — seller information, dates, totals, and so on. It does not provide annotations for individual rows or cells inside the invoice table. This means models trained on it cannot extract structured line-item data. Other publicly available invoice datasets share this limitation, leaving table-level extraction largely unaddressed.

## Proposal

We want to fine-tune LayoutLMv3 to extract entities from invoice tables, specifically the individual positions and their attributes. Since no suitable dataset exists for this task, we plan to build one ourselves using a template-based generation approach, loosely inspired by how FATURA was constructed, but with a focus on table content. The idea is to create a set of parameterised invoice templates where we can control things like column order, number of columns, table position on the page, and visual styling. We then fill these templates with plausible commercial data — product names, quantities, prices — and automatically produce token-level bounding-box annotations for every table cell. This gives us full control over the data, which is important not just for training but also for designing targeted evaluation experiments. Long-term, the fine-tuned model is meant to work as the table-extraction component in a broader invoice processing pipeline, complementing existing models that handle header fields.

## Dataset

We plan to generate roughly 5,000 to 10,000 invoice images from 30 to 50 templates. Templates will be rendered programmatically using HTML/CSS or a PDF library. To ensure diversity, we will vary the number of columns (between 3 and 8), the order in which columns appear, the vertical position of the table, whether sub-total or tax rows are included, and visual properties like fonts, borders, and background colours. Each table cell gets annotated with its bounding box, text content, and a semantic label such as item_description, quantity, unit_price, line_total, or tax. On top of the synthetic data, we intend to manually annotate a small set of real invoices to test how well the model transfers to authentic documents.

## Models

Our main model is LayoutLMv3, a multimodal transformer from Microsoft that combines text, 2D positional information, and image features. We will set it up as a token classification task with BIO tagging, where each token receives a label indicating which table entity it belongs to. As a baseline, we plan to compare against a text-only model (a BERT-based NER setup without any layout input) to see how much the spatial and visual signals actually contribute.

## Evaluation

We will measure entity-level Precision, Recall, and F1 on a held-out test split, but the more interesting part of the evaluation concerns robustness. Because we control the data generation, we can construct specific test scenarios: one where the column order is different from anything seen during training, one where the table is placed in an unusual position on the page, and one using entirely new template layouts. Comparing performance across these splits will tell us whether the model has learned to recognise table entities by their semantic context or whether it is just relying on spatial patterns. We will also report results on the small set of manually annotated real invoices to get a sense of how the model holds up outside of synthetic data.

## Reference

Limam, M., Dhiaf, M., & Kessentini, Y. (2023). FATURA: A Multi-Layout Invoice Image Dataset for Document Analysis and Understanding. arXiv preprint arXiv:2311.11856.
