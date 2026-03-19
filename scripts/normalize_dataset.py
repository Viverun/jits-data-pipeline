import argparse
import json
from pathlib import Path


DEFAULT_INPUT_DIR = "legal_ai_toolkit/data/judgments"
DEFAULT_OUTPUT_FILE = "train.jsonl"


def normalize_string(value):
    return str(value) if value is not None else ""


def normalize_list(value):
    return value if isinstance(value, list) else []


def normalize_dict(value):
    return value if isinstance(value, dict) else {}


def normalize_record(data):
    metadata = normalize_dict(data.get("metadata"))
    classification = normalize_dict(data.get("classification"))
    extractions = normalize_dict(data.get("extractions"))
    provenance = normalize_dict(data.get("provenance"))
    statutory_transitions = data.get("statutory_transitions", [])

    if isinstance(statutory_transitions, dict):
        statutory_transitions = normalize_list(statutory_transitions.get("transitions"))
    else:
        statutory_transitions = normalize_list(statutory_transitions)

    return {
        "judgment_id": normalize_string(data.get("judgment_id")),
        "text": normalize_string(data.get("text")),
        "metadata": {
            "court": normalize_string(metadata.get("court")),
            "court_level": normalize_string(metadata.get("court_level")),
            "decision_date": normalize_string(metadata.get("decision_date")),
            "case_number": normalize_string(metadata.get("case_number")),
            "jurisdiction": normalize_string(metadata.get("jurisdiction")),
            "petitioner": normalize_string(metadata.get("petitioner")),
            "respondent": normalize_string(metadata.get("respondent")),
            "bench": metadata.get("bench", []),
        },
        "classification": {
            "domain": normalize_string(classification.get("domain")),
            "confidence": normalize_string(classification.get("confidence", "low")),
            "signals": normalize_dict(classification.get("signals")),
            "reasoning": normalize_list(classification.get("reasoning")),
        },
        "extractions": {
            "citations": normalize_dict(extractions.get("citations")),
            "sections": normalize_dict(extractions.get("sections")),
            "transitions": normalize_dict(extractions.get("transitions")),
            "landmarks": normalize_dict(extractions.get("landmarks")),
            "issues": normalize_dict(extractions.get("issues")),
        },
        "statutory_transitions": statutory_transitions,
        "provenance": {
            "pipeline_version": normalize_string(provenance.get("pipeline_version", provenance.get("version", "2.0"))),
            "processed_date": normalize_string(provenance.get("processed_date")),
            "processing_steps": normalize_list(provenance.get("processing_steps")),
        },
    }


def export_jsonl(input_dir: Path, output_file: Path) -> int:
    files = sorted(input_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No processed JSON files found in {input_dir}")

    count = 0
    with output_file.open("w", encoding="utf-8") as out_f:
        for file_path in files:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            out_f.write(json.dumps(normalize_record(data), ensure_ascii=False) + "\n")
            count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Export current processed judgments to train.jsonl")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT_FILE)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)

    count = export_jsonl(input_dir, output_file)
    print(f"Successfully wrote {count} records to {output_file}")


if __name__ == "__main__":
    main()
