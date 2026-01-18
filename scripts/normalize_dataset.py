
import json
import subprocess
from datetime import datetime

# Commit hash containing the full 846 judgments
COMMIT_HASH = "9a4f934"
DATA_DIR = "legal_ai_toolkit/data/judgments"
OUTPUT_FILE = "train.jsonl"

def normalize_string(val):
    return str(val) if val is not None else ""

def normalize_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return [str(v) for v in val] # Ensure all items are strings
    return []

def normalize_dict(val):
    return val if isinstance(val, dict) else {}

def normalize_record(data):
    """
    Enforces a strict schema for each record.
    """
    # 1. Core Fields
    judgment_id = normalize_string(data.get("judgment_id"))
    text = normalize_string(data.get("text"))

    # 2. Metadata (Flatten/normalize known fields)
    raw_meta = normalize_dict(data.get("metadata"))
    metadata = {
        "court": normalize_string(raw_meta.get("court")),
        "date": normalize_string(raw_meta.get("date")),
        "bench": normalize_list(raw_meta.get("bench")),
        "case_type": normalize_string(raw_meta.get("case_type")),
        "case_number": normalize_string(raw_meta.get("case_number")),
        "petitioner": normalize_string(raw_meta.get("petitioner")),
        "respondent": normalize_string(raw_meta.get("respondent"))
    }

    # 3. Classification
    raw_class = normalize_dict(data.get("classification"))
    classification = {
        "domain": normalize_string(raw_class.get("domain")),
        "confidence": normalize_string(raw_class.get("confidence", "low")), 
        "signals": raw_class.get("signals", {}) 
    }
    # Ensure signals values are lists
    if not isinstance(classification["signals"], dict):
        classification["signals"] = {}
    for k, v in classification["signals"].items():
        if not isinstance(v, list):
            classification["signals"][k] = []
    
    # 4. Extractions (Handle both keys and map correctly)
    raw_extract = data.get("extractions") or data.get("annotations") or {}
    raw_extract = normalize_dict(raw_extract)
    
    # Map 'annotations' keys to 'extractions' schema if needed
    # In some JSONs: annotations = {citations: [], issues: {details: ...}}
    # We want extractions = {citations: [], sections: [], landmarks: []}
    
    citations = normalize_list(raw_extract.get("citations"))
    
    # Try to find sections and landmarks, default to empty if not found
    sections = normalize_list(raw_extract.get("sections"))
    landmarks = normalize_list(raw_extract.get("landmarks"))
    
    extractions = {
        "citations": citations,
        "sections": sections,
        "landmarks": landmarks
    }

    # 5. Statutory Transitions
    raw_trans = data.get("statutory_transitions")
    statutory_transitions = []
    if isinstance(raw_trans, list):
        for item in raw_trans:
            if isinstance(item, dict):
                 # Ensure all values in transition dict are strings
                clean_item = {k: str(v) for k, v in item.items()}
                statutory_transitions.append(clean_item)
    
    # 6. Provenance
    raw_prov = normalize_dict(data.get("provenance"))
    provenance = {
        "version": normalize_string(raw_prov.get("version", "1.0")),
        "processed_date": normalize_string(raw_prov.get("processed_date", datetime.now().isoformat()))
    }
    
    # Construct final record
    return {
        "judgment_id": judgment_id,
        "text": text,
        "metadata": metadata,
        "classification": classification,
        "extractions": extractions,
        "statutory_transitions": statutory_transitions,
        "provenance": provenance
    }

def get_git_files(commit, path):
    """List files in a specific commit and directory."""
    try:
        cmd = ["git", "ls-tree", "-r", "--name-only", commit, path]
        result = subprocess.check_output(cmd, text=True)
        return [f for f in result.splitlines() if f.endswith(".json")]
    except subprocess.CalledProcessError as e:
        print(f"Error listing files: {e}")
        return []

def read_git_file(commit, path):
    """Read a file content from a specific commit."""
    try:
        cmd = ["git", "show", f"{commit}:{path}"]
        content = subprocess.check_output(cmd, text=True, encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return None

def main():
    print(f"Listing files from commit {COMMIT_HASH} in {DATA_DIR}...")
    files = get_git_files(COMMIT_HASH, DATA_DIR)
    print(f"Found {len(files)} JSON files in git history.")
    
    if not files:
        print("No files found!")
        return

    count = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        for fpath in files:
            data = read_git_file(COMMIT_HASH, fpath)
            if data:
                clean_record = normalize_record(data)
                out_f.write(json.dumps(clean_record) + '\n')
                count += 1
            if count % 100 == 0:
                print(f"Processed {count} files...")
    
    print(f"Successfully wrote {count} records to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
