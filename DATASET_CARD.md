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
  - n<1K
---

# JITS Legal Dataset

A production-ready, deterministic pipeline for processing Indian legal judgments into structured, high-quality legal datasets — with comprehensive extraction, self-citation exclusion, and multi-act statutory section detection.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://github.com/Viverun/jits-data-pipeline/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

> **Disclaimer:** This dataset is independently created for research and engineering use. It is *not* an official government or judicial release and does not constitute legal advice.

The JITS Legal Dataset contains **846 Supreme Court and High Court judgments**
processed into machine-readable JSON with:

- **Clean text extraction** with artifact removal (Phase 1)
- **Citation extraction** with self-citation exclusion (Phase 2)
- **Multi-act section extraction** supporting 9+ statutory acts (Phase 3)
- **IPC→BNS transition mapping** with temporal validation (Phase 4)
- **Comprehensive processing** of 846 judgments (Phase 5)

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
| **Total Judgments** | 846 | Available in `train.jsonl` |
| **Processed Files** | 846 | 100% processed and validated |
| **Citations Extracted** | 4,233 | Self-citations excluded |
| **Sections Extracted** | 2,402 | Across 9+ statutory acts |
| **Statutory Acts Detected** | 9+ | IPC, CrPC, Evidence Act, Dowry Act, POCSO, BNS, BNSS, NDPS, SC/ST |
| **Similarity Edges** | 90,924 | Deterministic graph edges after clean rerun |
| **Refined Clusters** | 25 | High-precision similarity clusters |
| **Domain Distribution** | criminal 356; service 191; mixed 179; civil 119; unknown 1 | Post-fix v1.4 rerun |
| **Processing Quality** | 0 errors | 100% success rate on current batch |

### Quality Improvements
- ✅ **Self-citation exclusion**: No false positive citations
- ✅ **Complete section extraction**: Hyphenated sections (498-A, 304-B) now captured
- ✅ **Section-act context**: All sections linked to correct parent act
- ✅ **Temporal transition guardrails**: Pre-`2024-07-01` judgments do not receive inferred BNS mappings
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
pip install -e .
legal-ai pipeline && legal-ai audit --type quality
```

- No randomness or probabilistic models are used
- Identical inputs produce identical outputs
- Each dataset version corresponds deterministically to a specific
  pipeline commit

> **Note on Dataset Size:** Earlier experimental pipeline runs processed up to 908 judgments. The current release (v1.4) contains **846 production-ready judgments** after stricter validation, self-citation exclusion, and quality filtering were applied.

### Changelog

#### v1.4

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
Viverun (2026). JITS Legal Dataset (v1.4). Hugging Face.
```

---

## License

This dataset is licensed under Apache-2.0.

## Community & Feedback

If you discover any noise, discrepancies, or have suggestions for improvements, please report them via the [GitHub Issues](https://github.com/Viverun/jits-data-pipeline/issues) page. Your feedback is crucial for refining this dataset.

Similarly, if you encounter any bugs in the processing pipeline, please contact us or open an issue on the repository. Contributions are welcome and highly appreciated!

*Note by Viverun*
