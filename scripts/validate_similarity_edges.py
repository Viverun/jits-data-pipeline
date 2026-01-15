import json
import os

EDGE_FILE = "annotations/similarity/edges.jsonl"
required_fields = {
    "source_judgment_id",
    "target_judgment_id",
    "similarity_score",
    "signals",
    "reason"
}

def validate_edges():
    if not os.path.exists(EDGE_FILE):
        print(f"❌ File not found: {EDGE_FILE}")
        return

    errors = 0
    count = 0

    with open(EDGE_FILE, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                missing = required_fields - obj.keys()
                if missing:
                    print(f"❌ Line {line_no}: Missing fields {missing}")
                    errors += 1
                if "similarity_score" in obj and not isinstance(obj["similarity_score"], (int, float)):
                    print(f"❌ Line {line_no}: similarity_score not numeric")
                    errors += 1
                count += 1
            except json.JSONDecodeError:
                print(f"❌ Line {line_no}: Invalid JSON")
                errors += 1

    print(f"✅ Checked {count} edges")
    print(f"❌ Errors found: {errors}")

if __name__ == "__main__":
    validate_edges()
