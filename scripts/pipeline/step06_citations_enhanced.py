import os
import json
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.utils.citation_extractor import CitationExtractor
from scripts.utils.precedent_database import PrecedentDatabase

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

    total_citations = 0
    total_landmarks = 0

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        text = data.get("text", "")
        if "annotations" not in data:
            data["annotations"] = {}
            
        # Extract citations
        citations = CitationExtractor.extract(text)
        
        # Match against landmark database
        matched_landmarks = []
        for citation in citations:
            citation_text = citation.get("raw", "")
            precedent = PrecedentDatabase.match_citation(citation_text)
            if precedent:
                matched_landmarks.append(precedent)
                citation["is_landmark"] = True
                citation["precedent_id"] = precedent["precedent_id"]
                total_landmarks += 1
            else:
                citation["is_landmark"] = False
        
        data["annotations"]["citations"] = citations
        data["annotations"]["matched_landmarks"] = matched_landmarks
        
        # Find potentially relevant precedents based on issues
        if "issues" in data.get("annotations", {}):
            issues = list(data["annotations"]["issues"].keys())
            sections = []
            if "statutory_transitions" in data:
                sections = data["statutory_transitions"].get("ipc_detected", [])
            
            relevant_precedents = PrecedentDatabase.find_relevant_precedents(issues, sections)
            data["annotations"]["suggested_precedents"] = relevant_precedents[:5]  # Top 5

        out_path = Path(OUTPUT_DIR) / file.name
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

        total_citations += len(citations)
        print(f"[OK] Citations extracted: {file.name} ({len(citations)} citations, {len(matched_landmarks)} landmarks)")

    print(f"\n[OK] Step 06 complete:")
    print(f"  - Total citations: {total_citations}")
    print(f"  - Landmark matches: {total_landmarks}")

if __name__ == "__main__":
    main()
