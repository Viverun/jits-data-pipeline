# JITS Legal Dataset

**The only major open Indian legal dataset with citation-graph extraction, statutory section tagging, and IPC/CrPC→BNS/BNSS transition mapping** — verified against the schemas of every comparable open dataset in this space (including one at 17.1M rows), which provide raw text and/or task labels but not structured legal extraction.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is not an official government or judicial release and does not constitute legal advice.

This repository contains the deterministic pipeline used to generate the JITS Legal Dataset. The current corpus build contains **14678** processed judgments, with **14037** release-ready rows exported in `train.jsonl`.

### What Makes This Different

- **Citation-graph extraction with self-citation exclusion** — not a raw text dump: an actual graph of what each judgment cites, with a judgment's references to itself filtered out so citation counts aren't inflated.
- **Multi-act statutory section tagging** — every invoked section (IPC, CrPC, Evidence Act, and 16 more) linked to its parent act, not left buried in prose.
- **IPC/CrPC → BNS/BNSS transition mapping** — India's 2023–24 criminal-code overhaul mapped per judgment, with temporal guardrails so pre-`2024-07-01` judgments never get an inferred BNS mapping they can't have.
- **Zero-ML, fully deterministic pipeline** — every field traces to an explicit, auditable rule. Re-run the pipeline on the same input and get byte-identical output; nothing here is a model's guess.
- **Court/domain classification and similarity clustering** on top of the above, all reproducible from source.

All outputs are reproducible, auditable, and traceable to explicit rules.

**Attribution:** Judgment texts were sourced from [Indian Kanoon](https://indiankanoon.org/), an independent legal search engine; this project is not affiliated with or endorsed by Indian Kanoon.

## Repository And Dataset

- **GitHub repository:** pipeline code, audit logic, schemas, scripts, and reproducible processed outputs
- **Canonical public dataset:** [Hugging Face - Viverun/jits-legal-dataset](https://huggingface.co/datasets/Viverun/jits-legal-dataset)
- **Primary release artifact:** `train.jsonl` (published on Hugging Face)

The metrics below are computed from the current exported `train.jsonl` and processed JSON corpus in this repository.

## Current Release

Current release: **v1.14** (pipeline and dataset).

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 14678 | |
| **Release Export Rows (`train.jsonl`)** | 14037 | UNKNOWN-court and unknown-year IDs excluded |
| **Metadata Accuracy** | 93.3% (13699/14678) | Court + date + case_number all present |
| **Missing Court / Date / Case Number** | 525 / 476 / 4669 | Full-corpus counts |
| **Duplicate IDs** | 0 | |
| **Referential Integrity Errors** | 0 | Rebuilt from scratch against the current corpus |
| **Similarity Edges / Refined Clusters** | 18,969,008 / 547 | **Freshly rebuilt** against the full 14,678-judgment corpus |

**Release-export field completeness:** court 100.0%, decision_date 97.6%, case_number 69.8% (digit-validated) — mean 89.1%, strict all-three-present 67.7%.

### Known Issues

- 525 records have no resolvable court — mostly missing headers at the source that even the fixed downloader can't recover.
- A handful of exact-duplicate downloads (same case, different source filename) are detected and excluded automatically rather than merged.

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

| Version | Date | Summary |
|---------|------|---------|
| **v1.14** | 2026-09-04 | +4,649 documents (corpus 10029→14678, `train.jsonl` 9517→14037) — completes the acquisition run started in v1.10. Rebuilt similarity/clusters again against the full corpus (18.97M edges, 547 clusters); the rebuild's `CentroidClusteter` step loaded the entire edge file into a list before filtering, which OOM-killed the process at ~19M edges on a 14 GB machine — fixed to stream and filter the file directly instead of materializing it, with a regression test. |
| **v1.13** | 2026-09-03 | +3,024 documents (corpus 7005→10029, `train.jsonl` 6686→9517). Fixed two latent bugs in similarity signal extraction (silently dropped all statutory-section signals, crashed on transitions) found while making the rebuild possible; fixed the downloader to leave a query pending on network failure instead of falsely marking it done (a DNS outage had burned through ~3,200 queries silently). Similarity graph and clusters rebuilt from scratch against the full corpus: 9.1M edges, 380 refined clusters, referential integrity errors 36→0. |
| **v1.12** | 2026-09-02 | +2,344 documents via the fixed downloader (zero errors/duplicates, ~9% unknown-court vs v1.10's ~49%). Corpus 4661→7005, `train.jsonl` 4451→6686. Tried 8 parallel download workers to speed this up — reverted immediately, indiankanoon.org rate-limits by IP and blocks concurrent bursts within seconds. |
| **v1.11** | 2026-09-02 | Found and fixed the real cause of v1.10's unknown-court records: the downloader silently dropped `<h2>/<h3>/<pre>/<blockquote>` tags, discarding court name, title, and cause-title text on many pages. Re-fetched and reprocessed the 1,216 affected documents; 1,128 (93%) recovered. `train.jsonl` 3324→4451. |
| **v1.10** | 2026-09-02 | Processed a 2,502-document backlog that had never run through the pipeline (56 exact duplicates skipped). Fixed two catastrophic-backtracking regex bugs that could hang extraction on ordinary text. Applied a pending `case_number` fix corpus-wide (50 values corrected). Corpus 3008→4661, `train.jsonl` 2215→3324. |
| **v1.9** | 2026-08-16 | Pipeline-only release (no corpus rebuild): determinism fixes for similarity/clustering, a ReDoS fix in the case-number pattern, statutory sections widened 9→19 acts, completeness now reported per-field, fixed `case_number` extraction matching letters as digits under `re.I`. |
| **v1.8** | 2026-03-23 | Added a targeted court fallback for Haryana CWP filings; regenerated `train.jsonl` (2215 rows). |
| **v1.7** | 2026-03-22 | Added a release gate blocking unknown-year IDs, fixed case-number regex stalls, rebuilt similarity/clusters (0 integrity errors). 2181 release rows. |
| **v1.6** | 2026-03-22 | Corpus rebuilt to 3008 judgments / 2377 release rows; metadata extractor improvements (deeper header fallback, widened case-number forms). |
| **v1.5** | 2026-03-19 | **Breaking:** 744 IDs changed. Court codes corrected, tribunal records separated into `TR`, malformed decision dates normalized to `null` for the HF viewer. |
| **v1.4** | 2026-03-19 | **Breaking:** 397 IDs changed. Fixed similarity section-overlap signal, added temporal BNS safeguards, switched to the strengthened zero-ML classifier. |

## Citation

If you use this dataset or pipeline, please cite:

```bibtex
@dataset{jits_legal_dataset_2026,
  author = {Viverun},
  title = {JITS Legal Dataset},
  year = {2026},
  publisher = {Hugging Face},
  version = {1.8},
  url = {https://huggingface.co/datasets/Viverun/jits-legal-dataset}
}
```

Or:

```text
Viverun (2026). JITS Legal Dataset (v1.8). Hugging Face.
```

## License

Licensed under [Apache-2.0](LICENSE).

## Community And Feedback

If you find noise, schema drift, or extraction errors, please open an issue:

- [GitHub Issues](https://github.com/Viverun/jits-data-pipeline/issues)

Contributions to the deterministic rules, mappings, audits, and documentation are welcome.
