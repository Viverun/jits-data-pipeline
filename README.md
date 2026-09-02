# JITS Legal Dataset

A production-ready, deterministic pipeline for processing Indian legal judgments into structured, high-quality legal datasets, with comprehensive extraction, self-citation exclusion, statutory section detection, court normalization, and similarity analysis.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is not an official government or judicial release and does not constitute legal advice.

This repository contains the deterministic pipeline used to generate the JITS Legal Dataset. The current corpus build contains **4661** processed judgments, with **3324** release-ready rows exported in `train.jsonl`, with:

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

Current release state: **v1.10** (pipeline and dataset). This is a full corpus
rebuild: it processes a 2,502-document backlog that had never gone through the
pipeline, applies two newly discovered extraction fixes to the whole corpus, and
regenerates `train.jsonl`.

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 4661 | Consolidated deterministic corpus (was 3008 in `v1.8`) |
| **Metadata Accuracy** | 64.5% (3008/4661) | Court + date + case_number all present |
| **Missing Court** | 1231 | Remaining UNKNOWN-court records |
| **Missing Decision Date** | 905 | Full-corpus missing dates |
| **Missing Case Number** | 1779 | Full-corpus missing case numbers |
| **Unknown-Year IDs** | 339 | IDs with unresolved year in full corpus |
| **Duplicate IDs** | 0 | ID uniqueness validated |
| **Referential Integrity Errors** | 23 | Pre-existing: `clusters_refined.json` references 23 judgment IDs absent from the corpus, predating this release; see Known Issues |
| **Release Export Rows (`train.jsonl`)** | 3324 | UNKNOWN-court and unknown-year IDs excluded (was 2215 in `v1.8`) |
| **Release Missing Dates** | 316 | Rows still eligible for release |
| **Release Missing Case Numbers** | 981 | Rows still eligible for release |
| **Similarity Edges** | 802,552 | **Not rebuilt this release** — still reflects only the pre-`v1.10` 2,215-judgment corpus |
| **Refined Clusters** | 77 | **Not rebuilt this release** — same caveat |

### Metadata Completeness

Completeness is reported **per field** rather than as a single all-three-present
conjunction, and every `case_number` must contain a digit to count:

| Field | Coverage | Notes |
|-------|----------|-------|
| `court` | 100.0% | 3324/3324 (the release filter excludes unknown-court records) |
| `decision_date` | 90.5% | 3008/3324 |
| `case_number` | 70.5% | 2343/3324, digit-validated |
| **Mean field completeness** | **87.0%** | headline metric |
| All-three-present (strict) | 62.7% | previous definition, retained for comparison |

Measured on the `3324`-row release export, not the `4661`-judgment full corpus.

> **Resolved in `v1.10`:** the `v1.9` notes below describe a `case_number`
> quality fix (letters matching the shared number class under `re.I`) that had
> landed in code but not yet been applied to the published corpus. This release
> replays extraction over every record and applies it, plus two more extraction
> fixes found while processing the backlog (see below). `50` `case_number`
> values were corrected corpus-wide; no other metadata field changed.

### v1.10 Extraction Fixes

Processing the 2,502-document backlog surfaced two catastrophic-backtracking
regressions in `extract_case_number` that could hang the pipeline indefinitely
on ordinary judgment text (not malformed input — plain prose mentioning a High
Court and a `Cr.`/`MCRC`/etc. abbreviation with no case number immediately
following it):

- `CASE_NO_PATTERNS[7]` carried a trailing `(?:sep [class])*` group whose
  separators were already inside the preceding character class — the same
  defect `v1.9` had already removed from a sibling pattern, just not from this
  one.
- The unbounded fallback regex inside `_extract_high_court_embedded_case_tag`
  carried the identical group, as a standalone literal rather than a list
  entry, so the `v1.9` fix did not cover it either.

Both were fixed by removing the redundant group (regression tests added:
`test_paragraph_case_number_scan_does_not_backtrack_catastrophically`,
`test_high_court_embedded_fallback_does_not_backtrack_catastrophically`).
Verified against all `2161` pre-existing raw/processed judgment pairs with
zero further hangs and zero unintended changes to `court`, `decision_date`,
`petitioner`, or `respondent` — only `case_number` is affected by this fix.

### Known Issues

- **23 orphaned cluster references** (pre-existing, not introduced by `v1.10`):
  `annotations/similarity/clusters_refined.json` references judgment IDs that
  are not present in the corpus. Predates this release.
- **Similarity graph and clusters are stale.** `edges.jsonl` and
  `clusters_refined.json` were built from the `2,215`-judgment `v1.8` corpus
  and have not been rebuilt over the `2,446` judgments added in `v1.10`. They
  do not yet reflect the current corpus.
- **56 exact-duplicate raw documents were skipped**, not merged: the backlog
  contained 56 judgments whose full text was byte-identical to an
  already-published record (the same case downloaded twice under different
  filenames). Verified by direct text comparison and left out of the corpus.

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

### v1.10 (2026-09-02)

Full corpus rebuild.

- processed a `2,502`-document backlog of raw judgments that had been
  downloaded (tracked in `download_manifest.jsonl`) but never run through the
  pipeline
- found and fixed two catastrophic-backtracking regressions in
  `extract_case_number` that hung the pipeline indefinitely on ordinary
  judgment text; see "v1.10 Extraction Fixes" above
- `56` of the backlog documents were exact-text duplicates of already-published
  judgments (same case, different download filename) and were skipped rather
  than merged
- `2,446` genuinely new judgments merged into the corpus: full corpus
  `3008` → `4661`
- replayed the `v1.9` `case_number` digit-validation fix (previously landed in
  code but never applied to the published corpus) across the whole corpus
  alongside the two fixes above: `50` `case_number` values corrected
  corpus-wide, no other field affected
- `train.jsonl` regenerated: `2215` → `3324` rows
- similarity edges and clusters **not** rebuilt this release — still describe
  only the pre-`v1.10` corpus; tracked as a known issue
- verified: zero hangs and zero unintended field changes across all `2161`
  pre-existing raw/processed judgment pairs; two new regression tests added,
  full suite green: `89/89`

### v1.9 (2026-08-16)

Pipeline-only release. No corpus rebuild ships here, so the dataset metrics above
and the published Hugging Face artifact remain at `v1.8`.

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
- **completeness redefined**: reported per field rather than as a single
  all-three-present conjunction, and a `case_number` must contain a digit to
  count. mean field completeness `87.4%`, strict all-three `64.6%` still
  published alongside it
- fixed `case_number` extraction emitting non-case-numbers — `51` published
  values (3.2%) were person names, label fragments, or prose, because the shared
  number class matched letters under `re.I` (`Manoj` = `Ma` + `no` + number `j`)
- widened case-number coverage: trailing full stops on cause titles, the
  `PREFIX-NNNN-YYYY` registry form (`CRM-M-8611-2022`), and `CRL.M.P.` / `CS DJ`
- verified by replaying extraction over all `2215` records: `35` recovered,
  `0` lost, `48` garbage values removed
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

### v1.8 (2026-03-23)

- added targeted CWP court fallback (`Haryana` marker with Himachal exclusion) when court is `UNKNOWN`
- re-ran pipeline through `consolidate` and regenerated `train.jsonl`
- full-corpus quality now: metadata completeness `69.0%` (`2077/3008`), missing court `738`, missing date `384`, missing case number `1068`, unknown-year IDs `165`
- release export now `2215` rows, missing dates `138`, missing case numbers `597`
- verification green: metadata tests `63/63`

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
