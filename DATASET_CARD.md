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
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
---

# JITS Legal Dataset

**The only major open Indian legal dataset with citation-graph extraction, statutory section tagging, and IPC/CrPC→BNS/BNSS transition mapping** — verified against the schemas of every comparable open dataset in this space (including one at 17.1M rows), which provide raw text and/or task labels but not structured legal extraction.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://github.com/Viverun/jits-data-pipeline/blob/main/LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

---

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is *not* an official government or judicial release and does not constitute legal advice.

The JITS Legal Dataset currently contains **10029 processed judgments** in the full corpus,
with **9517 rows** in the current public `train.jsonl` release export.

### What Makes This Different

- **Citation-graph extraction with self-citation exclusion** — an actual graph of what each judgment cites, not a raw text dump, with a judgment's references to itself filtered out so citation counts aren't inflated.
- **Multi-act statutory section tagging** across 19 acts (IPC, CrPC, Evidence Act, and more) — every invoked section linked to its parent act.
- **IPC/CrPC → BNS/BNSS transition mapping** — India's 2023–24 criminal-code overhaul mapped per judgment, with temporal guardrails so pre-`2024-07-01` judgments never get an inferred BNS mapping they can't have.
- **Zero-ML, fully deterministic pipeline** — every field traces to an explicit, auditable rule. Nothing here is a model's guess, and re-running the pipeline on the same input reproduces the same output.
- **Court/domain classification and similarity clustering** on top of the above, all reproducible from source.

All outputs are reproducible, auditable, and traceable to explicit rules.

**Attribution:** Judgment texts were sourced from [Indian Kanoon](https://indiankanoon.org/), an independent legal search engine; this project is not affiliated with or endorsed by Indian Kanoon.

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
| **Full Corpus (Processed Judgments)** | 10029 | |
| **Release Export Rows (`train.jsonl`)** | 9517 | UNKNOWN-court and unknown-year IDs excluded |
| **Metadata Accuracy** | 91.7% (9195/10029) | Court + date + case_number all present |
| **Missing Court / Date / Case Number** | 396 / 459 / 3236 | Full-corpus counts |
| **Duplicate IDs** | 0 | Uniqueness verified |
| **Referential Integrity Errors** | 0 | Rebuilt from scratch against the current corpus |
| **Similarity Edges / Refined Clusters** | 9,106,864 / 380 | **Freshly rebuilt** against the full 10,029-judgment corpus |

**Release-export field completeness:** court 100.0%, decision_date 96.6%, case_number 69.7% (digit-validated) — mean 88.8%, strict all-three-present 66.8%. The conjunction can't distinguish an extraction failure from a field genuinely absent at source (many records lack a cause-title header entirely).

### Known Issues
- 396 records have no resolvable court — mostly missing headers at the source that even the fixed downloader can't recover.
- A handful of exact-duplicate downloads (same case, different source filename) are detected and excluded automatically rather than merged.

See the GitHub repository's `README.md` for the full per-version changelog.

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
