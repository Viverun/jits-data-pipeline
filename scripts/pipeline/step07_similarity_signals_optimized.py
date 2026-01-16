import os
import json
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool, cpu_count
import argparse

INPUT_DIR = "interim/citations_extracted"
SIGNAL_DIR = "annotations/similarity/signals"
EDGE_FILE = "annotations/similarity/edges.jsonl"

os.makedirs(SIGNAL_DIR, exist_ok=True)

# Universal filters (from your v0.2.3)
UNIVERSAL_ISSUES = {"jurisdiction", "maintainability", "limitation"}
UNIVERSAL_SECTIONS = {
    "IPC 1", "IPC 2", "IPC 3", "IPC 4", "IPC 5", "IPC 6", "IPC 7", "IPC 8", "IPC 9", "IPC 10",
    "IPC 34", "IPC 120B", "IPC 149"
}

def extract_signals(data):
    """Extracts core similarity signals from a judgment's annotations."""
    signals = {
        "judgment_id": data["judgment_id"],
        "issues": list(data.get("annotations", {}).get("issues", {}).keys()),
        "sections": [],
        "citations": [],
        "domain": data.get("classification", {}).get("domain", "unknown")
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

    # Deduplicate and filter
    signals["sections"] = list(set(signals["sections"]) - UNIVERSAL_SECTIONS)
    signals["citations"] = list(set(signals["citations"]))
    signals["issues"] = list(set(signals["issues"]) - UNIVERSAL_ISSUES)
    
    return signals

def calculate_similarity_batch(args):
    """Process a batch of pairs in parallel"""
    pair_batch, all_signals_dict = args
    edges = []
    
    for sig1_id, sig2_id in pair_batch:
        sig1 = all_signals_dict[sig1_id]
        sig2 = all_signals_dict[sig2_id]
        
        # Skip cross-domain pairs for efficiency (optional optimization)
        if sig1["domain"] != sig2["domain"] and sig1["domain"] != "mixed" and sig2["domain"] != "mixed":
            continue
        
        shared_issues = list(set(sig1["issues"]) & set(sig2["issues"]))
        shared_sections = list(set(sig1["sections"]) & set(sig2["sections"]))
        shared_citations = list(set(sig1["citations"]) & set(sig2["citations"]))

        if not (shared_issues or shared_sections or shared_citations):
            continue

        # Calculate weight (your v0.2.3 logic)
        weight = len(shared_issues) + len(shared_sections) + len(shared_citations)
        
        # Determine strength
        strength = "low"
        if weight >= 10:  # Your high-precision threshold
            strength = "high"
        elif weight >= 5:
            strength = "medium"

        edge = {
            "from": sig1_id,
            "to": sig2_id,
            "signals": {
                "shared_issues": shared_issues,
                "shared_sections": shared_sections,
                "shared_citations": shared_citations
            },
            "weight": weight,
            "strength": strength
        }
        edges.append(edge)
    
    return edges

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    parser.add_argument("--batch-size", type=int, default=1000, help="Pairs per batch")
    args = parser.parse_args()
    
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    if not files:
        print(f"[WARNING] No .json files found in {INPUT_DIR}")
        return

    # Extract all signals first
    print(f"[OK] Extracting signals from {len(files)} judgments...")
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

    # Create lookup dict for parallel processing
    all_signals_dict = {s["judgment_id"]: s for s in all_signals}
    
    # Generate all pairs
    all_pairs = list(combinations([s["judgment_id"] for s in all_signals], 2))
    total_pairs = len(all_pairs)
    print(f"[OK] Signals extracted. Computing {total_pairs:,} pairwise similarities...")
    
    # Split pairs into batches for parallel processing
    batches = []
    for i in range(0, len(all_pairs), args.batch_size):
        batch = all_pairs[i:i + args.batch_size]
        batches.append((batch, all_signals_dict))
    
    print(f"[OK] Processing in {len(batches)} batches using {args.workers} workers...")
    
    # Parallel processing
    with Pool(args.workers) as pool:
        batch_results = pool.map(calculate_similarity_batch, batches)
    
    # Flatten results
    all_edges = [edge for batch in batch_results for edge in batch]
    
    # Write edges
    print(f"[OK] Writing {len(all_edges):,} similarity edges...")
    with open(EDGE_FILE, "w", encoding="utf-8") as ef:
        for edge in all_edges:
            ef.write(json.dumps(edge, ensure_ascii=False) + "\n")

    print(f"[OK] Similarity computation complete:")
    print(f"  - Total pairs evaluated: {total_pairs:,}")
    print(f"  - Edges created: {len(all_edges):,}")
    print(f"  - Edge ratio: {len(all_edges)/total_pairs*100:.2f}%")

if __name__ == "__main__":
    main()
