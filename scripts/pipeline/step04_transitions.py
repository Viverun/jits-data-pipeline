import os
import json
import re
import sys
from pathlib import Path

# Add project root to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.utils.ipc_bns_mapping import IPCBNSTransitionDB

INPUT_DIR = "interim/classified"
OUTPUT_DIR = "interim/transitions_extracted"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pattern to find section numbers following common legal prefixes
IPC_PATTERN = re.compile(
    r'(?:section|sections|u/s|under section)\s+([\dA-Z,\s]+)',
    re.IGNORECASE
)

def extract_ipc_sections(text):
    found = set()
    for match in IPC_PATTERN.finditer(text):
        parts = match.group(1)
        # Split by commas or spaces to handle "Sections 302, 304"
        for sec in re.split(r"[,\s]+", parts):
            sec = sec.strip().upper()
            # Basic validation: must start with a digit
            if sec and sec[0].isdigit():
                found.add(f"IPC {sec}")
    return sorted(found)

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"❌ INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    if not files:
        print(f"⚠️ No .json files found in {INPUT_DIR}")
        return

    total_mapped = 0
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        classification = data.get("classification", {})
        domain = classification.get("domain")

        # Process only criminal or mixed judgments
        if domain not in {"criminal", "mixed"}:
            out_path = Path(OUTPUT_DIR) / file.name
            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(data, out, indent=2, ensure_ascii=False)
            continue

        text = data["text"]
        ipc_sections = extract_ipc_sections(text)

        mapped = []
        unmapped = []

        for ipc in ipc_sections:
            section_num = ipc.replace("IPC ", "")
            transition = IPCBNSTransitionDB.get(section_num)
            
            if transition:
                mapped.append({
                    "ipc": ipc,
                    "bns": f"BNS {transition['bns']}",
                    "change_type": transition['type'],
                    "risk_level": transition['risk']
                })
                total_mapped += 1
            else:
                unmapped.append(ipc)

        data["statutory_transitions"] = {
            "ipc_detected": ipc_sections,
            "bns_mapped": mapped,
            "unmapped_ipc": unmapped,
            "confidence": "high" if mapped else "low"
        }

        out_path = Path(OUTPUT_DIR) / file.name
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

        print(f"✔ Transitions extracted: {file.name} ({len(mapped)} mapped, {len(unmapped)} unmapped)")

    print(f"\n✅ Step 04 complete — {total_mapped} IPC sections mapped across files.")

if __name__ == "__main__":
    main()
