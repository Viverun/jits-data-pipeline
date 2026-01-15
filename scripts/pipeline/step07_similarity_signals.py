import os
import json
from pathlib import Path
from itertools import combinations

INPUT_DIR = "interim/citations_extracted"
SIGNAL_DIR = "annotations/similarity/signals"
EDGE_FILE = "annotations/similarity/edges.jsonl"

os.makedirs(SIGNAL_DIR, exist_ok=True)

def extract_signals(data):
    """Extracts core similarity signals from a judgment's annotations."""
    signals = {
        "judgment_id": data["judgment_id"],
        "issues": list(data.get("annotations", {}).get("issues", {}).keys()),
        "sections": [],
        "citations": []
    }

    # Extract sections from statutory transitions
    transitions = data.get("statutory_transitions", {})
    if transitions:
        signals["sections"].extend(transitions.get("ipc_detected", []))
        for m in transitions.get("bns_mapped", []):
            signals["sections"].append(m["bns"])

    # Extract citations
    citations = data.get("annotations", {}).get("citations", [])
    for c in citations:
        if "raw" in c:
            signals["citations"].append(c["raw"])

    # Deduplicate
    signals["sections"] = list(set(signals["sections"]))
    signals["citations"] = list(set(signals["citations"]))
    
    return signals

def calculate_similarity(sig1, sig2):
    """Calculates pairwise similarity evidence between two signal sets."""
    shared_issues = list(set(sig1["issues"]) & set(sig2["issues"]))
    shared_sections = list(set(sig1["sections"]) & set(sig2["sections"]))
    shared_citations = list(set(sig1["citations"]) & set(sig2["citations"]))

    if not (shared_issues or shared_sections or shared_citations):
        return None

    # Determine strength
    overlap_count = sum([1 for x in [shared_issues, shared_sections, shared_citations] if x])
    
    strength = "low"
    if overlap_count >= 2:
        strength = "high"
    elif shared_issues or shared_citations:
        strength = "medium"

    return {
        "from": sig1["judgment_id"],
        "to": sig2["judgment_id"],
        "signals": {
            "shared_issues": shared_issues,
            "shared_sections": shared_sections,
            "shared_citations": shared_citations
        },
        "strength": strength
    }

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    if not files:
        print(f"[WARNING] No .json files found in {INPUT_DIR}")
        return

    all_signals = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        signals = extract_signals(data)
        all_signals.append(signals)

        # Save per-judgment signal dump
        signal_path = Path(SIGNAL_DIR) / f"{data['judgment_id']}.json"
        with open(signal_path, "w", encoding="utf-8") as out:
            json.dump(signals, out, indent=2, ensure_ascii=False)

    print(f"[OK] Signals extracted: {len(all_signals)} judgments")

    # Generate pairwise edges
    edge_count = 0
    with open(EDGE_FILE, "w", encoding="utf-8") as ef:
        for sig1, sig2 in combinations(all_signals, 2):
            edge = calculate_similarity(sig1, sig2)
            if edge:
                ef.write(json.dumps(edge, ensure_ascii=False) + "\n")
                edge_count += 1

    print(f"[OK] Similarity edges created: {edge_count}")

if __name__ == "__main__":
    main()
