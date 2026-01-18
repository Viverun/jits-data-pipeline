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
| **Sections Extracted** | 2,433+ | Across 9+ statutory acts |
| **Statutory Acts Detected** | 9+ | IPC, CrPC, Evidence Act, Dowry Act, POCSO, BNS, BNSS, NDPS, SC/ST |
| **Processing Quality** | 0 errors | 100% success rate on current batch |

### Quality Improvements
- ✅ **Self-citation exclusion**: No false positive citations
- ✅ **Complete section extraction**: Hyphenated sections (498-A, 304-B) now captured
- ✅ **Section-act context**: All sections linked to correct parent act
- ✅ **100% transition coverage**: All extracted IPC sections mapped to BNS
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

---

---

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

> **Note on Dataset Size:** Earlier experimental pipeline runs processed up to 908 judgments. The current release (v1.3) contains **846 production-ready judgments** after stricter validation, self-citation exclusion, and quality filtering were applied.

Core quality metrics are computed using audit logic in:
`legal_ai_toolkit/analytics/audit.py::DataAuditor.audit_quality()`

---

## Dataset Structure

Each record contains:

- `judgment_id`: Stable unique identifier
- `text`: Full judgment text
- `metadata`: Court, date, case identifiers
- `classification`: Rule-based domain classification
- `annotations`: Issues, citations, landmarks
- `statutory_transitions`: IPC / CrPC → BNS / BNSS mappings
- `similarity`: Deterministic similarity signals and edges

## Schema Overview

The dataset schema is designed for clarity and ease of use:

- **text** (`string`): Raw source text of the judgment, cleaned of HTML artifacts.
- **metadata** (`dict`): Core legal metadata including court, date, and case identifiers.
- **extractions** (`dict`): Structured legal entities extracted from the text (citations, sections).
- **classification** (`dict`): Rule-based domain classification (e.g., Civil vs Criminal) with confidence scores and signal keywords.
- **statutory_transitions** (`list`): Mappings of legacy IPC/CrPC sections to new BNS/BNSS equivalents.
- **provenance** (`dict`): detailed pipeline versioning and processing timestamp for full auditability.

## JSON Record Example

Here is a simplified example of a single record:

```json
{
  "judgment_id": "IN-HC-ALL-2006-CV-E0B4E7",
  "text": "Allahabad High Court...",
  "metadata": {
    "court": "Allahabad High Court",
    "date": "2006-11-03",
    "bench": ["V.M. Sahai", "Sabhajeet Yadav"]
  },
  "classification": {
    "domain": "service",
    "confidence": "high",
    "signals": {
      "service": ["seniority", "pension", "Article 16"]
    }
  },
  "statutory_transitions": [
    {
      "ipc": "302",
      "bns": "103",
      "source": "inferred"
    }
  ],
  "provenance": {
    "version": "2.0",
    "processed_date": "2026-01-18T18:40:35"
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
Viverun, JITS Legal Dataset, Hugging Face, 2026.
```

---

## License

This dataset is licensed under Apache-2.0.
