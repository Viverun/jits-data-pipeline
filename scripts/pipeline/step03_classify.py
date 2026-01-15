import os
import json
import re
from pathlib import Path

INPUT_DIR = "interim/headers_extracted"
OUTPUT_DIR = "interim/classified"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CRIMINAL_STATUTES = ["IPC", "CrPC", "BNS", "BNSS", "IEA", "Indian Penal Code", "Code of Criminal Procedure"]
CIVIL_STATUTES = ["CPC", "Contract Act", "Arbitration", "Specific Relief", "Code of Civil Procedure"]

CRIMINAL_KEYWORDS = ["bail", "fir", "accused", "offence", "custody", "conviction", "acquittal", "sentence"]
CIVIL_KEYWORDS = ["suit", "decree", "injunction", "arbitration", "plaintiff", "defendant", "specific performance"]

def detect_signals(text):
    signals = {"criminal": [], "civil": []}

    for s in CRIMINAL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I):
            signals["criminal"].append(s)

    for s in CIVIL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I):
            signals["civil"].append(s)

    for k in CRIMINAL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I):
            signals["criminal"].append(k)

    for k in CIVIL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I):
            signals["civil"].append(k)

    # Deduplicate signals
    signals["criminal"] = list(set(signals["criminal"]))
    signals["civil"] = list(set(signals["civil"]))
    
    return signals

def classify(signals):
    has_criminal_statute = any(s in CRIMINAL_STATUTES for s in signals["criminal"])
    has_civil_statute = any(s in CIVIL_STATUTES for s in signals["civil"])

    if has_criminal_statute and has_civil_statute:
        return "mixed", "high"
    if has_criminal_statute:
        return "criminal", "high"
    if has_civil_statute:
        return "civil", "high"

    if signals["criminal"] and signals["civil"]:
        return "mixed", "medium"
    if signals["criminal"]:
        return "criminal", "medium"
    if signals["civil"]:
        return "civil", "medium"

    return "unknown", "low"

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"❌ INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    if not files:
        print(f"⚠️ No .json files found in {INPUT_DIR}")
        return

    count = 0
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        text = data["text"]

        signals = detect_signals(text)
        domain, confidence = classify(signals)

        data["classification"] = {
            "domain": domain,
            "confidence": confidence,
            "signals": signals
        }

        out_path = Path(OUTPUT_DIR) / file.name
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

        print(f"✔ Classified {file.name} → {domain} ({confidence})")
        count += 1

    print(f"\n✅ Step03 complete — classified {count} files")

if __name__ == "__main__":
    main()
