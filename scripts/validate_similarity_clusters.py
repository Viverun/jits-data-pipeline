import json
import os

CLUSTER_FILE = "annotations/similarity/clusters.json"

def validate_clusters():
    if not os.path.exists(CLUSTER_FILE):
        print(f"❌ File not found: {CLUSTER_FILE}")
        return

    with open(CLUSTER_FILE, "r", encoding="utf-8") as f:
        try:
            clusters = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ {CLUSTER_FILE} is not a valid JSON file")
            return

    errors = 0

    for i, cluster in enumerate(clusters, start=1):
        if "cluster_id" not in cluster:
            print(f"❌ Cluster {i}: missing cluster_id")
            errors += 1
        if "judgments" not in cluster or not isinstance(cluster["judgments"], list):
            print(f"❌ Cluster {i}: invalid judgments list")
            errors += 1
        elif len(cluster["judgments"]) < 2:
            print(f"⚠️ Cluster {i}: only one judgment (may not be useful)")
        
        if "reason" not in cluster:
            print(f"❌ Cluster {i}: missing reason")
            errors += 1

    print(f"✅ Clusters checked: {len(clusters)}")
    print(f"❌ Errors found: {errors}")

if __name__ == "__main__":
    validate_clusters()
