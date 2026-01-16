import json
import os
from pathlib import Path

PROCESSED_DIR = "processed/judgments"
CLUSTER_FILE = "annotations/similarity/clusters.json"
EDGE_FILE = "annotations/similarity/edges.jsonl"

def audit_dataset():
    print("🔍 Starting JITS Quality Audit...\n")
    
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")]
    total_cases = len(files)
    
    issues_found = 0
    empty_metadata = 0
    empty_annotations = 0
    landmark_coverage = 0
    
    for f in files:
        with open(os.path.join(PROCESSED_DIR, f), "r", encoding="utf-8") as jf:
            data = json.load(jf)
            
            # 1. Check Metadata
            meta = data.get("metadata", {})
            if not meta.get("court") or meta.get("court") == "UNKNOWN":
                empty_metadata += 1
            
            # 2. Check Annotations
            anno = data.get("annotations", {})
            if not anno.get("issues") and not anno.get("citations"):
                empty_annotations += 1
                
            # 3. Check Landmarks
            if anno.get("matched_landmarks"):
                landmark_coverage += 1

    # 4. Check Clusters
    with open(CLUSTER_FILE, "r", encoding="utf-8") as cf:
        clusters = json.load(cf)
        total_clustered = sum(c["count"] for c in clusters)

    print(f"📊 Dataset Health Report:")
    print(f"  - Total Judgments: {total_cases}")
    print(f"  - Metadata Quality: {(total_cases - empty_metadata)/total_cases*100:.1f}% (Cases with identified courts)")
    print(f"  - Annotation Density: {(total_cases - empty_annotations)/total_cases*100:.1f}% (Cases with issues/citations)")
    print(f"  - Landmark Authority: {landmark_coverage/total_cases*100:.1f}% (Cases linked to precedents)")
    print(f"  - Clustering Efficiency: {total_clustered/total_cases*100:.1f}% (Cases assigned to high-precision groups)")
    
    print("\n✅ Audit Complete.")

if __name__ == "__main__":
    audit_dataset()
