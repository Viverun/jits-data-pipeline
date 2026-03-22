import os
import json
import re
import hashlib
from pathlib import Path
from multiprocessing import Pool, cpu_count

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


def build_temporary_judgment_id(relative_path: str, clean_text: str) -> str:
    """
    Build a deterministic ingestion-time ID.

    We include the source-relative path as well as the normalized text so
    judgments with near-identical headers do not overwrite one another during
    ingestion.
    """
    temp_hash = hashlib.sha1(f"{relative_path}\0{clean_text}".encode("utf-8")).hexdigest()[:12].upper()
    return f"TEMP_{temp_hash}"

def process_single_file(args):
    file_path, input_dir, output_dir = args

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        clean_text = normalize_text(raw_text)
        paragraphs = paragraphize(clean_text)
        relative_path = str(Path(file_path).relative_to(input_dir).as_posix())

        metadata = {
            "court": "UNKNOWN",
            "court_level": "UNKNOWN",
            "jurisdiction": "India",
            "year": "UNKNOWN",
        }

        # Generate TEMPORARY ID during ingestion
        # This will be regenerated in MetadataExtractionStep with proper metadata
        temp_id = build_temporary_judgment_id(relative_path, clean_text)

        data = {
            "judgment_id": temp_id,
            "metadata": metadata,
            "text": clean_text,
            "paragraphs": paragraphs,
            "annotations": {},
            "provenance": {
                "source_file": relative_path,
                "ingestion_step": "ingestion",
            },
        }

        out_path = Path(output_dir) / f"{temp_id}.json"
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
        args = [(f, self.input_dir, self.output_dir) for f in files]

        with Pool(workers) as pool:
            results = pool.map(process_single_file, args)

        success_count = sum(1 for r in results if r)
        print(f"Successfully ingested {success_count}/{len(files)} judgments.")
