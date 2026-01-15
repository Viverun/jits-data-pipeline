"""
Step 07: Similarity Engine (Batch Listing)
-----------------------------------------
Zero-ML, rule-based similarity detection for judicial batch listing.
"""

import os
import json
import itertools
from collections import defaultdict

# --------------------
# Paths
# --------------------
PROCESSED_DIR = "processed/judgments"
SIM_DIR = "annotations/similarity"
SIGNALS_DIR = os.path.join(SIM_DIR, "signals")

EDGES_FILE = os.path.join(SIM_DIR, "edges.jsonl")
CLUSTERS_FILE = os.path.join(SIM_DIR, "clusters.json")

os.makedirs(SIGNALS_DIR, exist_ok=True)

# --------------------
# Helper functions
# --------------------
def load_judgments():
    judgments = {}
    for file in os.listdir(PROCESSED_DIR):
        if file.endswith(".json"):
            with open(os.path.join(PROCESSED_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                judgments[data["judgment_id"]] = data
    return judgments


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --------------------
# Similarity rules
# --------------------
def compute_similarity(j1, j2):
    signals = []

    # 1️⃣ Legal issue overlap
    issues1 = set(j1.get("legal_issues", []))
    issues2 = set(j2.get("legal_issues", []))
    issue_score = jaccard(issues1, issues2)

    if issue_score >= 0.5:
        signals.append({
            "type": "LEGAL_ISSUE_OVERLAP",
            "score": round(issue_score, 2),
            "details": list(issues1 & issues2)
        })

    # 2️⃣ Statutory overlap (IPC/BNS)
    secs1 = set(j1.get("statutes", []))
    secs2 = set(j2.get("statutes", []))
    statute_score = jaccard(secs1, secs2)

    if statute_score >= 0.5:
        signals.append({
            "type": "STATUTE_OVERLAP",
            "score": round(statute_score, 2),
            "details": list(secs1 & secs2)
        })

    # 3️⃣ Procedural posture
    if j1.get("procedural_stage") == j2.get("procedural_stage"):
        signals.append({
            "type": "PROCEDURAL_MATCH",
            "score": 1.0,
            "details": j1.get("procedural_stage")
        })

    return signals


# --------------------
# Main execution
# --------------------
def main():
    judgments = load_judgments()
    edges = []
    clusters = defaultdict(list)

    for j1_id, j2_id in itertools.combinations(judgments.keys(), 2):
        j1, j2 = judgments[j1_id], judgments[j2_id]
        signals = compute_similarity(j1, j2)

        if signals:
            edge = {
                "source": j1_id,
                "target": j2_id,
                "signals": signals,
                "weight": round(sum(s["score"] for s in signals), 2)
            }
            edges.append(edge)

            # Save signal file (per pair)
            signal_path = os.path.join(
                SIGNALS_DIR, f"{j1_id}__{j2_id}.jsonl"
            )
            with open(signal_path, "w", encoding="utf-8") as sf:
                for s in signals:
                    sf.write(json.dumps({
                        "source": j1_id,
                        "target": j2_id,
                        **s
                    }) + "\n")

            # Simple clustering rule
            if edge["weight"] >= 1.5:
                cluster_key = "|".join(sorted([j1_id, j2_id]))
                clusters[cluster_key].extend([j1_id, j2_id])

    # Write edges
    with open(EDGES_FILE, "w", encoding="utf-8") as ef:
        for e in edges:
            ef.write(json.dumps(e) + "\n")

    # Write clusters
    final_clusters = [
        {
            "cluster_id": f"CLUSTER-{i+1:04d}",
            "judgments": sorted(set(jids)),
            "reason": "High statutory / issue similarity"
        }
        for i, jids in enumerate(clusters.values())
    ]

    with open(CLUSTERS_FILE, "w", encoding="utf-8") as cf:
        json.dump(final_clusters, cf, indent=2)

    print(f"✅ Similarity edges created: {len(edges)}")
    print(f"✅ Clusters created: {len(final_clusters)}")


if __name__ == "__main__":
    main()
