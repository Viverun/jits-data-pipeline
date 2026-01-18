# Migration Guide - Pipeline v2.0

**Date:** January 18, 2026  
**Migration:** v1.0 → v2.0

## Overview

This guide helps you migrate from the old pipeline (v1.0) to the refactored pipeline (v2.0) with improved ID generation, better classification, and enhanced error tracking.

---

## 🚨 Breaking Changes

### 1. Judgment ID Format Change

**Old (v1.0):**
```
IN-UNK-UNK-2026-CV-ABC123  # Generated at ingestion with placeholder values
```

**New (v2.0):**
```
TEMP_A1B2C3D4E5F6  # During ingestion
↓
IN-HC-DEL-2023-CV-A1B2C3  # After metadata extraction (proper semantic ID)
```

**Impact:** 
- Existing judgment IDs in your database will not match new IDs
- Need to regenerate IDs for consistency
- Or: maintain a mapping table between old and new IDs

---

### 2. Pipeline Step Order Change

**Old (v1.0):**
```
Metadata → Classification → Transitions → Issues → Citations
```

**New (v2.0):**
```
Metadata → Issues → Classification → Transitions → Citations
```

**Impact:**
- Cannot use v1.0 intermediate files with v2.0 pipeline
- Must reprocess from raw files OR from normalized text
- Classification results may differ (improved accuracy)

---

### 3. Enhanced Metadata Fields

**New fields added:**
- `petitioner`: String
- `respondent`: String
- `bench`: String (judge composition)

**Impact:**
- Downstream analytics relying on metadata schema should be updated
- Existing unified JSONs won't have these fields (backward compatible)

---

## 🔄 Migration Options

### Option A: Full Reprocessing (Recommended)

**Best for:** Clean slate, production deployment

```bash
# 1. Backup existing data
mkdir -p backup/
cp -r interim/ backup/interim_v1/
cp -r data/judgments/ backup/judgments_v1/

# 2. Clean interim directories
rm -rf interim/*

# 3. Run new pipeline
python -m legal_ai_toolkit.cli run-pipeline --workers 4

# 4. Verify outputs
python scripts/verify_v2_output.py
```

**Pros:**
- Clean, consistent IDs
- All new features enabled
- No legacy data issues

**Cons:**
- Time-consuming for large datasets
- Loses old IDs (need mapping if referenced elsewhere)

---

### Option B: Partial Migration (Hybrid)

**Best for:** Testing, gradual rollout

```bash
# Keep existing data, process only new files
python -m legal_ai_toolkit.cli run-step ingest --input-dir data/raw/new_judgments/

# Then run remaining pipeline
python -m legal_ai_toolkit.cli run-step metadata
python -m legal_ai_toolkit.cli run-step issues
python -m legal_ai_toolkit.cli run-step classify
# ... etc
```

**Pros:**
- Faster for incremental updates
- Can compare old vs new results

**Cons:**
- Mixed ID formats in database
- Need to track which version processed what

---

### Option C: ID Remapping (Advanced)

**Best for:** Preserving references, database integration

```bash
# Generate ID mapping from old to new
python scripts/generate_id_mapping.py \
    --old-dir backup/judgments_v1/ \
    --new-dir data/judgments/ \
    --output id_mapping.json

# Update database references
python scripts/update_database_refs.py --mapping id_mapping.json
```

**Mapping format:**
```json
{
  "IN-UNK-UNK-2026-CV-ABC123": "IN-HC-DEL-2023-CV-A1B2C3",
  "IN-UNK-UNK-2026-CV-DEF456": "IN-SC-SUP-2024-CR-D4E5F6"
}
```

**Pros:**
- Maintains backward compatibility
- Database integrity preserved

**Cons:**
- Complex implementation
- Additional maintenance overhead

---

## ✅ Pre-Migration Checklist

- [ ] Backup existing `interim/` directory
- [ ] Backup existing `data/judgments/` directory
- [ ] Document current database schema
- [ ] Test new pipeline on 10-20 sample files
- [ ] Verify error logs are working
- [ ] Check disk space (error logs + provenance = ~20% larger files)
- [ ] Update any scripts that rely on judgment IDs
- [ ] Update analytics dashboards for new metadata fields

---

## 🧪 Testing the New Pipeline

### 1. Small Batch Test

```bash
# Create test directory with 10 files
mkdir -p data/raw/test_batch/
cp data/raw/judgments/*.txt data/raw/test_batch/ | head -10

# Run pipeline on test batch
python -m legal_ai_toolkit.cli run-pipeline \
    --input-dir data/raw/test_batch/ \
    --output-dir test_output/ \
    --workers 2

# Verify outputs
ls test_output/
# Should see proper IDs: IN-HC-DEL-2023-CV-XXXXXX (not TEMP_XXXXXX)
```

### 2. Validate ID Regeneration

```python
import json
from pathlib import Path

# Check a processed file
with open('test_output/IN-HC-DEL-2023-CV-123456.json') as f:
    data = json.load(f)

# Verify:
assert data['judgment_id'].startswith('IN-')
assert not data['judgment_id'].startswith('TEMP_')
assert 'petitioner' in data['metadata']  # New field
assert 'bench' in data['metadata']  # New field
assert 'provenance' in data  # New field
print("✅ Validation passed!")
```

### 3. Compare Classification Results

```bash
# Run comparison script
python scripts/compare_classification.py \
    --old-dir backup/judgments_v1/ \
    --new-dir test_output/ \
    --report classification_diff.html
```

Expected improvements:
- Service matter detection: +15-20% accuracy
- Mixed domain detection: +10% accuracy

---

## 🐛 Troubleshooting

### Issue 1: TEMP_ IDs in Final Output

**Symptom:**
```json
{"judgment_id": "TEMP_ABC123DEF456", ...}
```

**Cause:** Metadata extraction step failed or didn't regenerate ID

**Fix:**
```bash
# Check metadata extraction errors
cat interim/headers_extracted/errors_*.json

# Re-run metadata step
python -m legal_ai_toolkit.cli run-step metadata
```

---

### Issue 2: Missing Petitioner/Respondent

**Symptom:**
```json
{"metadata": {"court": "...", "decision_date": "..."}}
// No "petitioner" or "respondent" fields
```

**Cause:** Header parsing couldn't find party information

**Fix:**
- This is expected for some judgments (not all headers have party names)
- Check `metadata.bench` - if also missing, header may be malformed
- Manually review 1-2 files to ensure patterns are working

---

### Issue 3: Classification Changed from v1.0

**Symptom:** Judgment classified as "civil" in v1.0, now "service"

**Cause:** This is intentional - v2.0 uses extracted issues

**Validation:**
```python
# Check if service issues were detected
with open('judgment.json') as f:
    data = json.load(f)

issues = data['annotations']['issues']
if any(issue in ['seniority_promotion', 'pension_gratuity', ...] for issue in issues):
    print("✅ Correct: Service issue detected")
```

---

### Issue 4: Similarity Calculation Very Slow

**Symptom:** Similarity step taking hours

**Potential causes:**
1. Not using the optimized version (check git branch)
2. Too many judgments (O(n²) growth)
3. Insufficient workers

**Fix:**
```bash
# Use more workers (but not more than CPU cores)
python -m legal_ai_toolkit.cli run-step similarity --workers 8

# Or: Process in batches
python scripts/batch_similarity.py --batch-size 1000
```

---

## 📊 Validation Queries

### Check ID Migration Success Rate

```bash
# Count TEMP_ IDs in final output (should be 0)
grep -r "TEMP_" data/judgments/ | wc -l
# Expected: 0

# Count proper IDs
grep -r "IN-[A-Z]" data/judgments/*.json | wc -l
# Expected: Total number of judgments
```

### Check New Metadata Fields

```bash
# Check how many have petitioner
grep -r '"petitioner":' data/judgments/*.json | wc -l

# Check how many have bench
grep -r '"bench":' data/judgments/*.json | wc -l
```

### Check Error Logs

```bash
# Find all error logs
find interim/ -name "errors_*.json"

# Summarize failures
python scripts/summarize_errors.py
```

---

## 🚀 Production Deployment Checklist

- [ ] Test pipeline on 100+ judgments
- [ ] Verify all error logs are captured
- [ ] Confirm ID regeneration success rate > 95%
- [ ] Update database schema for new metadata fields
- [ ] Update API endpoints for new provenance field
- [ ] Document ID mapping strategy (if needed)
- [ ] Train team on new error log locations
- [ ] Set up monitoring for pipeline failures
- [ ] Create rollback plan (keep v1.0 backups for 30 days)
- [ ] Update CI/CD pipelines

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Check error logs: `interim/*/errors_*.json`
2. Review `PIPELINE_REFACTORING_SUMMARY.md`
3. Run validation script: `python scripts/validate_v2_pipeline.py`
4. Check GitHub issues for known problems

---

## 🔮 Future Considerations

### Planned Enhancements (Not Yet Implemented)

1. **Schema Validation**
   - Add JSON schema validation after each step
   - Catch data quality issues early

2. **Adaptive Clustering**
   - Use statistical thresholds instead of hard-coded values
   - Better cluster quality

3. **Set-Based Similarity**
   - Pre-convert signals to sets for O(1) lookups
   - Further performance improvements

4. **Incremental Processing**
   - Only reprocess modified files
   - Timestamp-based change detection

---

**End of Migration Guide**

Good luck with the migration! 🚀
