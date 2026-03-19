import os
import json
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool, cpu_count

# Universal filters
UNIVERSAL_ISSUES = {"jurisdiction", "maintainability", "limitation"}
UNIVERSAL_SECTIONS = {
    "IPC 1", "IPC 2", "IPC 3", "IPC 4", "IPC 5", "IPC 6", "IPC 7", "IPC 8", "IPC 9", "IPC 10",
    "IPC 34", "IPC 120B", "IPC 149"
}
_ALL_SIGNALS = {}


def _init_similarity_pool(all_signals_dict):
    global _ALL_SIGNALS
    _ALL_SIGNALS = all_signals_dict


def _normalize_issue_names(issue_data):
    if isinstance(issue_data, dict):
        return list(issue_data.keys())
    if isinstance(issue_data, list):
        return list(issue_data)
    return []


def _normalize_section_signal(act, section):
    if not act or not section:
        return None
    return f"{str(act).upper()} {str(section).upper()}"


def _extract_section_signals(data):
    section_signals = set()

    for act_key, section_nums in data.get("extracted_sections", {}).items():
        act = str(act_key).replace("_", " ")
        for section in section_nums:
            normalized = _normalize_section_signal(act, section)
            if normalized:
                section_signals.add(normalized)

    transitions = data.get("statutory_transitions", {}).get("transitions", [])
    if not transitions:
        transitions = data.get("extractions", {}).get("transitions", {}).get("details", [])

    for transition in transitions:
        ipc = transition.get("ipc")
        bns = transition.get("bns")
        if ipc:
            section_signals.add(f"IPC {str(ipc).upper()}")
        if bns:
            section_signals.add(f"BNS {str(bns).upper()}")

    extraction_sections = data.get("extractions", {}).get("sections", {}).get("details", [])
    for section in extraction_sections:
        normalized = _normalize_section_signal(section.get("act"), section.get("section"))
        if normalized:
            section_signals.add(normalized)

    return list(section_signals)

def extract_signals(data):
    """Extracts core similarity signals from a judgment's annotations."""
    # Handle both old 'id' field and new 'judgment_id' field
    judgment_id = data.get("judgment_id") or data.get("id", "UNKNOWN")

    annotation_issues = _normalize_issue_names(data.get("annotations", {}).get("issues", {}))
    extraction_issues = _normalize_issue_names(data.get("extractions", {}).get("issues", {}).get("details", {}))
    citations = data.get("annotations", {}).get("citations", [])
    if not citations:
        citations = data.get("extractions", {}).get("citations", {}).get("details", [])

    signals = {
        "judgment_id": judgment_id,
        "issues": annotation_issues or extraction_issues,
        "sections": _extract_section_signals(data),
        "citations": [],
        "domain": data.get("classification", {}).get("domain", "unknown")
    }

    # Extract citations
    for c in citations:
        if "raw" in c:
            signals["citations"].append(c["raw"])

    # Deduplicate and filter
    signals["sections"] = list(set(signals["sections"]) - UNIVERSAL_SECTIONS)
    signals["citations"] = list(set(signals["citations"]))
    signals["issues"] = list(set(signals["issues"]) - UNIVERSAL_ISSUES)

    return signals

def calculate_similarity_batch(args):
    """Process a batch of pairs in parallel"""
    pair_batch = args
    all_signals_dict = _ALL_SIGNALS
    edges = []

    for sig1_id, sig2_id in pair_batch:
        sig1 = all_signals_dict[sig1_id]
        sig2 = all_signals_dict[sig2_id]

        # Skip cross-domain pairs for efficiency
        if sig1["domain"] != sig2["domain"] and sig1["domain"] != "mixed" and sig2["domain"] != "mixed":
            continue

        # OPTIMIZATION: Quick overlap check BEFORE detailed comparison
        # Skip expensive set operations if there's no potential overlap
        if not (set(sig1["issues"]) & set(sig2["issues"]) or
                set(sig1["sections"]) & set(sig2["sections"]) or
                set(sig1["citations"]) & set(sig2["citations"])):
            continue  # No overlap at all, skip this pair

        shared_issues = list(set(sig1["issues"]) & set(sig2["issues"]))
        shared_sections = list(set(sig1["sections"]) & set(sig2["sections"]))
        shared_citations = list(set(sig1["citations"]) & set(sig2["citations"]))


        # Calculate weight
        weight = len(shared_issues) + len(shared_sections) + len(shared_citations)

        # Determine strength
        strength = "low"
        if weight >= 10:
            strength = "high"
        elif weight >= 5:
            strength = "medium"

        edge = {
            "from": sig1_id,
            "to": sig2_id,
            "signals": {
                "shared_issues": shared_issues,
                "shared_sections": shared_sections,
                "shared_citations": shared_citations
            },
            "weight": weight,
            "strength": strength
        }
        edges.append(edge)

    return edges

class SimilarityProcessor:
    def __init__(self, input_dir, signal_dir, edge_file):
        self.input_dir = Path(input_dir)
        self.signal_dir = Path(signal_dir)
        self.edge_file = Path(edge_file)
        os.makedirs(self.signal_dir, exist_ok=True)
        os.makedirs(self.edge_file.parent, exist_ok=True)

    def run(self, workers=None, batch_size=1000):
        if workers is None:
            workers = max(1, cpu_count() - 1)

        files = list(self.input_dir.glob("*.json"))
        all_signals = {}

        print(f"Extracting signals from {len(files)} judgments...")
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            sig = extract_signals(data)
            jid = sig["judgment_id"]
            all_signals[jid] = sig

            # Save signal file
            with open(self.signal_dir / f"{jid}.json", "w", encoding="utf-8") as out:
                json.dump(sig, out, indent=2)

        jid_list = list(all_signals.keys())
        pairs = list(combinations(jid_list, 2))
        print(f"Total potential pairs: {len(pairs)}")

        batches = [pairs[i : i + batch_size] for i in range(0, len(pairs), batch_size)]

        print(f"Calculating similarity on {len(batches)} batches using {workers} workers...")
        all_edges = []
        if workers <= 1:
            _init_similarity_pool(all_signals)
            for batch in batches:
                all_edges.extend(calculate_similarity_batch(batch))
        else:
            with Pool(workers, initializer=_init_similarity_pool, initargs=(all_signals,)) as pool:
                for result in pool.imap_unordered(calculate_similarity_batch, batches):
                    all_edges.extend(result)

        print(f"Generated {len(all_edges)} edges. Saving to {self.edge_file}...")
        with open(self.edge_file, "w", encoding="utf-8") as out:
            for edge in all_edges:
                out.write(json.dumps(edge) + "\n")

        print("[OK] Similarity calculation complete.")
