---
license: apache-2.0
task_categories:
  - text-classification
  - token-classification
  - sentence-similarity
language:
  - en
size_categories:
  - n<1K
---

# JITS Legal Dataset

A structured dataset of Indian criminal law judgments generated using a
fully deterministic, rule-based processing pipeline.  
No machine learning models are used in data creation.

[![Version](https://img.shields.io/badge/version-1.3-blue.svg)](https://github.com/Viverun/jits-data-pipeline/releases/tag/v1.3)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://github.com/Viverun/jits-data-pipeline/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

The JITS Legal Dataset contains **908 Supreme Court and High Court judgments**
processed into machine-readable JSON with:

- Deterministic metadata extraction
- Statutory transition mapping (IPC → BNS, CrPC → BNSS)
- Rule-based issue and citation detection
- Similarity graphs for thematic clustering

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

## Reproducibility & Provenance

- No randomness or probabilistic models are used
- Identical inputs produce identical outputs
- Each dataset version corresponds deterministically to a specific
  pipeline commit

Core quality metrics are computed using audit logic in:
`legal_ai_toolkit/analytics/audit.py::DataAuditor.audit_quality()`

---

## Version History

| Dataset Version | Pipeline Commit | Release Date | Notes |
|-----------------|-----------------|--------------|-------|
| v1.3 | [View on GitHub](https://github.com/Viverun/jits-data-pipeline/releases/tag/v1.3) | January 2026 | IPC → BNS transition coverage, citation audit |

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

---

## Dataset Metrics

| Metric | Value |
|--------|-------|
| Total Judgments | 908 |
| Metadata Extraction Accuracy | 98.9% |
| Statutory Coverage | 856 IPC mappings |
| Citation Detection | 1,247+ landmark references |
| Similarity Edges | 12,000+ |
| Similarity Coherence | 85.0% |

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
