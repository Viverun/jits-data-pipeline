import os
import json
import sys
from pathlib import Path

# Add project root to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.utils.citation_extractor import CitationExtractor

INPUT_DIR = "interim/issues_extracted"
OUTPUT_DIR = "interim/citations_extracted"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    if not files:
        print(f"[WARNING] No .json files found in {INPUT_DIR}")
        return

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        text = data.get("text", "")
        # Ensure annotations object exists
        if "annotations" not in data:
            data["annotations"] = {}
            
        # Extract citations using the utility
        citations = CitationExtractor.extract(text)
        data["annotations"]["citations"] = citations

        out_path = Path(OUTPUT_DIR) / file.name
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

        print(f"[OK] Citations extracted: {file.name} ({len(citations)} citations found)")

    print(f"\n[OK] Step 06 complete — citations extracted across files.")

if __name__ == "__main__":
    main()
