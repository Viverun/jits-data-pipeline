# JITS Legal Dataset v1.3

A deterministic, rule-based pipeline for processing Indian criminal law judgments into structured, auditable legal datasets — no machine learning, full explainability.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

This project transforms raw Supreme Court and High Court judgments into machine-readable JSON with:
- Deterministic metadata extraction and classification
- Statutory transition mapping (IPC → BNS, CrPC → BNSS)
- Citation and issue detection
- Similarity graphs and thematic clustering

All processing logic is rule-based, not probabilistic. Outputs are reproducible, auditable, and traceable to explicit rules.

---

## 🎯 Who This Project Is For

This repository and dataset are intentionally designed to serve multiple stakeholders:

### 📄 Researchers
- Fully reproducible, deterministic pipeline
- Auditable dataset creation (no probabilistic labeling)
- Clear schemas and versioned outputs
- Suitable for legal NLP benchmarking and evaluation (without label noise from ML)

### 💼 Hiring Managers & Engineers
- Demonstrates large-scale text processing at dataset scale
- Rule-engine design and statutory knowledge modeling
- Production-style architecture with CLI tooling and audits
- Emphasis on explainability and correctness over black-box accuracy

### 🏆 Hackathons & Competitions
- Ready-to-use structured legal dataset (908 judgments)
- Clear problem framing (classification, similarity, transitions)
- Fast onboarding via Hugging Face + CLI tools
- No preprocessing required

### ⚖️ Legal & Government Adoption
- Rule-based, explainable logic suitable for judicial contexts
- Deterministic outputs auditable by legal professionals
- Designed for modernization initiatives requiring compliance and transparency

> **This is not an end-user legal advice system.**  
> While portions of the dataset were manually reviewed, the dataset has not undergone formal judicial or institutional validation.

All audiences interact with the same canonical dataset and deterministic pipeline; the difference lies only in how the outputs are consumed.

---

## 📌 Dataset vs Pipeline Clarification

- **This GitHub repository** contains the deterministic data processing pipeline, rule engines, schemas, and audit tools.
- **The canonical dataset** is hosted on [Hugging Face](https://huggingface.co/datasets/Viverun/jits-legal-dataset) and should be used for training, research, or downstream applications.

Any data bundled in this repository exists only for transparency, provenance, and reproducibility.

---

## 🔁 Reproducibility & Provenance

The dataset published on Hugging Face can be regenerated using this pipeline with:
- Identical rule sets
- Versioned statutory mappings (IPC → BNS, CrPC → BNSS)
- Deterministic execution (no randomness or ML models)

Each dataset version corresponds deterministically to a specific pipeline commit hash, documented in the dataset card.

**Audit verification**: Core quality metrics are computed by 
`legal_ai_toolkit/analytics/audit.py::DataAuditor.audit_quality()`

---

## Dataset Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Judgments** | 908 | Supreme Court + High Courts |
| **Metadata Extraction Accuracy** | 98.9% | Measured on 908 manually-verified judgments; audit logic in `legal_ai_toolkit/analytics/audit.py::DataAuditor.audit_quality()` |
| **Statutory Coverage** | 856 IPC mappings | IPC → BNS transitions |
| **Citation Detection** | 1,247+ landmark case references | Rule-based extraction; see `legal_ai_toolkit/extraction/citations.py::CitationExtractor.extract()` |
| **Similarity Edges** | 12,000+ | Deterministic graph construction |
| **Similarity Coherence** | 85.0% | Validated on high-strength edges |

---

## ⚡ Hackathon Quick Start

- Download dataset from [Hugging Face](https://huggingface.co/datasets/Viverun/jits-legal-dataset)
- Use structured fields for:
  - Case classification (domain, confidence, signals)
  - Similarity & clustering analysis
  - Statutory transition modeling (IPC → BNS)
- No preprocessing required — fields are ready for ML, analytics, or visualization

Ideal for rapid prototyping and legal analytics demos.

---

## 🚀 Quick Start

### Installation
Clone the repository and install the toolkit in editable mode:
```bash
git clone https://github.com/Viverun/jits-data-pipeline.git
cd jits-data-pipeline
pip install -e .
```

### Essential Commands
The toolkit provides a unified CLI `legal-ai` and an interactive dashboard:

*   **Launch Dashboard**: `legal-ai dashboard` (Real-time analytics & data exploration)
*   **Audit Quality**: `legal-ai audit --type quality` (Verify metadata and annotation density)
*   **Run Pipeline**: `legal-ai pipeline` (Process new raw text into structured JSON)
*   **Check Integrity**: `python scripts/audit_dataset.py` (Validate link integrity across files)

---

## 🏗️ System Architecture
The project is built as an installable toolkit where the logic and the data coexist to provide full provenance.

```text
jits-data/
├── legal_ai_toolkit/      # Package Root (The "Logic")
│   ├── analytics/         # Auditing, reporting, and quality benchmarks
│   ├── classification/    # Rule-based domain classifiers (Criminal, Civil, Service)
│   ├── clustering/        # Similarity-based grouping and centroid logic
│   ├── extraction/        # Metadata, Citations, and Landmark identification
│   ├── pipeline/          # The 8-step "Factory" Orchestrator
│   ├── utils/             # Knowledge Bases (IPC/BNS mappings, Issue Taxonomies)
│   └── data/              # Bundled Gold Standard Dataset (908 JSONs)
├── annotations/           # Multi-layered intelligence (Clusters, Edges, Signals)
├── scripts/               # Utility scripts for maintenance and auditing
├── schemas/               # Official Data Contracts (Judgment & Similarity schemas)
└── setup.py               # Pip-installable configuration
```

---

## ⚙️ The Deterministic Factory Pipeline
The system follows a strict, 8-stage enrichment process without "black-box" ML dependencies:
1.  **Ingestion**: Normalization and unique, stable ID generation.
2.  **Metadata**: Extraction of Court names, Bench, and Decision Dates (98.9% accuracy).
3.  **Classify**: Rule-based domain assignment (Service, Criminal, Civil, Mixed).
4.  **Transitions**: **IPC → BNS (2024)** and **CrPC → BNSS** mapping for legacy case modernization.
5.  **Issues**: Identifying key legal issues from headers (Bail, Quashing, Seniority, etc.).
6.  **Citations**: Extracting AIR/SCC/SCALE references and matching landmark precedents.
7.  **Similarity**: Building relationship graphs and thematic clusters (85% validated coherence).
8.  **Consolidate**: Final JSON synthesis with full provenance for the bundled dataset.
---
## 🛠️ Advanced Usage
### Running Specific Pipeline Steps
If you only need to run part of the factory:
```bash
legal-ai pipeline --step classify   # Only run classification
legal-ai pipeline --step similarity # Only run similarity analysis
```
### Deep Dataset Auditing
Audit specific aspects of the dataset:
```bash
legal-ai audit --type landmarks  # Check landmark precedent coverage
legal-ai audit --type unmapped   # Find missing IPC-BNS mappings
legal-ai audit --type samples    # View random classification samples
```

---

## 📖 Citation

If you use this dataset or pipeline in research or applications, please cite:

```
Viverun, JITS Legal Dataset v1.3, Hugging Face, 2025.
```

---

## 📜 License
Directly licensed under the [LICENSE](LICENSE) provided in this repository.
## 🤝 Contributing
Researchers and developers are welcome to contribute to the deterministic rulesets, IPC-BNS mapping databases, or the issue taxonomy. 
*Powered by the Legal AI Toolkit.*