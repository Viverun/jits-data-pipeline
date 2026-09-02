---
license: apache-2.0
task_categories:
  - text-classification
  - token-classification
  - sentence-similarity
tags:
  - information-retrieval
  - statistical-analysis
  - graph-analysis
  - law
  - legal
language:
  - en
size_categories:
  - 1K<n<10K
---

# JITS Legal Dataset

A production-ready, deterministic pipeline for processing Indian legal judgments into structured, high-quality legal datasets — with comprehensive extraction, self-citation exclusion, and multi-act statutory section detection.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://github.com/Viverun/jits-data-pipeline/blob/main/LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

---

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is *not* an official government or judicial release and does not constitute legal advice.

The JITS Legal Dataset currently contains **4661 processed judgments** in the full corpus,
with **3324 rows** in the current public `train.jsonl` release export,
processed into machine-readable JSON with:

- **Clean text extraction** with artifact removal (Phase 1)
- **Citation extraction** with self-citation exclusion (Phase 2)
- **Multi-act section extraction** supporting 19 statutory acts (Phase 3)
- **IPC→BNS transition mapping** with temporal validation (Phase 4)
- **Comprehensive processing** of 4661 judgments (current full-corpus build)

All outputs are reproducible, auditable, and traceable to explicit rules.

---

## Intended Use

This dataset is designed to support multiple use cases:

- **Research**: Legal NLP benchmarking without label noise from ML
- **Engineering**: Structured legal data for analytics and downstream systems
- **Hackathons**: Ready-to-use dataset requiring no preprocessing
- **Legal & GovTech**: Explainable, audit-friendly legal data artifacts

This dataset is **not** intended to provide legal advice.

**Limitations**: While portions of the dataset were manually reviewed, the dataset has not undergone formal judicial or institutional validation.

---

## Dataset Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Full Corpus (Processed Judgments)** | 4661 | Consolidated deterministic corpus (was 3008 in `v1.8`) |
| **Release Export Rows (`train.jsonl`)** | 3324 | UNKNOWN-court and unknown-year IDs excluded (was 2215 in `v1.8`) |
| **Metadata Accuracy** | 64.5% (3008/4661) | Court + date + case_number all present |
| **Missing Court (Full Corpus)** | 1231 | Remaining UNKNOWN-court records |
| **Missing Decision Date (Full Corpus)** | 905 | Full-corpus missing dates |
| **Missing Case Number (Full Corpus)** | 1779 | Full-corpus missing case numbers |
| **Unknown-Year IDs (Full Corpus)** | 339 | IDs with unresolved year |
| **Release Missing Dates** | 316 | Missing dates in exported `train.jsonl` |
| **Release Missing Case Numbers** | 981 | Missing case numbers in exported `train.jsonl` |
| **Similarity Edges** | 802,552 | **Not rebuilt in `v1.10`** — still describes only the pre-`v1.10` 2,215-judgment corpus |
| **Refined Clusters** | 77 | **Not rebuilt in `v1.10`** — same caveat |
| **Duplicate IDs** | 0 | Uniqueness verified |
| **Referential Integrity Errors** | 23 | Pre-existing orphaned cluster references, predates `v1.10` — see Known Issues |

### Metadata Completeness (v1.10)

Completeness is reported **per field** rather than as a single all-three-present
conjunction, and a `case_number` must contain a digit to count:

| Field | Coverage | Notes |
|-------|----------|-------|
| `court` | 100.0% | 3324/3324 (the release filter excludes unknown-court records) |
| `decision_date` | 90.5% | 3008/3324 |
| `case_number` | 70.5% | 2343/3324, digit-validated |
| **Mean field completeness** | **87.0%** | headline metric |
| All-three-present (strict) | 62.7% | previous definition, retained for comparison |

Measured on the `3324`-row release export, not the `4661`-judgment full corpus.

The conjunction could not separate an extraction failure from a field that is
absent at source: some records are served without a cause-title header, so no
parser can recover a case number from them. Per-field coverage also shows
where the gap actually is — `100.0%` on court against `70.5%` on case number.

> **Resolved in `v1.10`:** the `v1.9` case_number quality fix below (letters
> matching the shared number class under `re.I`) had landed in code but was
> never applied to the published corpus. `v1.10` replays extraction over every
> record and applies it, plus two more catastrophic-backtracking extraction
> bugs found while processing a 2,502-document backlog — ordinary judgment
> text mentioning a High Court could hang the pipeline indefinitely. `50`
> `case_number` values were corrected corpus-wide; no other metadata field
> changed. See the GitHub repository's `README.md` release notes for detail.

> **Known issue in `v1.8`/`v1.9` (superseded above):** `51` records (3.2% of
> populated values) carried `case_number` values that were not case numbers —
> person names (`Manoj`, `MANOMOHAN`), label fragments (`CASE NO`), and
> sentence fragments. Under `re.I` the shared number class matched letters, so
> `Manoj` parsed as `Ma` + `no` + number `j`. Kept here for history; resolved
> in `v1.10` as described above.

### Known Issues (v1.10)
- Similarity edges and refined clusters were **not** rebuilt for `v1.10` and
  only describe the pre-`v1.10` 2,215-judgment corpus, not the 2,446 judgments
  added in this release.
- `clusters_refined.json` has 23 pre-existing references to judgment IDs no
  longer present in the corpus; predates `v1.10`.
- 56 documents from the backlog processed for `v1.10` were exact-text
  duplicates of already-published judgments (same case, different source
  filename) and were left out of the corpus rather than merged.

### Quality Improvements
- ✅ **Self-citation exclusion**: No false positive citations
- ✅ **Complete section extraction**: Hyphenated sections (498-A, 304-B) now captured
- ✅ **Section-act context**: All sections linked to correct parent act
- ✅ **Temporal transition guardrails**: Pre-`2024-07-01` judgments do not receive inferred BNS mappings
- ✅ **Canonical court codes**: HC/SC/TR levels with real court identifiers (ALL, DEL, BOM...)
- ✅ **Tribunal separation**: CAT records correctly typed as TR, not HC
- ✅ **Comprehensive testing**: Validated extraction modules

---

## Data Generation

The dataset was generated using a deterministic pipeline that performs:

- Text normalization and stable ID generation
- Rule-based metadata and domain classification
- Statutory transition mapping for legacy cases
- Issue, citation, and landmark extraction
- Deterministic similarity graph construction

The full preprocessing, audit logic, and schemas are available in the
associated GitHub repository:

👉 https://github.com/Viverun/jits-data-pipeline

## Reproducibility & Provenance

### Quick Verification
To reproduce the dataset generation locally:

```bash
git clone https://github.com/Viverun/jits-data-pipeline.git
cd jits-data-pipeline
uv sync
source .venv/bin/activate
legal-ai pipeline && legal-ai audit --type quality
```

- No randomness or probabilistic models are used
- Identical inputs produce identical outputs
- Each dataset version corresponds deterministically to a specific
  pipeline commit

> **Note on Dataset Size:** Earlier snapshots in this repository may show lower counts. The current deterministic corpus build contains **3008** processed judgments, while the current release export contains **2215** rows after UNKNOWN-court and unknown-year exclusion.

### Changelog

#### v1.9 (2026-08-16) — pipeline only

The corpus is **not** rebuilt in this release. All dataset metrics above, and the
published `train.jsonl`, remain exactly as generated for `v1.8`.

- Made similarity edge generation, centroid selection, and cluster refinement
  independent of set iteration order, and sorted pipeline file iteration so ID
  collisions resolve identically every run. Artifacts are now byte-identical across
  `PYTHONHASHSEED` values; previously refined-cluster membership could differ between
  runs on identical inputs.
- Widened statutory section extraction from `9` acts to `19` (adds NI Act, CPC,
  Arbitration, MV Act, Companies Act, IBC, PC Act, Income Tax, Hindu Marriage,
  SARFAESI). On a `2,215`-judgment sample rebuild this lifted section coverage from
  `50.7%` to `66.0%` of cases — the shipped corpus will pick this up at the next rebuild.
- Removed regex backtracking in case-number header parsing and added act-presence
  gating plus pattern caching to section extraction, each verified output-identical
  against the prior implementation on real corpus text.
- Added `pyproject.toml`, `uv.lock`, and a Python `3.10` pin; the repository
  previously had no build configuration, so `pip install -e .` could not succeed.
- **Completeness is now reported per field**, not as a single all-three-present
  conjunction, and a `case_number` must contain a digit to count. Mean field
  completeness `87.4%`; the strict all-three figure (`64.6%`) is still published
  alongside it. See *Metadata Completeness* above for why the definition changed.
- Fixed `case_number` extraction emitting non-case-numbers. `51` published values
  (3.2%) were person names, label fragments, or prose — under `re.I` the shared
  number class matched letters, so `Manoj` parsed as `Ma` + `no` + number `j`.
- Widened case-number coverage: trailing full stops on cause titles, the
  `PREFIX-NNNN-YYYY` registry form (`CRM-M-8611-2022`), and `CRL.M.P.` / `CS DJ`.
- Verified by replaying extraction over all `2215` records: `35` recovered,
  `0` lost, `48` garbage values removed.
- Verification green: full suite `87/87`.

#### v1.8 (2026-03-23)

- Added targeted CWP court fallback (`Haryana` marker with Himachal exclusion) when court is `UNKNOWN`.
- Re-ran pipeline through `consolidate` and regenerated `train.jsonl`.
- Full-corpus quality now: metadata `69.0%` (`2077/3008`), missing court `738`, missing date `384`, missing case number `1068`, unknown-year IDs `165`, non-ISO dates `0`, duplicate IDs `0`.
- Release quality now: `2215` rows, missing dates `138`, missing case numbers `597`, unknown-year IDs excluded from export.
- Verification green: metadata tests `63/63`.

#### v1.7 (2026-03-22)

- Added strict release gate to block unknown-year (`0000`) IDs in export/upload.
- Deepened decision-date fallback and year recovery in metadata/ID regeneration.
- Fixed metadata case-number regex backtracking stalls and restored stable throughput.
- Re-ran pipeline from metadata through consolidate.
- Rebuilt similarity graph (`802,552` edges) and refined clusters (`77`).
- Referential integrity re-validated with `0` errors after graph rebuild.
- Full-corpus quality now: metadata completeness `67.4%` (`2027/3008`), missing court `753`, missing date `527`, missing case number `1108`, unknown-year IDs `238`, non-ISO dates `0`, duplicate IDs `0`.
- Release quality now: `2181` rows, missing dates `154`, missing case numbers `607`, unknown-year IDs `0`, non-ISO dates `0`.

#### v1.6 (2026-03-22)

- Rebuilt corpus through `consolidate` and regenerated `train.jsonl`.
- Added deeper-header fallback recovery in metadata extraction.
- Added Delhi QR/order-portal detection, Orissa signed-location recovery, and Andhra Amaravati proceedings-sheet recovery.
- Added safer embedded high-court caption matching.
- Broadened case-tag support (`MA`, `First Appeal`, `C.Misc.`, `CR. WJC`).
- Full-corpus quality: `66.3%` metadata completeness (`1995/3008`), missing court `631`, unknown-year IDs `321`, non-ISO dates `0`, duplicate IDs `0`, referential integrity errors `0`.
- Release quality (`train.jsonl`): `2377` rows, unknown-ID cases excluded `631`, missing dates `382`, missing case numbers `635`, non-ISO dates `0`.
- Verification green: metadata tests `63/63`, normalize-dataset tests `3/3`, pipeline-runner tests `2/2`.

#### v1.5 (2026-03-19)

**Breaking**: 744 judgment IDs changed from v1.4.

- Court codes corrected across all IDs.
- Tribunal records (CAT, AFT) separated from High Court records.
- Metadata court extraction tightened; overmatched court phrases removed.
- 23 refined clusters (was 25), with 90,924 similarity edges unchanged.

#### v1.4 (2026-03-19)

- Regenerated all 846 records from the rebuilt raw text corpus and reran the full deterministic pipeline end-to-end.
- Fixed similarity signal extraction so statutory section overlap is populated from actual transition/section fields.
- Normalized decision dates and enforced temporal safeguards so judgments dated before `2024-07-01` do not receive inferred BNS mappings.
- Switched the pipeline to the strengthened zero-ML classifier with explicit service-domain handling and removed the prior writ-petition overclassification path.
- Wrote `statutory_transitions` consistently at the record top level in consolidated outputs.
- Corrected analytics compatibility for v2 extraction fields and removed the duplicate `audit_landmarks` method definition.
- **v1.4 breaking change**: `397` judgment IDs changed because domain classification was corrected. IDs containing `-CV-`, `-CR-`, or `-SV-` segments may differ from v1.3. If you stored v1.3 IDs externally, re-map using the `judgment_id` field in the new export.

Core quality metrics are computed using audit logic in:
`legal_ai_toolkit/analytics/audit.py::DataAuditor.audit_quality()`

---

## Dataset Structure

Each record contains:

- `judgment_id`: Stable unique identifier
- `text`: Full judgment text
- `metadata`: Court, date, case identifiers
- `extractions`: Structured citations, sections, issues, landmarks, and transition summaries
- `classification`: Rule-based domain classification
- `statutory_transitions`: IPC / CrPC → BNS / BNSS mappings
- `provenance`: Pipeline versioning and processing metadata

## Schema Overview

The dataset schema is designed for clarity and ease of use:

- **text** (`string`): Raw source text of the judgment, cleaned of HTML artifacts.
- **metadata** (`dict`): Core legal metadata including court, date, and case identifiers.
- **extractions** (`dict`): Structured legal entities extracted from the text (citations, sections).
- **classification** (`dict`): Rule-based domain classification (e.g., Civil vs Criminal) with confidence scores and signal keywords.
- **statutory_transitions** (`list`): Mappings of legacy IPC/CrPC sections to new BNS/BNSS equivalents.
- **provenance** (`dict`): detailed pipeline versioning and processing timestamp for full auditability.

> **Note:** The field `annotations` in the raw data is a logical grouping that acts as a container for extracted entities like citations, issues, and similarity metadata, which are detailed above under `extractions` and `classification`.

## JSON Record Example

Here is a simplified example of a single record:

```json
{
  "judgment_id": "IN-HC-ALL-2007-CR-25B3AC",
  "text": "Allahabad High Court...",
  "metadata": {
    "court": "Allahabad High Court",
    "court_level": "HC",
    "decision_date": "2007-12-11",
    "case_number": "CRIMINAL MISC. BAIL APPLICATION NO. 7936",
    "jurisdiction": "India"
  },
  "classification": {
    "domain": "criminal",
    "confidence": "high",
    "signals": {
      "criminal": ["CrPC", "IPC", "accused", "bail", "fir"]
    }
  },
  "statutory_transitions": [
    {
      "ipc": "498-A",
      "bns": null,
      "source": "pre_bns_background"
    }
  ],
  "provenance": {
    "pipeline_version": "2.0",
    "processed_date": "2026-03-19T19:35:17"
  }
}
```

---

## Source Code

The complete data processing pipeline, schemas, and audit tools are available at:

👉 https://github.com/Viverun/jits-data-pipeline

---

## Citation

If you use this dataset, please cite:

```
Viverun (2026). JITS Legal Dataset (v1.8). Hugging Face.
```

---

## License

This dataset is licensed under Apache-2.0.

## Community & Feedback

If you discover any noise, discrepancies, or have suggestions for improvements, please report them via the [GitHub Issues](https://github.com/Viverun/jits-data-pipeline/issues) page. Your feedback is crucial for refining this dataset.

Similarly, if you encounter any bugs in the processing pipeline, please contact us or open an issue on the repository. Contributions are welcome and highly appreciated!

*Note by Viverun*
