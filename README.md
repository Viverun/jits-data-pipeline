# 🏛️ Judicial Intelligence & Transition System (JTIS) / Legal AI Toolkit
### *A Deterministic, "Zero-ML" Legal Data Factory for Indian Court Operations*
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
The **Legal AI Toolkit** (part of the JITS project) is a high-performance orchestration layer designed to transform unstructured Indian legal judgments into structured, legally-defensible datasets. Unlike probabilistic AI models, JITS relies on **rule-based statutory anchors**, ensuring that every output is explainable, repeatable, and auditable by judicial authorities.
---
## 📊 Dataset Operational Status (v1.0)
*   **908** Finalized judgments processed into structured JSON.
*   **900+** Raw text judgments bundled for research.
*   **54** Legally coherent similarity clusters identified for batch listing.
*   **99.6%** Annotation completeness across the dataset.
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
The toolkit provides a unified CLI `legal-ai` and an interactive CLI dashboard:

*   **Launch Dashboard**: `legal-ai dashboard` (or `legal-ai-dashboard`)
*   **Run Full Pipeline**: `legal-ai pipeline`
*   **Audit Dataset**: `legal-ai audit --type quality`
*   **Generate Report**: `legal-ai report`
---
## 🏗️ System Architecture
The project has been refactored into a unified package root, making the logic and the data immediately accessible to researchers and developers.
```text
jits-data/
├── legal_ai_toolkit/      # Package Root (The "Logic")
│   ├── analytics/         # Auditing and Reporting tools
│   ├── classification/    # Zero-ML domain classifiers
│   ├── clustering/        # Similarity and Centroid grouping
│   ├── extraction/        # Metadata, Citations, and Downloaders
│   ├── pipeline/          # The 8-step Factory Orchestrator
│   ├── utils/             # Legal Knowledge Bases (IPC/BNS mappings)
│   └── data/              # Bundled Gold Standard Dataset (The "Product")
├── annotations/           # Intelligence layer (Clusters, Edges, Signals)
├── schemas/               # Official Data Contracts (JSON Schemas)
└── setup.py               # Pip-installable configuration
```
---
## ⚙️ The Zero-ML Factory Pipeline
The system follows a strict, multi-stage enrichment process without "black-box" ML dependencies:
1.  **Ingestion**: Normalization and stable ID generation.
2.  **Metadata**: Automated capture of Court, Level, and Decision Date.
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