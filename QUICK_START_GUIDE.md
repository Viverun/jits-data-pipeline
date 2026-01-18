# Quick Start Guide - Pipeline v2.0.1

**Version:** 2.0.1 (All Critical Fixes Applied)  
**Date:** January 18, 2026  
**Status:** ✅ Production Ready

---

## 🚀 Quick Start (3 Steps)

### 1. Clean Previous Data
```bash
# Delete old processed files
python -c "
import shutil
from pathlib import Path

# Clean interim directories
for d in Path('interim').glob('*'):
    if d.is_dir():
        shutil.rmtree(d)
        print(f'Cleaned: {d}')

# Clean output
if Path('legal_ai_toolkit/data/judgments').exists():
    shutil.rmtree('legal_ai_toolkit/data/judgments')
    print('Cleaned: legal_ai_toolkit/data/judgments')

print('✅ Cleanup complete!')
"
```

### 2. Run Pipeline
```bash
# Full pipeline with all critical fixes
python -m legal_ai_toolkit.cli run-pipeline --workers 4
```

### 3. Validate Results
```bash
# Validate general pipeline
python validate_v2_pipeline.py

# Validate critical fixes (ID timing, file renaming, etc.)
python validate_critical_fixes.py
```

---

## 📋 Pipeline Steps (NEW Order)

```
Step 1: Ingestion
  ↓ Generates: TEMP_ABC123DEF456

Step 2: Metadata Extraction
  ↓ Extracts: court, parties, bench
  ↓ Keeps: TEMP_ABC123DEF456

Step 3: Issue Extraction
  ↓ Extracts: legal issues
  ↓ Keeps: TEMP_ABC123DEF456

Step 4: Classification
  ↓ Uses: issues for better accuracy
  ↓ Keeps: TEMP_ABC123DEF456
  ↓ Adds: classification.domain

Step 4.5: ID Regeneration ⭐ NEW
  ↓ Regenerates: IN-HC-DEL-2023-SV-ABC123
  ↓ Renames files: TEMP_*.json → IN-HC-*.json
  ↓ Tracks: ID history in provenance

Step 5: Statutory Transitions
  ↓ Uses: stable IDs

Step 6: Citation Extraction
  ↓ Uses: case name for self-filtering

Step 7: Similarity Analysis
  ↓ Uses: stable IDs (no orphaned references)

Step 8: Consolidation
  ↓ Final unified JSON
```

---

## ✅ Expected Outputs

### Interim Directories
```
interim/
├── normalized_text/          # Step 1: TEMP_*.json
├── headers_extracted/         # Step 2: TEMP_*.json
├── issues_extracted/          # Step 3: TEMP_*.json
├── classified/                # Step 4: TEMP_*.json
├── id_regenerated/ ⭐         # Step 4.5: IN-HC-*.json (proper IDs!)
├── transitions_extracted/     # Step 5: IN-HC-*.json
└── citations_extracted/       # Step 6: IN-HC-*.json
```

### Final Output
```
legal_ai_toolkit/data/judgments/
├── IN-HC-DEL-2023-CV-ABC123.json
├── IN-HC-DEL-2023-SV-DEF456.json
├── IN-SC-SUP-2024-CR-GHI789.json
└── ...

annotations/similarity/
├── edges.jsonl                # Edges with stable IDs
├── clusters.json
└── signals/
    ├── IN-HC-DEL-2023-CV-ABC123.json
    └── ...
```

---

## 🔍 Validation Checklist

### ✅ Step 1: Check ID Format
```bash
# Should see proper IDs, NOT TEMP_
ls interim/id_regenerated/*.json | head -5

# Expected output:
# IN-HC-DEL-2023-CV-ABC123.json
# IN-HC-DEL-2023-SV-DEF456.json
```

### ✅ Step 2: Verify Domain Codes
```bash
python -c "
import json
from pathlib import Path

for f in list(Path('interim/id_regenerated').glob('*.json'))[:5]:
    data = json.load(open(f))
    jid = data['judgment_id']
    domain = data.get('classification', {}).get('domain')
    
    # Check domain code matches
    if domain == 'service' and '-SV-' in jid:
        print(f'✅ {f.name}: service → SV')
    elif domain == 'criminal' and '-CR-' in jid:
        print(f'✅ {f.name}: criminal → CR')
    elif domain == 'civil' and '-CV-' in jid:
        print(f'✅ {f.name}: civil → CV')
    else:
        print(f'❌ {f.name}: {domain} (code mismatch!)')
"
```

### ✅ Step 3: Check File Renaming
```bash
python -c "
import json
from pathlib import Path

for f in list(Path('interim/id_regenerated').glob('*.json'))[:5]:
    data = json.load(open(f))
    filename = f.stem
    internal_id = data['judgment_id']
    
    if filename == internal_id:
        print(f'✅ {filename}')
    else:
        print(f'❌ Mismatch: {filename} vs {internal_id}')
"
```

### ✅ Step 4: Verify Similarity Edges
```bash
# Check edges don't have TEMP_ IDs
grep "TEMP_" annotations/similarity/edges.jsonl

# Expected output: (nothing - no matches)
```

---

## 🐛 Troubleshooting

### Issue: TEMP_ IDs in id_regenerated/
**Symptom:**
```bash
ls interim/id_regenerated/
# Output: TEMP_ABC123.json  ❌
```

**Cause:** ID regeneration step didn't run or failed

**Fix:**
```bash
# Run ID regeneration step manually
python -m legal_ai_toolkit.cli run-step id_regen

# Check error log
cat interim/id_regenerated/errors_*.json
```

---

### Issue: Domain code wrong in ID
**Symptom:**
```bash
# Service matter classified as CV instead of SV
IN-HC-DEL-2023-CV-ABC123.json  ❌
{"classification": {"domain": "service"}}
```

**Cause:** Classification step didn't run before ID regeneration

**Fix:**
```bash
# Re-run in correct order
python -m legal_ai_toolkit.cli run-step issues
python -m legal_ai_toolkit.cli run-step classify
python -m legal_ai_toolkit.cli run-step id_regen
```

---

### Issue: Filename doesn't match internal ID
**Symptom:**
```bash
# File: TEMP_ABC123.json
# Internal: IN-HC-DEL-2023-SV-ABC123
```

**Cause:** File renaming logic not working

**Fix:**
```bash
# Check BaseStep has file renaming code
grep -A 10 "old_id != new_id" legal_ai_toolkit/pipeline/runner.py

# Should see:
# if old_id != new_id:
#     out_path = self.output_dir / f"{new_id}.json"
```

---

### Issue: Orphaned similarity edges
**Symptom:**
```bash
# Edges reference IDs that don't exist
{"from": "TEMP_ABC123", "to": "TEMP_DEF456"}
```

**Cause:** Similarity ran before ID regeneration

**Fix:**
```bash
# Re-run similarity AFTER id_regen
python -m legal_ai_toolkit.cli run-step id_regen
python -m legal_ai_toolkit.cli run-step transitions
python -m legal_ai_toolkit.cli run-step citations
python -m legal_ai_toolkit.cli run-step similarity
```

---

## 📊 Performance Expectations

### Small Dataset (100 judgments)
- **Ingestion:** ~30 seconds
- **Metadata:** ~1 minute
- **Issues:** ~1 minute
- **Classification:** ~30 seconds
- **ID Regeneration:** ~10 seconds ⭐
- **Transitions:** ~1 minute
- **Citations:** ~2 minutes
- **Similarity:** ~2 minutes (with optimization)
- **Total:** ~8-10 minutes

### Large Dataset (1000 judgments)
- **Ingestion:** ~5 minutes
- **Metadata:** ~10 minutes
- **Issues:** ~10 minutes
- **Classification:** ~5 minutes
- **ID Regeneration:** ~1 minute ⭐
- **Transitions:** ~10 minutes
- **Citations:** ~20 minutes
- **Similarity:** ~20 minutes (with optimization, was ~40-60 min)
- **Total:** ~80-90 minutes

---

## 🎯 Success Criteria

Before deploying to production, verify:

- [ ] ✅ No TEMP_ IDs in final output
- [ ] ✅ Domain codes match classification (service → SV, criminal → CR, civil → CV)
- [ ] ✅ Filenames match internal judgment_id
- [ ] ✅ No orphaned references in similarity edges
- [ ] ✅ Provenance tracking includes ID history
- [ ] ✅ Error logs generated for failures
- [ ] ✅ All validation scripts pass

**Run both validation scripts:**
```bash
python validate_v2_pipeline.py       # General validation
python validate_critical_fixes.py    # Critical fixes validation
```

Both should show: **"ALL CHECKS PASSED"** ✅

---

## 📞 Support

### Quick Commands
```bash
# Run full pipeline
python -m legal_ai_toolkit.cli run-pipeline --workers 4

# Run single step
python -m legal_ai_toolkit.cli run-step <step_name>
# Steps: ingest, metadata, issues, classify, id_regen, transitions, citations, similarity, consolidate

# Validate
python validate_v2_pipeline.py
python validate_critical_fixes.py

# Check errors
find interim/ -name "errors_*.json" -exec cat {} \;
```

### Documentation
- `CODE_REVIEW_IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `MIGRATION_GUIDE_V2.md` - Migration strategies
- `PIPELINE_REFACTORING_SUMMARY.md` - Technical details

---

**Pipeline v2.0.1 - All Critical Fixes Applied** 🚀
