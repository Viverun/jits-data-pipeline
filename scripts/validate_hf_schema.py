"""HF-schema validator: mimics HF datasets Arrow cast checks with stdlib only."""
import json
import sys
from collections import Counter
from pathlib import Path

PATH = Path(sys.argv[1] if len(sys.argv) > 1 else "train.jsonl")

EXPECTED_TRANSITION_KEYS = tuple(sorted([
    "ipc", "bns", "source", "validated", "risk", "confidence",
    "note", "context_snippet", "requires_judicial_confirmation", "temporal_warning",
]))
EXPECTED_CITATION_KEYS = tuple(sorted([
    "type", "reporter", "year", "page", "volume", "court",
    "petitioner", "respondent", "case_name", "raw",
    "start_pos", "end_pos", "is_landmark", "precedent_id",
]))

errors = []
trans_keysets = Counter()
cit_keysets = Counter()
bench_types = Counter()

with PATH.open(encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            r = json.loads(line)
        except Exception as e:
            errors.append(f"row {i}: invalid JSON: {e}")
            continue
        # bench must be list
        bench_types[type(r.get("metadata", {}).get("bench")).__name__] += 1
        if not isinstance(r.get("metadata", {}).get("bench"), list):
            if len(errors) < 5:
                errors.append(f"row {i} {r.get('judgment_id')}: bench is {type(r['metadata']['bench']).__name__}, expected list")
        # transitions uniform
        for loc in ("statutory_transitions",):
            arr = r.get(loc, [])
            for d in arr:
                ks = tuple(sorted(d.keys())) if isinstance(d, dict) else ("NONDIC",)
                trans_keysets[ks] += 1
                if ks != EXPECTED_TRANSITION_KEYS and len(errors) < 10:
                    errors.append(f"row {i}: {loc} keys {ks} != expected")
                    break
        det = r.get("extractions", {}).get("transitions", {}).get("details", [])
        for d in det:
            ks = tuple(sorted(d.keys())) if isinstance(d, dict) else ("NONDIC",)
            trans_keysets[ks] += 1
        # citations uniform
        cdet = r.get("extractions", {}).get("citations", {}).get("details", [])
        for d in cdet:
            ks = tuple(sorted(d.keys())) if isinstance(d, dict) else ("NONDIC",)
            cit_keysets[ks] += 1
            if ks != EXPECTED_CITATION_KEYS and len(errors) < 10:
                errors.append(f"row {i}: citation keys {ks} != expected")
                break

print(f"bench types: {dict(bench_types)}")
print(f"transition keysets: {len(trans_keysets)} variants")
for ks, c in trans_keysets.most_common():
    print(f"  {c}: {ks}")
print(f"citation keysets: {len(cit_keysets)} variants")
for ks, c in cit_keysets.most_common()[:5]:
    print(f"  {c}: {ks}")

if errors:
    print("\nFAIL: HF-blocking heterogeneities found:")
    for e in errors[:10]:
        print(" -", e)
    sys.exit(1)
# strict gates for the two fields that broke HF parquet conversion
if set(bench_types) != {"list"}:
    print("\nFAIL: bench must be list in every row")
    sys.exit(1)
if set(trans_keysets) != {EXPECTED_TRANSITION_KEYS} and trans_keysets:
    # empty train.jsonl edge: allow no transitions, but if any exist they must be uniform
    print("\nFAIL: statutory_transitions not uniform")
    sys.exit(1)
if set(cit_keysets) != {EXPECTED_CITATION_KEYS} and cit_keysets:
    print("\nFAIL: citations.details not uniform")
    sys.exit(1)
print("\nPASS: uniform structs, HF Arrow cast should succeed for these fields")
