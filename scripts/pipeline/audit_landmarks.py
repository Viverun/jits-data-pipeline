import json
import os
from collections import Counter

PROCESSED_DIR = "processed/judgments"

def main():
    if not os.path.exists(PROCESSED_DIR):
        print("Processed directory not found")
        return

    landmark_counts = Counter()
    total_cases = 0
    cases_with_landmarks = 0

    for file in os.listdir(PROCESSED_DIR):
        if not file.endswith(".json"): continue
        total_cases += 1
        
        with open(os.path.join(PROCESSED_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            landmarks = data.get("annotations", {}).get("matched_landmarks", [])
            
            if landmarks:
                cases_with_landmarks += 1
                for lm in landmarks:
                    landmark_counts[lm["short_name"]] += 1

    print(f"🏛️ JITS Landmark Audit ({total_cases} Cases)\n")
    print(f"Cases citing landmarks: {cases_with_landmarks} ({cases_with_landmarks/total_cases*100:.1f}%)")
    print("\nTop Cited Landmarks:")
    for name, count in landmark_counts.most_common(10):
        print(f"  - {name}: {count} citations")

if __name__ == "__main__":
    main()
