import os
import json
import shutil
from pathlib import Path

IN_DIR = "interim/citations_extracted"
OUT_DIR = "processed/judgments"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    if not os.path.exists(IN_DIR):
        print(f"[ERROR] IN_DIR not found: {IN_DIR}")
        return

    files = list(Path(IN_DIR).glob("*.json"))
    if not files:
        print(f"[WARNING] No .json files found in {IN_DIR}")
        return

    count = 0
    for file in files:
        shutil.copy(file, Path(OUT_DIR) / file.name)
        count += 1

    print(f"[OK] Consolidated {count} judgments to {OUT_DIR}")

if __name__ == "__main__":
    main()
