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


def normalize_bench(value):
    """Always return bench as list[str] for HF Arrow stability.

    Legacy corpus mixes str (present) with [] (missing). HF infers a
    conflicting str vs list type and parquet conversion fails.
    """
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text and text.upper() != "UNKNOWN":
                out.append(text)
        return out
    text = str(value).strip()
    if not text or text.upper() == "UNKNOWN":
        return []
    # extract_bench() joins multiple judges with " | "
    if " | " in text:
        return [part.strip() for part in text.split(" | ") if part.strip()]
    return [text]


TRANSITION_FIELDS = (
    "ipc",
    "bns",
    "source",
    "validated",
    "risk",
    "confidence",
    "note",
    "context_snippet",
    "requires_judicial_confirmation",
    "temporal_warning",
)


def normalize_transition(item):
    """Coerce any transition dict to the canonical 10-field struct.

    Fixes HF error: Couldn't cast struct<ipc,bns,...requires_judicial_confirmation,
    context_snippet> to {ipc,bns:null,...} caused by three producers emitting
    different key sets.
    """
    if not isinstance(item, dict):
        return {k: None for k in TRANSITION_FIELDS}
    return {
        "ipc": item.get("ipc"),
        "bns": item.get("bns"),
        "source": item.get("source"),
        "validated": bool(item.get("validated", False)),
        "risk": item.get("risk"),
        "confidence": item.get("confidence"),
        "note": item.get("note"),
        "context_snippet": item.get("context_snippet"),
        "requires_judicial_confirmation": bool(item.get("requires_judicial_confirmation", False)),
        "temporal_warning": item.get("temporal_warning"),
    }


def normalize_transitions_block(value):
    block = normalize_dict(value)
    details = block.get("details", [])
    if not isinstance(details, list):
        details = []
    norm_details = [normalize_transition(d) for d in details if isinstance(d, dict)]
    by_source = {}
    for d in norm_details:
        src = d.get("source") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
    return {
        "total": len(norm_details),
        "by_source": by_source,
        "details": norm_details,
    }


CITATION_FIELDS = (
    "type",
    "reporter",
    "year",
    "page",
    "volume",
    "court",
    "petitioner",
    "respondent",
    "case_name",
    "raw",
    "start_pos",
    "end_pos",
    "is_landmark",
    "precedent_id",
)


def _as_int_or_none(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_citation(item):
    if not isinstance(item, dict):
        return {k: None for k in CITATION_FIELDS}
    return {
        "type": item.get("type"),
        "reporter": item.get("reporter"),
        "year": item.get("year"),
        "page": item.get("page"),
        "volume": item.get("volume"),
        "court": item.get("court"),
        "petitioner": item.get("petitioner"),
        "respondent": item.get("respondent"),
        "case_name": item.get("case_name"),
        "raw": item.get("raw"),
        "start_pos": _as_int_or_none(item.get("start_pos")),
        "end_pos": _as_int_or_none(item.get("end_pos")),
        "is_landmark": bool(item.get("is_landmark", False)),
        "precedent_id": item.get("precedent_id"),
    }


def normalize_citations_block(value):
    block = normalize_dict(value)
    details = block.get("details", [])
    if not isinstance(details, list):
        details = []
    norm_details = [normalize_citation(d) for d in details if isinstance(d, dict)]
    by_type = {}
    for d in norm_details:
        t = d.get("type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1
    return {
        "total": len(norm_details),
        "by_type": by_type,
        "details": norm_details,
    }


def normalize_landmark(item):
    if not isinstance(item, dict):
        return {
            "precedent_id": None,
            "full_citation": None,
            "short_name": None,
            "aliases": [],
            "year": None,
            "court": None,
            "bench_strength": None,
            "legal_principle": None,
            "issues": [],
            "keywords": [],
            "provisions": [],
            "binding_authority": None,
            "overrules": [],
            "status": None,
            "matched_by": None,
        }
    aliases = item.get("aliases", [])
    if not isinstance(aliases, list):
        aliases = []
    overrules = item.get("overrules", [])
    if not isinstance(overrules, list):
        overrules = [overrules] if overrules else []
    return {
        "precedent_id": item.get("precedent_id"),
        "full_citation": item.get("full_citation"),
        "short_name": item.get("short_name"),
        "aliases": [str(x) for x in aliases if x is not None],
        "year": _as_int_or_none(item.get("year")),
        "court": item.get("court"),
        "bench_strength": _as_int_or_none(item.get("bench_strength")),
        "legal_principle": item.get("legal_principle"),
        "issues": normalize_list(item.get("issues")),
        "keywords": normalize_list(item.get("keywords")),
        "provisions": normalize_list(item.get("provisions")),
        "binding_authority": item.get("binding_authority"),
        "overrules": [str(x) for x in overrules if x is not None],
        "status": item.get("status"),
        "matched_by": item.get("matched_by"),
    }


def normalize_landmarks_block(value):
    block = normalize_dict(value)
    details = block.get("details", [])
    if not isinstance(details, list):
        details = []
    norm_details = [normalize_landmark(d) for d in details if isinstance(d, dict)]
    by_id = {}
    for d in norm_details:
        pid = d.get("precedent_id") or "unknown"
        by_id[pid] = by_id.get(pid, 0) + 1
    return {
        "total": len(norm_details),
        "by_id": by_id,
        "details": norm_details,
    }


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

    # Uniform structs: every object in these lists has identical keys so that
    # HF datasets Arrow conversion can cast the whole column.
    statutory_transitions = [
        normalize_transition(t) for t in statutory_transitions if isinstance(t, dict)
    ]
    transitions_block = normalize_transitions_block(extractions.get("transitions"))
    # Keep top-level and nested details in sync (consolidation duplicates them).
    transitions_block["details"] = statutory_transitions
    transitions_block["total"] = len(statutory_transitions)
    by_source = {}
    for d in statutory_transitions:
        src = d.get("source") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
    transitions_block["by_source"] = by_source

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
            "bench": normalize_bench(metadata.get("bench", [])),
        },
        "classification": {
            "domain": normalize_string(classification.get("domain")),
            "confidence": normalize_string(classification.get("confidence", "low")),
            "signals": normalize_dict(classification.get("signals")),
            "reasoning": normalize_list(classification.get("reasoning")),
        },
        "extractions": {
            "citations": normalize_citations_block(extractions.get("citations")),
            "sections": normalize_dict(extractions.get("sections")),
            "transitions": transitions_block,
            "landmarks": normalize_landmarks_block(extractions.get("landmarks")),
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
