import json
import os
from collections import Counter

PROCESSED_DIR = "processed/judgments"

def check_unmapped():
    unmapped_counter = Counter()
    
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")]
    
    for f in files:
        with open(os.path.join(PROCESSED_DIR, f), "r", encoding="utf-8") as jf:
            data = json.load(jf)
            unmapped = data.get("statutory_transitions", {}).get("unmapped_ipc", [])
            for sec in unmapped:
                unmapped_counter[sec] += 1

    print("📋 Top 20 Unmapped IPC Sections (Potential Noise or Missing Mappings):")
    for sec, count in unmapped_counter.most_common(20):
        print(f"  - {sec}: {count} occurrences")

if __name__ == "__main__":
    check_unmapped()
