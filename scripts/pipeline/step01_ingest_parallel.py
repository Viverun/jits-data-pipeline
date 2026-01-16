import os
import json
import re
from datetime import datetime
import sys
from pathlib import Path
from multiprocessing import Pool, cpu_count
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.utils.id_generator import generate_judgment_id

def normalize_text(text: str) -> str:
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def paragraphize(text: str):
    paras = []
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    for i, p in enumerate(raw_paras, start=1):
        paras.append({"para_id": i, "text": p})
    return paras

def process_single_file(args):
    """Process a single file - designed for parallel execution"""
    file_path, output_dir = args
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        clean_text = normalize_text(raw_text)
        paragraphs = paragraphize(clean_text)

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

        out_path = os.path.join(output_dir, judgment_id + ".json")
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(output, out, indent=2, ensure_ascii=False)

        return (True, file_path.name, judgment_id)
    except Exception as e:
        return (False, file_path.name, str(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="raw/judgments/unclassified")
    parser.add_argument("--output-dir", default="interim/normalized_text")
    parser.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    args = parser.parse_args()

    RAW_DIR = args.input_dir
    OUT_DIR = args.output_dir
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(RAW_DIR):
        print(f"[ERROR] RAW_DIR not found: {RAW_DIR}")
        return

    files = [Path(RAW_DIR) / f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not files:
        print(f"[WARNING] No .txt files found in {RAW_DIR}")
        return

    print(f"[OK] Found {len(files)} files. Using {args.workers} workers.")
    
    # Prepare arguments for parallel processing
    process_args = [(f, OUT_DIR) for f in files]
    
    # Parallel processing
    with Pool(args.workers) as pool:
        results = pool.map(process_single_file, process_args)
    
    # Report results
    successes = sum(1 for r in results if r[0])
    failures = [r for r in results if not r[0]]
    
    print(f"\n[OK] Processed {successes}/{len(files)} files successfully")
    if failures:
        print(f"[WARNING] {len(failures)} failures:")
        for _, fname, error in failures[:10]:  # Show first 10 errors
            print(f"  - {fname}: {error}")

if __name__ == "__main__":
    main()
