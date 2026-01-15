import json
import os

PROCESSED_DIR = "processed/judgments"
EDGE_FILE = "annotations/similarity/edges.jsonl"
CLUSTER_FILE = "annotations/similarity/clusters.json"

def validate_references():
    # Load existing judgment IDs
    existing_ids = set()
    if not os.path.exists(PROCESSED_DIR):
        print(f"❌ Directory not found: {PROCESSED_DIR}")
        return

    for f in os.listdir(PROCESSED_DIR):
        if f.endswith(".json"):
            with open(os.path.join(PROCESSED_DIR, f), "r", encoding="utf-8") as jf:
                try:
                    data = json.load(jf)
                    if "judgment_id" in data:
                        existing_ids.add(data["judgment_id"])
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse {f}")

    errors = 0

    # Check edges
    if os.path.exists(EDGE_FILE):
        with open(EDGE_FILE, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line: continue
                try:
                    obj = json.loads(line)
                    if obj.get("source_judgment_id") not in existing_ids:
                        print(f"❌ Edge Line {line_no}: Missing source judgment: {obj.get('source_judgment_id')}")
                        errors += 1
                    if obj.get("target_judgment_id") not in existing_ids:
                        print(f"❌ Edge Line {line_no}: Missing target judgment: {obj.get('target_judgment_id')}")
                        errors += 1
                except json.JSONDecodeError:
                    pass # Handled in edge validator

    # Check clusters
    if os.path.exists(CLUSTER_FILE):
        with open(CLUSTER_FILE, "r", encoding="utf-8") as f:
            try:
                clusters = json.load(f)
                for i, cluster in enumerate(clusters, start=1):
                    for jid in cluster.get("judgments", []):
                        if jid not in existing_ids:
                            print(f"❌ Cluster {cluster.get('cluster_id', i)} references missing judgment: {jid}")
                            errors += 1
            except json.JSONDecodeError:
                pass # Handled in cluster validator

    print(f"✅ Referential integrity check complete.")
    print(f"❌ Total reference errors: {errors}")

if __name__ == "__main__":
    validate_references()
