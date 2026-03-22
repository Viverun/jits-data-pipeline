# JITS Legal Dataset

A production-ready, deterministic pipeline for processing Indian legal judgments into structured, high-quality legal datasets, with comprehensive extraction, self-citation exclusion, statutory section detection, court normalization, and similarity analysis.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is not an official government or judicial release and does not constitute legal advice.

This repository contains the deterministic pipeline used to generate the JITS Legal Dataset. The current corpus build contains **3008** processed judgments, with **2377** release-ready rows exported in `train.jsonl`, with:

- clean text extraction and normalization
- rule-based metadata extraction and domain classification
- citation extraction with self-citation exclusion
- multi-act statutory section extraction
- IPC/CrPC to BNS/BNSS transition handling with temporal guardrails
- deterministic similarity graph construction and cluster refinement

All outputs are reproducible, auditable, and traceable to explicit rules.

## Repository And Dataset

- **GitHub repository:** pipeline code, audit logic, schemas, scripts, and reproducible processed outputs
- **Canonical public dataset:** [Hugging Face - Viverun/jits-legal-dataset](https://huggingface.co/datasets/Viverun/jits-legal-dataset)
- **Primary release artifact:** `train.jsonl` (published on Hugging Face)

The metrics below are computed from the current exported `train.jsonl` and processed JSON corpus in this repository.

## Current Release

Current GitHub release state: **v1.6**

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 3008 | Consolidated deterministic corpus |
| **Metadata Completeness** | 66.3% (1995/3008) | Completeness across court/date/case_number |
| **Missing Court** | 631 | Remaining UNKNOWN-court records |
| **Missing Decision Date** | 709 | Full-corpus missing dates |
| **Missing Case Number** | 998 | Full-corpus missing case numbers |
| **Unknown-Year IDs** | 321 | IDs with unresolved year |
| **Non-ISO Dates** | 0 | ISO normalization validated |
| **Duplicate IDs** | 0 | ID uniqueness validated |
| **Referential Integrity Errors** | 0 | Cross-record integrity validated |
| **Release Export Rows (`train.jsonl`)** | 2377 | UNKNOWN-court IDs excluded; artifact published on Hugging Face |
| **Release Missing Dates** | 382 | Rows still eligible for release |
| **Release Missing Case Numbers** | 635 | Rows still eligible for release |

### Release Quality Improvements

- canonical court codes in all regenerated IDs
- tribunal records correctly typed as `TR` instead of being folded into High Court IDs
- tighter line-based header parsing for cleaner `metadata.court` extraction
- pre-`2024-07-01` judgments excluded from inferred BNS mappings
- section overlap signals restored for similarity generation
- invalid export dates normalized to `null` so Hugging Face viewer/parquet generation works reliably

## Quick Start

### Installation

```bash
git clone https://github.com/Viverun/jits-data-pipeline.git
cd jits-data-pipeline
pip install -e .
```

### Run The Pipeline

```bash
legal-ai pipeline
legal-ai audit --type quality
python3 scripts/normalize_dataset.py
```

### Load The Public Export

```python
import json

with open("train.jsonl", encoding="utf-8") as f:
    first_record = json.loads(next(f))

print(first_record["judgment_id"])
print(first_record["metadata"]["court"])
print(first_record["classification"]["domain"])
print(first_record["extractions"]["sections"]["total"])
```

### Load A Processed Judgment Object

```python
import json
from pathlib import Path

path = Path("legal_ai_toolkit/data/judgments/IN-HC-ALL-2007-CR-25B3AC.json")
record = json.loads(path.read_text(encoding="utf-8"))

print(record["judgment_id"])
print(record["metadata"]["decision_date"])
print(record["statutory_transitions"][:2])
```

## Project Layout

```text
jits-data-pipeline/
├── legal_ai_toolkit/
│   ├── analytics/        # Audits and reporting
│   ├── classification/   # Deterministic domain classification
│   ├── clustering/       # Similarity graph and cluster refinement
│   ├── data/
│   │   ├── judgments/    # Processed unified judgment JSONs
│   │   └── raw/          # Raw text corpus
│   ├── extraction/       # Metadata, sections, transitions, citations
│   ├── pipeline/         # End-to-end processing steps
│   └── utils/            # IDs, mappings, helpers
├── annotations/          # Similarity artifacts and clusters
├── scripts/              # Export, rebuild, and upload helpers
├── train.jsonl           # Generated local export (published on Hugging Face)
├── DATASET_CARD.md       # Hugging Face dataset card source
└── README.md             # Repository overview
```

## Reproducibility

The pipeline is deterministic:

- no probabilistic labeling is used for the shipped dataset
- identical inputs produce identical outputs for a given pipeline revision
- release artifacts can be regenerated from the raw corpus and committed rules
- audit logic lives in `legal_ai_toolkit/analytics/audit.py`

A typical verification flow is:

```bash
legal-ai pipeline
legal-ai audit --type quality
python3 scripts/normalize_dataset.py
```

## Release Notes

### v1.6 (2026-03-22)

- corpus rebuilt through `consolidate` and `train.jsonl` regenerated
- full corpus now at `3008` processed judgments
- release export now at `2377` rows after UNKNOWN-court exclusion
- missing/unknown court reduced to `631` from `646` in the prior clean build
- metadata extractor improved with deeper-header fallback and safer embedded-caption matching
- Delhi QR/order-portal, Orissa signed-location, and Andhra proceedings-sheet recoveries added
- case-number support widened (`MA`, `First Appeal`, `C.Misc.`, `CR. WJC`)
- verification green: metadata tests `63/63`, normalize-dataset tests `3/3`, pipeline-runner tests `2/2`

### v1.5 (2026-03-19)

**Breaking:** `744` judgment IDs changed from `v1.4`.

- court codes corrected across the corpus
- tribunal records separated into `TR` identifiers, including `CAT`
- metadata court extraction tightened to avoid header overmatch noise
- refined clusters updated to `23`
- Hugging Face export normalized malformed decision dates to `null` for viewer compatibility

### v1.4 (2026-03-19)

**Breaking:** `397` judgment IDs changed from `v1.3`.

- similarity signal extraction fixed for real section overlap
- temporal safeguards applied to pre-BNS judgments
- classifier pipeline switched to the strengthened zero-ML path
- top-level `statutory_transitions` written consistently

## Citation

If you use this dataset or pipeline, please cite:

```bibtex
@dataset{jits_legal_dataset_2026,
  author = {Viverun},
  title = {JITS Legal Dataset},
  year = {2026},
  publisher = {Hugging Face},
  version = {1.5},
  url = {https://huggingface.co/datasets/Viverun/jits-legal-dataset}
}
```

Or:

```text
Viverun (2026). JITS Legal Dataset (v1.6). Hugging Face.
```

## License

Licensed under [Apache-2.0](LICENSE).

## Community And Feedback

If you find noise, schema drift, or extraction errors, please open an issue:

- [GitHub Issues](https://github.com/Viverun/jits-data-pipeline/issues)

Contributions to the deterministic rules, mappings, audits, and documentation are welcome.
