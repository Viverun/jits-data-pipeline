import os
import json
import re
from datetime import datetime

IN_DIR = "interim/normalized_text"
OUT_DIR = "interim/headers_extracted"
os.makedirs(OUT_DIR, exist_ok=True)

COURT_PATTERNS = [
    r"SUPREME COURT OF INDIA",
    r"HIGH COURT OF ([A-Z ]+)",
    r"DISTRICT COURT",
    r"SESSIONS COURT"
]

DATE_PATTERNS = [
    r"Date of Decision[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Decided on[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})"
]

CASE_NO_PATTERN = r"(Criminal|Civil|Writ|Appeal|Revision)[^\n]{0,40}No\.?\s*[0-9/ -]+"

def extract_header_metadata(text: str):
    lines = text.split("\n")[:30]
    header = " ".join(lines).upper()

    metadata = {
        "court": None,
        "court_level": None,
        "case_number": None,
        "decision_date": None,
        "jurisdiction": "India"
    }

    for pattern in COURT_PATTERNS:
        match = re.search(pattern, header)
        if match:
            metadata["court"] = match.group(0).title()
            if "SUPREME" in match.group(0):
                metadata["court_level"] = "SC"
            elif "HIGH" in match.group(0):
                metadata["court_level"] = "HC"
            else:
                metadata["court_level"] = "District"
            break

    case_match = re.search(CASE_NO_PATTERN, header)
    if case_match:
        metadata["case_number"] = case_match.group(0).title()

    for dp in DATE_PATTERNS:
        dmatch = re.search(dp, header)
        if dmatch:
            metadata["decision_date"] = dmatch.group(1)
            break

    return metadata

def main():
    if not os.path.exists(IN_DIR):
        print(f"❌ IN_DIR not found: {IN_DIR}")
        return

    files = [f for f in os.listdir(IN_DIR) if f.endswith(".json")]
    if not files:
        print(f"⚠️ No .json files found in {IN_DIR}. Did you run Step 01?")
        return

    for file in files:
        with open(os.path.join(IN_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        extracted = extract_header_metadata(data["text"])

        # Merge metadata (do not overwrite existing unless found)
        for k, v in extracted.items():
            if v:
                data["metadata"][k] = v

        out_path = os.path.join(OUT_DIR, file)
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

        print(f"✅ Metadata extracted: {data['judgment_id']}")

if __name__ == "__main__":
    main()
