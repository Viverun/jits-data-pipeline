import json
import random
from pathlib import Path
from collections import defaultdict

def load_judgment(jid, judgments_dir):
    path = Path(judgments_dir) / f"{jid}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def validate_similarity(judgments_dir, edges_file, clusters_file, samples=20):
    print("=== JITS SIMILARITY ENGINE VALIDATION ===")

    if not Path(edges_file).exists():
        print("Edge file not found.")
        return

    # Test 1: Cluster Coherence (High Strength Pairs)
    print(f"\nTest 1: High-Strength Pair Coherence (Sample: {samples})")
    print("-" * 50)

    high_strength_pairs = []
    with open(edges_file, "r", encoding="utf-8") as f:
        for line in f:
            edge = json.loads(line)
            if edge.get("strength") == "high":
                high_strength_pairs.append(edge)

    if not high_strength_pairs:
        print("No high-strength pairs found to validate.")
    else:
        sample_pairs = random.sample(high_strength_pairs, min(len(high_strength_pairs), samples))
        coherent_count = 0

        for pair in sample_pairs:
            s_id, t_id = pair["from"], pair["to"]
            case1 = load_judgment(s_id, judgments_dir)
            case2 = load_judgment(t_id, judgments_dir)

            if not case1 or not case2:
                continue

            # ipc1 = set(m["ipc"] for m in case1.get("statutory_transitions", {}).get("mapped", []))
            # ipc2 = set(m["ipc"] for m in case2.get("statutory_transitions", {}).get("mapped", []))

            ipc1 = set()
            for m in case1.get("statutory_transitions", {}).get("mapped", []):
                ipc1.add(m.get("ipc"))

            ipc2 = set()
            for m in case2.get("statutory_transitions", {}).get("mapped", []):
                ipc2.add(m.get("ipc"))

            shared_sections = ipc1 & ipc2
            shared_issues = set(case1.get("annotations", {}).get("issues", [])) & set(case2.get("annotations", {}).get("issues", []))

            is_coherent = len(shared_sections) > 0 or len(shared_issues) > 0
            if is_coherent: coherent_count += 1

            print(f"Pair: {s_id} <-> {t_id}")
            print(f"  Shared IPC: {list(shared_sections) if shared_sections else 'None'}")
            print(f"  Shared Issues: {len(shared_issues)} found")
            print(f"  Result: {'COHERENT' if is_coherent else 'DIVERGENT'}")
            print("-" * 20)

        print(f"Coherence Rate (High Strength): {coherent_count/len(sample_pairs)*100:.1f}%")

    # Test 2: Batch Listing Candidates
    if Path(clusters_file).exists():
        print(f"\nTest 2: Batch Listing Opportunities")
        print("-" * 50)
        with open(clusters_file, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        batch_candidates = [c for c in clusters if c.get("count", 0) >= 3]
        print(f"Found {len(batch_candidates)} clusters with 3+ members (Batch Listing Candidates)")
        for c in batch_candidates[:5]:
            print(f"  Cluster {c['cluster_id']}: {c['count']} cases")
            basis = c.get("basis", {})
            if basis.get("sections"):
                print(f"    Basis Sections: {', '.join(basis['sections'][:3])}")
            if basis.get("issues"):
                print(f"    Basis Issues: {', '.join(basis['issues'][:2])}")

if __name__ == "__main__":
    validate_similarity(
        "legal_ai_toolkit/data/judgments",
        "annotations/similarity/edges.jsonl",
        "annotations/similarity/clusters.json"
    )
