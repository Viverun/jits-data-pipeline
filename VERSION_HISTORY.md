# JITS Legal Dataset - Version History

This document provides the canonical mapping between dataset versions and pipeline commits for full reproducibility.

---

## Version History

### v1.3 (Current)

**Release Date**: January 2026  
**Pipeline Commit**: `TBD` (to be tagged upon release)  
**HuggingFace Dataset**: `Viverun/jits-legal-dataset`

#### Key Features
- IPC → BNS transition coverage (856 mappings)
- Enhanced citation audit (1,247+ landmark references)
- Similarity coherence validation (85.0% verified)
- 908 finalized judgments with full provenance

#### Pipeline Changes
- Deterministic metadata extraction (98.9% accuracy)
- Rule-based domain classification
- Statutory transition engine for legacy cases
- Similarity graph construction with coherence validation

#### Audit Results
```
Total Judgments: 908
Metadata Accuracy: 98.9%
Citation Coverage: 39.3%
Similarity Coherence: 85.0%
Statutory Mappings: 856 IPC sections
```

---

## Reproducibility Instructions

To regenerate any dataset version:

1. Clone the repository at the specified commit:
   ```bash
   git clone https://github.com/Viverun/jits-data-pipeline.git
   cd jits-data-pipeline
   git checkout <commit_hash>
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Run the pipeline:
   ```bash
   legal-ai pipeline
   ```

4. Verify outputs:
   ```bash
   legal-ai audit --type quality
   ```

---

## Commit Hash Instructions

When tagging a release:

1. **Tag the commit**:
   ```bash
   git tag -a v1.3 -m "JITS Legal Dataset v1.3 - IPC→BNS transitions"
   git push origin v1.3
   ```

2. **Update this file** with the commit hash

3. **Update DATASET_CARD.md** with the same commit hash

4. **Create GitHub release** referencing the dataset version

---

## Provenance Contract

Each dataset version guarantees:

- ✅ Deterministic outputs (no randomness)
- ✅ Identical inputs → identical outputs
- ✅ Traceable to explicit commit hash
- ✅ Auditable via included quality scripts
- ✅ Versioned statutory mappings (IPC, BNS, CrPC, BNSS)

---

## Notes

- Dataset versions use semantic versioning (vX.Y)
- Pipeline commits are immutable references
- HuggingFace dataset card maintains authoritative version table
- This file provides detailed changelog and audit data
