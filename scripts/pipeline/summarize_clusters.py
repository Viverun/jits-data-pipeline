import json
import os

CLUSTER_FILE = "annotations/similarity/clusters.json"
SIGNAL_DIR = "annotations/similarity/signals"

def main():
    if not os.path.exists(CLUSTER_FILE):
        print("Cluster file not found")
        return

    with open(CLUSTER_FILE, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    print(f"📊 JITS v0.2 Cluster Summary ({len(clusters)} Clusters)\n")

    for c in clusters:
        print(f"ID: {c['cluster_id']} ({c['count']} judgments)")
        print(f"Centroid: {c['centroid']}")
        
        # Load centroid signals to see the theme
        signal_path = os.path.join(SIGNAL_DIR, f"{c['centroid']}.json")
        if os.path.exists(signal_path):
            with open(signal_path, "r", encoding="utf-8") as sf:
                sig = json.load(sf)
                print(f"  Themes: {', '.join(sig['issues'][:5])}")
                print(f"  Key Sections: {', '.join(sig['sections'][:5])}")
        print("-" * 40)

if __name__ == "__main__":
    main()
