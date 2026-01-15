import os
import json
import re
from datetime import datetime
import sys

# Add project root to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.utils.id_generator import generate_judgment_id

RAW_DIR = "raw/judgments/unclassified"
OUT_DIR = "interim/normalized_text"
os.makedirs(OUT_DIR, exist_ok=True)

def normalize_text(text: str) -> str:
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def paragraphize(text: str):
    paras = []
    # Split by double newline to identify paragraphs
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    for i, p in enumerate(raw_paras, start=1):
        paras.append({
            "para_id": i,
            "text": p
        })
    return paras

def main():
    if not os.path.exists(RAW_DIR):
        print(f"❌ RAW_DIR not found: {RAW_DIR}")
        return

    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not files:
        print(f"⚠️ No .txt files found in {RAW_DIR}")
        return

    for file in files:
        file_path = os.path.join(RAW_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        clean_text = normalize_text(raw_text)
        paragraphs = paragraphize(clean_text)

        # Minimal metadata for now
        metadata = {
            "court": "UNKNOWN",
            "court_level": "UNKNOWN",
            "jurisdiction": "India",
            "year": datetime.now().year
        }

        judgment_id = generate_judgment_id(
            court_level="UNK",
            court_code="UNK",
            year=metadata["year"],
            domain="unknown",
            text=clean_text
        )

        output = {
            "judgment_id": judgment_id,
            "metadata": metadata,
            "text": clean_text,
            "paragraphs": paragraphs,
            "annotations": {}
        }

        out_path = os.path.join(
            OUT_DIR,
            judgment_id + ".json"
        )

        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(output, out, indent=2, ensure_ascii=False)

        print(f"✅ Ingested: {file} → {judgment_id}")

if __name__ == "__main__":
    main()
