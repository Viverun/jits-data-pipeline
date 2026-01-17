import os
import json
import re
from datetime import datetime
from pathlib import Path
from multiprocessing import Pool, cpu_count
from legal_ai_toolkit.utils.ids import generate_judgment_id

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

        data = {
            "judgment_id": judgment_id,
            "metadata": metadata,
            "text": clean_text,
            "paragraphs": paragraphs,
            "annotations": {}
        }

        out_path = Path(output_dir) / f"{judgment_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False

class IngestionProcessor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, workers=None):
        if workers is None:
            workers = max(1, cpu_count() - 1)

        files = list(self.input_dir.rglob("*.txt"))
        if not files:
            print(f"No .txt files found in {self.input_dir}")
            return

        print(f"Ingesting {len(files)} files with {workers} workers...")
        args = [(f, self.output_dir) for f in files]

        with Pool(workers) as pool:
            results = pool.map(process_single_file, args)

        success_count = sum(1 for r in results if r)
        print(f"Successfully ingested {success_count}/{len(files)} judgments.")
