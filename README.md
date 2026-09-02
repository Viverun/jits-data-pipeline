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

Current release state: **v1.11** (pipeline and dataset). Same 4,661-document
corpus as `v1.10`, but 1,216 documents that came back from the downloader with
no recoverable header have been re-fetched and corrected, raising the release
export from 3,324 to 4,451 rows.

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 4661 | Same document count as `v1.10`; 1,216 corrected in place |
| **Metadata Accuracy** | 88.7% (4134/4661) | Court + date + case_number all present |
| **Missing Court** | 103 | Was 1231 in `v1.10` |
| **Missing Decision Date** | 437 | Was 905 in `v1.10` |
| **Missing Case Number** | 1541 | Was 1779 in `v1.10` |
| **Duplicate IDs** | 0 | ID uniqueness validated |
| **Referential Integrity Errors** | 36 | Pre-existing category (see Known Issues): re-IDing the 1,216 corrected documents added more stale cluster references, same root cause as `v1.10`'s 23 |
| **Release Export Rows (`train.jsonl`)** | 4451 | UNKNOWN-court and unknown-year IDs excluded (was 3324 in `v1.10`, 2215 in `v1.8`) |
| **Release Missing Dates** | 317 | Rows still eligible for release |
| **Release Missing Case Numbers** | 1367 | Rows still eligible for release |
| **Similarity Edges** | 802,552 | **Still not rebuilt** — reflects only the pre-`v1.10` 2,215-judgment corpus |
| **Refined Clusters** | 77 | **Still not rebuilt** — same caveat |

### Metadata Completeness

Completeness is reported **per field** rather than as a single all-three-present
conjunction, and every `case_number` must contain a digit to count:

| Field | Coverage | Notes |
|-------|----------|-------|
| `court` | 100.0% | 4451/4451 (the release filter excludes unknown-court records) |
| `decision_date` | 92.9% | 4134/4451 |
| `case_number` | 69.3% | 3084/4451, digit-validated |
| **Mean field completeness** | **87.4%** | headline metric |
| All-three-present (strict) | 63.3% | previous definition, retained for comparison |

Measured on the `4451`-row release export, not the `4661`-judgment full corpus.

### v1.11: Downloader Header-Loss Bug

`v1.10` shipped 1,231 unknown-court records, every one of them from the
2,502-document backlog (the pre-existing corpus had ~0). Sampling 20 of them
showed the raw `.txt` files themselves started mid-document, with no cause
title at all - and any "High Court" mention nearby was a citation to another
court's precedent, not the originating court, so a smarter regex could not
safely recover it.

The actual cause was in the downloader, not extraction: Indian Kanoon renders
the court name, case title, author, and bench as `<h2>`/`<h3>` headings, the
opening cause-title block as a bare `<pre>`, and some judgment paragraphs as
`<blockquote>`. `extract_clean_text()` only kept direct-child `<p>`/`<div>`
tags, so all of that - not just the header - was silently dropped on every
page that used this layout.

Fixed by widening the allowlist to `["p", "div", "h1", "h2", "h3", "h4",
"pre", "blockquote"]` (regression tests added: `test_downloader.py`). Verified
on a live sample page that the fix recovers the correct court, case number,
decision date, and parties.

Backfilled the existing corpus rather than waiting for a future download run:
1,216 of the 1,231 unknown-court records had a `source_url` in
`download_manifest.jsonl` (the other 15 predate the manifest and could not be
re-fetched). Re-fetched all 1,216 (paced, resumable, 12 transient DNS
failures retried to completion), replaced the truncated raw text in place,
and reprocessed them through the full pipeline. `1,128` (93%) now have a
resolved court; `88` remain unknown even with the full page content,
presumably a different page layout. Total full-corpus document count is
unchanged at `4661` - this only replaces the content and regenerates the
IDs of the 1,216 corrected records (a breaking ID change for those specific
records, same as any other extraction correction in this project's history).

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

- **36 orphaned cluster references** (pre-existing, not introduced by `v1.11`):
  `annotations/similarity/clusters_refined.json` references judgment IDs that
  are not present in the corpus. `v1.10` had 23; correcting the 1,216
  documents in `v1.11` regenerated their IDs and added more, same root cause.
- **Similarity graph and clusters are stale.** `edges.jsonl` and
  `clusters_refined.json` were built from the `2,215`-judgment `v1.8` corpus
  and have not been rebuilt over the `2,446` judgments added in `v1.10` or the
  1,216 corrected in `v1.11`. They do not yet reflect the current corpus.
- **103 records still have no resolvable court**: 15 predate
  `download_manifest.jsonl` and have no `source_url` to re-fetch; 88 came back
  from a full, corrected re-fetch with still no identifiable header (a
  different page layout, presumably).
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

### v1.11 (2026-09-02)

Fixes the root cause of `v1.10`'s 1,231 unknown-court records rather than
accepting them as unrecoverable.

- found the actual cause: the downloader's `extract_clean_text()` kept only
  direct-child `<p>`/`<div>` tags, silently dropping the `<h2>`/`<h3>`
  headings Indian Kanoon uses for court name/case title/author/bench, the
  `<pre>` cause-title block, and `<blockquote>` judgment paragraphs
- fixed the tag allowlist; verified against a live sample page that court,
  case number, decision date, and parties are now all recovered correctly;
  regression tests added (`tests/test_downloader.py`)
- re-fetched all `1,216` backlog documents that had a `source_url` in
  `download_manifest.jsonl` (paced, resumable; 15 of the original 1,231
  predate the manifest and could not be re-fetched), replaced their
  truncated raw text, and reprocessed them through the full pipeline
- `1,128` of `1,216` (93%) now have a resolved court; `88` remain unknown
  even with full page content
- full corpus document count unchanged at `4661`; `train.jsonl` grows
  `3324` → `4451` rows
- similarity edges/clusters still not rebuilt; orphaned cluster references
  grew `23` → `36` from the ID changes (same pre-existing category, not a
  new defect)
- verification green: full suite `91/91`

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
