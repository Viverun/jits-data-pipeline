# JITS Legal Dataset

A production-ready, deterministic pipeline for processing Indian legal judgments into structured, high-quality legal datasets, with comprehensive extraction, self-citation exclusion, statutory section detection, court normalization, and similarity analysis.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is not an official government or judicial release and does not constitute legal advice.

This repository contains the deterministic pipeline used to generate the JITS Legal Dataset. The current corpus build contains **3008** processed judgments, with **2181** release-ready rows exported in `train.jsonl`, with:

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

Current GitHub release state: **v1.8** (pipeline). The published dataset artifact is
still **v1.7** — `v1.8` changes the pipeline only and does not rebuild the corpus, so
the metrics below are unchanged.

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 3008 | Consolidated deterministic corpus |
| **Metadata Completeness** | 67.4% (2027/3008) | Completeness across court/date/case_number |
| **Missing Court** | 753 | Remaining UNKNOWN-court records |
| **Missing Decision Date** | 527 | Full-corpus missing dates |
| **Missing Case Number** | 1108 | Full-corpus missing case numbers |
| **Unknown-Year IDs** | 238 | IDs with unresolved year in full corpus |
| **Non-ISO Dates** | 0 | ISO normalization validated |
| **Duplicate IDs** | 0 | ID uniqueness validated |
| **Referential Integrity Errors** | 0 | Cross-record integrity validated |
| **Release Export Rows (`train.jsonl`)** | 2181 | UNKNOWN-court and unknown-year IDs excluded; artifact published on Hugging Face |
| **Release Missing Dates** | 154 | Rows still eligible for release |
| **Release Missing Case Numbers** | 607 | Rows still eligible for release |
| **Similarity Edges** | 802,552 | Rebuilt deterministic graph |
| **Refined Clusters** | 77 | Post-rebuild domain-pure clusters |

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
uv sync
source .venv/bin/activate
```

This project is pinned to Python 3.10 (`.python-version`) for compatibility with the pinned `torch`/`tokenizers` versions; `uv` will download that interpreter automatically if it isn't already installed. Add `--extra dev` to also install the dev/test tooling from `requirements-dev.txt`. Activating the environment puts `legal-ai` on `PATH` directly (no `uv run` prefix needed); alternatively, prefix each command below with `uv run` without activating.

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

### v1.8 (2026-08-16)

Pipeline-only release. No corpus rebuild ships here, so the dataset metrics above
and the published Hugging Face artifact remain at `v1.7`.

- **determinism fixes.** similarity edge generation, cluster centroid selection, and
  cluster refinement no longer depend on set iteration order, and pipeline file
  iteration is sorted so ID collisions resolve the same way every run. verified
  byte-identical artifacts across `PYTHONHASHSEED` values; previously refined-cluster
  *membership* varied between runs on identical inputs
- removed nested-quantifier backtracking from the case-number header pattern
  (identical matches over `16,638` real header lines)
- section extractor gains an act-presence gate and a compiled-pattern cache
  (identical output over `2,217` judgments)
- high-court location rules precompiled behind a substring gate
  (identical output over `163,252` header segments)
- similarity candidate pairs built from an inverted index instead of all-pairs
  enumeration; on a `2,215`-judgment corpus this evaluated `539,590` of `2,452,005`
  possible pairs with the edge set preserved
- statutory section extraction widened from `9` acts to `19`, adding NI Act, CPC,
  Arbitration, MV Act, Companies Act, IBC, PC Act, Income Tax, Hindu Marriage, and
  SARFAESI. on a `2,215`-judgment sample rebuild this raised section coverage from
  `50.7%` to `66.0%` of cases; the shipped corpus is unchanged until the next rebuild
- added `pyproject.toml`, `uv.lock`, and a `.python-version` pin of `3.10`. the repo
  previously carried no build configuration, so the documented `pip install -e .`
  could not succeed
- verification green: full suite `87/87`

### v1.6 (2026-03-22)

- corpus rebuilt through `consolidate` and `train.jsonl` regenerated
- full corpus now at `3008` processed judgments
- release export now at `2377` rows after UNKNOWN-court exclusion
- missing/unknown court reduced to `631` from `646` in the prior clean build
- metadata extractor improved with deeper-header fallback and safer embedded-caption matching
- Delhi QR/order-portal, Orissa signed-location, and Andhra proceedings-sheet recoveries added
- case-number support widened (`MA`, `First Appeal`, `C.Misc.`, `CR. WJC`)
- verification green: metadata tests `63/63`, normalize-dataset tests `3/3`, pipeline-runner tests `2/2`

### v1.7 (2026-03-22)

- added strict release gate to block `0000` year IDs in export and upload
- deepened decision-date fallback and year recovery in metadata and ID regeneration
- fixed metadata case-number regex backtracking stalls (previously stuck around `42%`)
- reran pipeline from metadata through consolidate, then rebuilt similarity and cluster artifacts
- referential integrity restored to `0` errors after similarity/cluster rebuild
- full corpus now reports `238` unknown-year IDs (down from `321`)
- release export now `2181` rows with `0` unknown-year IDs

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
  version = {1.7},
  url = {https://huggingface.co/datasets/Viverun/jits-legal-dataset}
}
```

Or:

```text
Viverun (2026). JITS Legal Dataset (v1.7). Hugging Face.
```

## License

Licensed under [Apache-2.0](LICENSE).

## Community And Feedback

If you find noise, schema drift, or extraction errors, please open an issue:

- [GitHub Issues](https://github.com/Viverun/jits-data-pipeline/issues)

Contributions to the deterministic rules, mappings, audits, and documentation are welcome.
