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

    Every string field uses normalize_string()'s "" sentinel rather than bare
    None. HF's JSON loader infers a column's type from an early chunk; if
    every value it samples for a field happens to be None, it locks in Arrow's
    null type, and any real string appearing later in the file then fails to
    cast ("Couldn't cast array of type string to null") - exactly what
    happened here, since bns is null for every transition except the rare
    explicit-mapping case, and none of those landed in the sampled chunk.
    """
    if not isinstance(item, dict):
        return {k: (False if k in ("validated", "requires_judicial_confirmation") else "") for k in TRANSITION_FIELDS}
    return {
        "ipc": normalize_string(item.get("ipc")),
        "bns": normalize_string(item.get("bns")),
        "source": normalize_string(item.get("source")),
        "validated": bool(item.get("validated", False)),
        "risk": normalize_string(item.get("risk")),
        "confidence": normalize_string(item.get("confidence")),
        "note": normalize_string(item.get("note")),
        "context_snippet": normalize_string(item.get("context_snippet")),
        "requires_judicial_confirmation": bool(item.get("requires_judicial_confirmation", False)),
        "temporal_warning": normalize_string(item.get("temporal_warning")),
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
    # Same "" sentinel as normalize_transition, for the same reason: every
    # optional string field must never be bare None, or an early all-null
    # sample chunk locks in Arrow's null type for that column.
    if not isinstance(item, dict):
        return {
            k: (False if k == "is_landmark" else None if k in ("start_pos", "end_pos") else "")
            for k in CITATION_FIELDS
        }
    return {
        "type": normalize_string(item.get("type")),
        "reporter": normalize_string(item.get("reporter")),
        "year": normalize_string(item.get("year")),
        "page": normalize_string(item.get("page")),
        "volume": normalize_string(item.get("volume")),
        "court": normalize_string(item.get("court")),
        "petitioner": normalize_string(item.get("petitioner")),
        "respondent": normalize_string(item.get("respondent")),
        "case_name": normalize_string(item.get("case_name")),
        "raw": normalize_string(item.get("raw")),
        "start_pos": _as_int_or_none(item.get("start_pos")),
        "end_pos": _as_int_or_none(item.get("end_pos")),
        "is_landmark": bool(item.get("is_landmark", False)),
        "precedent_id": normalize_string(item.get("precedent_id")),
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
    # Same "" sentinel as normalize_transition/normalize_citation.
    if not isinstance(item, dict):
        return {
            "precedent_id": "",
            "full_citation": "",
            "short_name": "",
            "aliases": [],
            "year": None,
            "court": "",
            "bench_strength": None,
            "legal_principle": "",
            "issues": [],
            "keywords": [],
            "provisions": [],
            "binding_authority": "",
            "overrules": [],
            "status": "",
            "matched_by": "",
        }
    aliases = item.get("aliases", [])
    if not isinstance(aliases, list):
        aliases = []
    overrules = item.get("overrules", [])
    if not isinstance(overrules, list):
        overrules = [overrules] if overrules else []
    return {
        "precedent_id": normalize_string(item.get("precedent_id")),
        "full_citation": normalize_string(item.get("full_citation")),
        "short_name": normalize_string(item.get("short_name")),
        "aliases": [str(x) for x in aliases if x is not None],
        "year": _as_int_or_none(item.get("year")),
        "court": normalize_string(item.get("court")),
        "bench_strength": _as_int_or_none(item.get("bench_strength")),
        "legal_principle": normalize_string(item.get("legal_principle")),
        "issues": normalize_list(item.get("issues")),
        "keywords": normalize_list(item.get("keywords")),
        "provisions": normalize_list(item.get("provisions")),
        "binding_authority": normalize_string(item.get("binding_authority")),
        "overrules": [str(x) for x in overrules if x is not None],
        "status": normalize_string(item.get("status")),
        "matched_by": normalize_string(item.get("matched_by")),
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
