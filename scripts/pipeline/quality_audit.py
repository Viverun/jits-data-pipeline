import json
import os
from pathlib import Path

PROCESSED_DIR = "processed/judgments"
CLUSTER_FILE = "annotations/similarity/clusters_refined.json"

def audit_dataset():
    print("🔍 Starting JITS Quality Audit (Refined)...\n")
    
    if not os.path.exists(PROCESSED_DIR):
        print(f"❌ Error: {PROCESSED_DIR} not found.")
        return

    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")]
    total_cases = len(files)
    
    if total_cases == 0:
        print("❌ No processed judgments found.")
        return
    
    empty_metadata = 0
    empty_annotations = 0
    landmark_coverage = 0
    domain_stats = {"civil": 0, "criminal": 0, "service": 0, "mixed": 0, "unknown": 0}
    
    for f in files:
        with open(os.path.join(PROCESSED_DIR, f), "r", encoding="utf-8") as jf:
            data = json.load(jf)
            
            meta = data.get("metadata", {})
            if not meta.get("court") or meta.get("court") == "UNKNOWN":
                empty_metadata += 1
            
            anno = data.get("annotations", {})
            if not anno.get("issues") and not anno.get("citations"):
                empty_annotations += 1
                
            if anno.get("matched_landmarks"):
                landmark_coverage += 1
            
            domain = data.get("classification", {}).get("domain", "unknown")
            domain_stats[domain] = domain_stats.get(domain, 0) + 1

    total_clustered = 0
    cluster_count = 0
    if os.path.exists(CLUSTER_FILE):
        with open(CLUSTER_FILE, "r", encoding="utf-8") as cf:
            clusters = json.load(cf)
            cluster_count = len(clusters)
            total_clustered = sum(c["count"] for c in clusters)

    print(f"📊 Dataset Health Report:")
    print(f"  - Total Judgments: {total_cases}")
    print(f"  - Metadata Quality: {(total_cases - empty_metadata)/total_cases*100:.1f}%")
    print(f"  - Annotation Density: {(total_cases - empty_annotations)/total_cases*100:.1f}%")
    print(f"  - Landmark Authority: {landmark_coverage/total_cases*100:.1f}%")
    print(f"  - Clustering Efficiency: {total_clustered/total_cases*100:.1f}% ({total_clustered} cases in {cluster_count} refined clusters)")
    
    print("\n⚖️ Domain Distribution:")
    # Sort by count descending
    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1], reverse=True)
    for domain, count in sorted_domains:
        print(f"  - {domain.capitalize()}: {count} ({count/total_cases*100:.1f}%)")
    
    print("\n✅ Audit Complete.")

if __name__ == "__main__":
    audit_dataset()
