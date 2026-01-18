# 📁 Data File Structure Guide - Version 2.0

## Quick Reference for New Users

---

## 🎯 Which Files Should I Use?

### For Most Applications: Use `processed/` Files ⭐

The `processed/` directory contains **unified judgment files** with all extractions integrated:

```python
import json
from pathlib import Path

# Load a complete judgment (RECOMMENDED)
file = Path("legal_ai_toolkit/data/judgments/processed/CIVIL_100121852.json")
with open(file) as f:
    judgment = json.load(f)

# Everything is in one place:
citations = judgment['extractions']['citations']      # All citations
sections = judgment['extractions']['sections']        # All sections
transitions = judgment['extractions']['transitions']  # All IPC→BNS mappings
```

---

## 📂 Directory Structure Explained

```
legal_ai_toolkit/data/judgments/
│
├── citations/           (1,056 files)
│   └── Purpose: Citation analysis, network graphs
│   └── Contains: Reporter + case name citations
│   └── Feature: Self-citations excluded
│
├── sections/            (1,056 files)
│   └── Purpose: Statutory section analysis, pattern discovery
│   └── Contains: Sections grouped by act (IPC, CrPC, etc.)
│   └── Feature: Multi-act support (9+ acts)
│
├── transitions/         (1,056 files)
│   └── Purpose: IPC→BNS transition research
│   └── Contains: IPC to BNS mappings with confidence
│   └── Feature: Temporal validation
│
└── processed/           (1,056 files) ⭐ RECOMMENDED
    └── Purpose: Complete judgment data
    └── Contains: Citations + Sections + Transitions + Metadata
    └── Feature: Everything in one unified structure
```

---

## 📄 File Formats

### 1. Citations File (`citations/{judgment_id}.json`)

```json
{
  "judgment_id": "CIVIL_100121852",
  "total_citations": 30,
  "citations": [
    {
      "type": "reporter",
      "reporter": "AIR",
      "year": "2015",
      "page": "123",
      "court": "SC"
    },
    {
      "type": "case_name",
      "petitioner": "ABC Ltd",
      "respondent": "XYZ Corp"
    }
  ]
}
```

**Use Cases:**
- Citation network analysis
- Precedent identification
- Landmark case research

---

### 2. Sections File (`sections/{judgment_id}.json`)

```json
{
  "judgment_id": "CIVIL_100121852",
  "total_sections": 6,
  "sections_by_act": {
    "IPC": ["498-A", "304-B"],
    "CrPC": ["313"],
    "Evidence Act": ["113-B"],
    "Dowry Prohibition Act": ["3", "4"]
  },
  "sections_detailed": [
    {
      "section": "498-A",
      "act": "IPC",
      "category": "criminal"
    }
  ]
}
```

**Use Cases:**
- Statutory section frequency analysis
- Multi-act pattern discovery
- Legal issue classification

---

### 3. Transitions File (`transitions/{judgment_id}.json`)

```json
{
  "judgment_id": "CIVIL_100121852",
  "total_transitions": 2,
  "transitions": [
    {
      "ipc": "498-A",
      "bns": "86",
      "source": "inferred_from_ipc",
      "confidence": "low",
      "requires_judicial_confirmation": true
    },
    {
      "ipc": "304-B",
      "bns": "80",
      "source": "inferred_from_ipc",
      "confidence": "low"
    }
  ]
}
```

**Use Cases:**
- IPC→BNS transition research
- Legacy code modernization
- Statutory mapping studies

---

### 4. Processed/Integrated File (`processed/{judgment_id}.json`) ⭐

```json
{
  "judgment_id": "CIVIL_100121852",
  "metadata": {
    "integrated_date": "2026-01-18T14:57:00"
  },
  "extractions": {
    "citations": {
      "total": 30,
      "by_type": {
        "reporter": 20,
        "case_name": 10
      },
      "details": [...]
    },
    "sections": {
      "total": 6,
      "by_act": {
        "IPC": ["498-A", "304-B"],
        "CrPC": ["313"]
      },
      "details": [...]
    },
    "transitions": {
      "total": 2,
      "by_source": {
        "inferred_from_ipc": 2
      },
      "details": [...]
    }
  },
  "classification": {...}  // If available
}
```

**Use Cases:**
- Complete judgment analysis
- ML model training
- Production applications
- Research datasets

---

## 🎯 Common Use Cases

### Use Case 1: Citation Network Analysis

```python
from pathlib import Path
import json

citations_dir = Path("legal_ai_toolkit/data/judgments/citations")

all_citations = []
for file in citations_dir.glob("*.json"):
    with open(file) as f:
        data = json.load(f)
        all_citations.extend(data['citations'])

# Analyze citation network
reporter_citations = [c for c in all_citations if c['type'] == 'reporter']
print(f"Total reporter citations: {len(reporter_citations)}")
```

### Use Case 2: Section Frequency Analysis

```python
from collections import Counter
from pathlib import Path
import json

sections_dir = Path("legal_ai_toolkit/data/judgments/sections")

ipc_sections = Counter()
for file in sections_dir.glob("*.json"):
    with open(file) as f:
        data = json.load(f)
        ipc_sections.update(data['sections_by_act'].get('IPC', []))

# Top 10 most common IPC sections
print("Top 10 IPC sections:")
for section, count in ipc_sections.most_common(10):
    print(f"  IPC {section}: {count} judgments")
```

### Use Case 3: IPC→BNS Transition Mapping

```python
from pathlib import Path
import json

transitions_dir = Path("legal_ai_toolkit/data/judgments/transitions")

ipc_to_bns_map = {}
for file in transitions_dir.glob("*.json"):
    with open(file) as f:
        data = json.load(f)
        for t in data['transitions']:
            if t['ipc'] not in ipc_to_bns_map:
                ipc_to_bns_map[t['ipc']] = t['bns']

print(f"Total IPC→BNS mappings: {len(ipc_to_bns_map)}")
print("Sample mappings:")
for ipc, bns in list(ipc_to_bns_map.items())[:5]:
    print(f"  IPC {ipc} → BNS {bns}")
```

### Use Case 4: Complete Judgment Analysis (RECOMMENDED)

```python
from pathlib import Path
import json

processed_dir = Path("legal_ai_toolkit/data/judgments/processed")

# Load all judgments
judgments = []
for file in processed_dir.glob("*.json"):
    with open(file) as f:
        judgments.append(json.load(f))

# Analyze
total_citations = sum(j['extractions']['citations']['total'] for j in judgments)
total_sections = sum(j['extractions']['sections']['total'] for j in judgments)
total_transitions = sum(j['extractions']['transitions']['total'] for j in judgments)

print(f"Dataset Statistics:")
print(f"  Judgments: {len(judgments)}")
print(f"  Citations: {total_citations}")
print(f"  Sections: {total_sections}")
print(f"  Transitions: {total_transitions}")
```

---

## 📊 Data Statistics

| Directory | Files | Total Extractions | Coverage |
|-----------|-------|------------------|----------|
| `citations/` | 1,056 | 5,637 citations | 73.1% of judgments |
| `sections/` | 1,056 | 3,780 sections | 44.6% of judgments |
| `transitions/` | 1,056 | 1,476 transitions | 35.4% of judgments |
| `processed/` | 1,056 | All combined | 100% of judgments |

---

## 🎓 Best Practices

### ✅ DO:
- Use `processed/` files for most applications
- Load only the extraction type you need if working with large datasets
- Check `total` counts before iterating through details
- Use `by_act` or `by_type` groupings for quick analysis

### ❌ DON'T:
- Don't load all files at once if you only need citations or sections
- Don't assume all judgments have all extraction types (check `total` first)
- Don't mix v1.0 and v2.0 data (v2.0 is significantly improved)

---

## 🆕 Migration from v1.0

If you were using the old v1.0 dataset:

| v1.0 | v2.0 Equivalent |
|------|-----------------|
| Single judgment JSON | `processed/{id}.json` |
| Citation count | `extractions.citations.total` |
| Sections | `extractions.sections.by_act` |
| Transitions | `extractions.transitions.details` |

**Key Difference**: v2.0 has self-citations excluded and complete section extraction, so counts may differ.

---

## 📞 Questions?

See:
- `README.md` - Main documentation
- `PROJECT_INDEX.md` - Complete navigation
- `HUGGINGFACE_UPLOAD_READY.md` - Upload guide
- Test files in `tests/` for usage examples

---

**Last Updated**: January 18, 2026  
**Version**: 2.0
