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

# v0.2.4: Aggressive noise filter for years and common procedural numbers
NOISE_SECTIONS = {
    "1860", "1872", "1973", "2023", "2024", "2019", "1959", "1961", "1983", "1984", "1993", "1994", "1996", "1999", "2001", "2003", "2008", "2012", "2013", "2014", "2016", "2018", "2022",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
}

IPC_PATTERN = re.compile(
    r'(?:section|sections|u/s|under section)\s+([\dA-Z,\s]+)',
    re.IGNORECASE
)

def extract_ipc_sections(text):
    found = set()
    for match in IPC_PATTERN.finditer(text):
        parts = match.group(1)
        for sec in re.split(r"[,\s]+", parts):
            sec = sec.strip().upper()
            # Filter out noise and ensure it's a valid section number
            if sec and sec[0].isdigit() and sec not in NOISE_SECTIONS:
                # Ensure it's not a 4-digit year
                if not (len(sec) == 4 and sec.startswith(("19", "20"))):
                    found.add(f"IPC {sec}")
    return sorted(found)

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        classification = data.get("classification", {})
        domain = classification.get("domain")

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
                if "bns" in transition:
                    mapped.append({
                        "ipc": ipc,
                        "bns": f"BNS {transition['bns']}",
                        "change_type": transition['type'],
                        "risk_level": transition['risk']
                    })
                elif transition.get("type") == "crpc_provision" and transition.get("bnss"):
                    mapped.append({
                        "ipc": f"CrPC {section_num}",
                        "bns": f"BNSS {transition['bnss']}",
                        "change_type": "procedural_transition",
                        "risk_level": "low"
                    })
                else:
                    unmapped.append(ipc)
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

    print(f"[OK] Transitions refined for {len(files)} files.")

if __name__ == "__main__":
    main()
