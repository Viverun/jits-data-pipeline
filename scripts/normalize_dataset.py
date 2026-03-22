import argparse
import json
from datetime import datetime
from pathlib import Path
from collections import Counter


DEFAULT_INPUT_DIR = "legal_ai_toolkit/data/judgments"
DEFAULT_OUTPUT_FILE = "train.jsonl"


def normalize_string(value):
    return str(value) if value is not None else ""


def normalize_list(value):
    return value if isinstance(value, list) else []


def normalize_dict(value):
    return value if isinstance(value, dict) else {}


def normalize_decision_date(value):
    text = normalize_string(value).strip()
    if not text or text.upper() == "UNKNOWN":
        return None

    try:
        return datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def is_unknown(value) -> bool:
    text = normalize_string(value).strip()
    return not text or text.upper() == "UNKNOWN"


def should_export_record(
    data,
    *,
    exclude_unknown_cases: bool = True,
    exclude_unknown_domain: bool = False,
):
    metadata = normalize_dict(data.get("metadata"))
    classification = normalize_dict(data.get("classification"))
    judgment_id = normalize_string(data.get("judgment_id")).strip()

    if exclude_unknown_cases:
        if judgment_id.startswith("IN-UNKNOWN-UNK-"):
            return False, "unknown_id"
        if "-0000-" in judgment_id:
            return False, "unknown_year_id"
        if is_unknown(metadata.get("court")) or is_unknown(metadata.get("court_level")):
            return False, "unknown_court"

    if exclude_unknown_domain and is_unknown(classification.get("domain")):
        return False, "unknown_domain"

    return True, None


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
            "decision_date": normalize_decision_date(metadata.get("decision_date")),
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


def export_jsonl(
    input_dir: Path,
    output_file: Path,
    *,
    exclude_unknown_cases: bool = True,
    exclude_unknown_domain: bool = False,
):
    files = sorted(input_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No processed JSON files found in {input_dir}")

    count = 0
    skipped = Counter()
    with output_file.open("w", encoding="utf-8") as out_f:
        for file_path in files:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            include, reason = should_export_record(
                data,
                exclude_unknown_cases=exclude_unknown_cases,
                exclude_unknown_domain=exclude_unknown_domain,
            )
            if not include:
                skipped[reason] += 1
                continue
            out_f.write(json.dumps(normalize_record(data), ensure_ascii=False) + "\n")
            count += 1

    return count, skipped


def validate_release_quality(output_file: Path):
    unknown_year_ids = []
    with Path(output_file).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            judgment_id = normalize_string(record.get("judgment_id")).strip()
            if "-0000-" in judgment_id:
                unknown_year_ids.append((line_no, judgment_id))

    if unknown_year_ids:
        preview = ", ".join(judgment_id for _, judgment_id in unknown_year_ids[:5])
        raise ValueError(
            "Release gate failed: found judgment IDs with year 0000 in export: "
            f"{len(unknown_year_ids)} records (examples: {preview})"
        )


def main():
    parser = argparse.ArgumentParser(description="Export current processed judgments to train.jsonl")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT_FILE)
    parser.add_argument(
        "--include-unknown-cases",
        action="store_true",
        help="Include records with UNKNOWN court / IN-UNKNOWN-UNK identifiers in the export.",
    )
    parser.add_argument(
        "--exclude-unknown-domain",
        action="store_true",
        help="Exclude records whose classified domain is UNKNOWN.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)

    count, skipped = export_jsonl(
        input_dir,
        output_file,
        exclude_unknown_cases=not args.include_unknown_cases,
        exclude_unknown_domain=args.exclude_unknown_domain,
    )
    validate_release_quality(output_file)
    print(f"Successfully wrote {count} records to {output_file}")
    if skipped:
        summary = ", ".join(f"{reason}={count}" for reason, count in sorted(skipped.items()))
        print(f"Skipped records: {summary}")


if __name__ == "__main__":
    main()
