# 🏛️ Judicial Intelligence & Transition System (JITS) / Legal AI Toolkit
### *A Deterministic, "Zero-ML" Legal Data Factory for Indian Court Operations*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

The **Legal AI Toolkit** is a high-performance orchestration layer designed to transform unstructured Indian legal judgments into structured, legally-defensible datasets. Unlike probabilistic AI models, JITS relies on **rule-based statutory anchors**, ensuring that every output is explainable, repeatable, and auditable by judicial authorities.

---

## 📊 Dataset Operational Status (v1.1)

*   **908** Finalized judgments processed into structured JSON (Gold Standard).
*   **93.3%** Metadata Extraction Accuracy (Automated capture of Court, Date, and Case IDs).
*   **39.3%** Landmark Citation Coverage (Automatic identification of cases like *Umadevi*, *Arnesh Kumar*, etc.).
*   **54** Legally coherent similarity clusters for batch listing optimizations.
*   **100%** Deterministic IPC → BNS statutory transition mapping.

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
│   ├── classification/    # Zero-ML domain classifiers (Criminal, Civil, Service)
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

## ⚙️ The Zero-ML Factory Pipeline
The system follows a strict, multi-stage enrichment process without "black-box" ML dependencies:
1.  **Ingestion**: Normalization and unique, stable ID generation.
2.  **Metadata**: Extraction of Court names, Bench, and Decision Dates.
3.  **Classify**: Rule-based domain assignment with confidence scoring.
4.  **Transitions**: Mapping IPC sections to their BNS (Bharatiya Nyaya Sanhita) counterparts.
5.  **Issues**: Identifying key legal issues from judgment headers.
6.  **Citations**: Extracting and matching landmark citations.
7.  **Similarity**: Building relationship graphs between cases.
8.  **Consolidate**: Final JSON generation for the bundled dataset.
3.  **Classification**: Categorization into Service, Criminal, or Civil domains.
4.  **Transitions**: **IPC → BNS (2024)** mapping for legacy case modernization.
5.  **Issue Extraction**: Deterministic tagging of legal issues (Bail, Arbitration, etc.).
6.  **Citations**: Graph construction from SCC, AIR, and SCALE references.
7.  **Similarity**: Generation of high-precision clusters for judicial batching.
8.  **Consolidation**: Final production-ready JSON synthesis.
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
## 📜 License
Directly licensed under the [LICENSE](LICENSE) provided in this repository.
## 🤝 Contributing
Researchers and developers are welcome to contribute to the deterministic rulesets, IPC-BNS mapping databases, or the issue taxonomy. 
*Powered by the Legal AI Toolkit.*