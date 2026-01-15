import json
import os
from collections import Counter

EDGE_FILE = "annotations/similarity/edges.jsonl"
UNIVERSAL_ISSUES = {"jurisdiction", "maintainability", "limitation"}

def main():
    if not os.path.exists(EDGE_FILE):
        print("File not found")
        return

    weights = []
    strengths = Counter()
    
    with open(EDGE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            edge = json.loads(line)
            strengths[edge["strength"]] += 1
            
            shared_specific_issues = set(edge["signals"].get("shared_issues", [])) - UNIVERSAL_ISSUES
            shared_sections = set(edge["signals"].get("shared_sections", []))
            shared_citations = set(edge["signals"].get("shared_citations", []))
            
            weight = len(shared_specific_issues) + len(shared_sections) + len(shared_citations)
            weights.append(weight)

    print(f"Total Edges: {len(weights)}")
    print(f"Strengths: {dict(strengths)}")
    
    weight_counts = Counter(weights)
    print("Weight Distribution:")
    for w in sorted(weight_counts.keys()):
        print(f"  Weight {w}: {weight_counts[w]} edges")

if __name__ == "__main__":
    main()
