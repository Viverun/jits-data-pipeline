import os
import json
import re
from pathlib import Path

INPUT_DIR = "interim/headers_extracted"
OUTPUT_DIR = "interim/classified"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CRIMINAL_STATUTES = [
    "IPC", "CrPC", "BNS", "BNSS", "IEA", "Indian Penal Code", "Code of Criminal Procedure",
    "NDPS", "POCSO", "UAPA", "PMLA", "Arms Act", "Excise Act"
]
CIVIL_STATUTES = [
    "CPC", "Contract Act", "Arbitration", "Specific Relief", "Code of Civil Procedure",
    "Transfer of Property", "Hindu Marriage Act", "Succession Act", "Limitation Act",
    "Negotiable Instruments", "NI Act", "Motor Vehicles Act", "MV Act"
]
SERVICE_STATUTES = [
    "Article 311", "Article 16", "Service Rules", "Fundamental Rules", "Pension Rules",
    "Payment of Gratuity", "Industrial Disputes"
]

CRIMINAL_KEYWORDS = [
    "bail", "fir", "accused", "offence", "custody", "conviction", "acquittal", "sentence",
    "quashing", "charge sheet", "police station", "magistrate", "sessions court", "penal"
]
CIVIL_KEYWORDS = [
    "suit", "decree", "injunction", "arbitration", "plaintiff", "defendant", "specific performance",
    "property", "possession", "partition", "mortgage", "tenant", "landlord", "compensation"
]
SERVICE_KEYWORDS = [
    "seniority", "promotion", "DPC", "selection list", "regularization", "suspension",
    "departmental inquiry", "misconduct", "termination", "pension", "gratuity", "retiral",
    "back wages", "reinstatement", "daily wage"
]

def detect_signals(text):
    signals = {"criminal": [], "civil": [], "service": []}

    for s in CRIMINAL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I):
            signals["criminal"].append(s)

    for s in CIVIL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I):
            signals["civil"].append(s)
            
    for s in SERVICE_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I):
            signals["service"].append(s)

    for k in CRIMINAL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I):
            signals["criminal"].append(k)

    for k in CIVIL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I):
            signals["civil"].append(k)
            
    for k in SERVICE_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I):
            signals["service"].append(k)

    # Deduplicate signals
    signals["criminal"] = list(set(signals["criminal"]))
    signals["civil"] = list(set(signals["civil"]))
    signals["service"] = list(set(signals["service"]))
    
    return signals

def classify(signals):
    has_criminal_statute = any(s in CRIMINAL_STATUTES for s in signals["criminal"])
    has_civil_statute = any(s in CIVIL_STATUTES for s in signals["civil"])
    has_service_statute = any(s in SERVICE_STATUTES for s in signals["service"])

    # Priority 1: Service Law
    if has_service_statute:
        return "service", "high"

    # Priority 2: Mixed
    if (has_criminal_statute + has_civil_statute + has_service_statute) > 1:
        return "mixed", "high"

    # Priority 3: Direct Statute Match
    if has_criminal_statute:
        return "criminal", "high"
    if has_civil_statute:
        return "civil", "high"

    # Fallback: Keyword Density
    counts = {
        "service": len(signals["service"]),
        "criminal": len(signals["criminal"]),
        "civil": len(signals["civil"])
    }
    
    max_domain = max(counts, key=counts.get)
    if counts[max_domain] >= 2:
        return max_domain, "medium"
    elif counts[max_domain] == 1:
        return max_domain, "low"

    return "unknown", "low"

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] INPUT_DIR not found: {INPUT_DIR}")
        return

    files = list(Path(INPUT_DIR).glob("*.json"))
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        signals = detect_signals(data["text"])
        domain, confidence = classify(signals)

        data["classification"] = {
            "domain": domain,
            "confidence": confidence,
            "signals": signals
        }

        out_path = Path(OUTPUT_DIR) / file.name
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2, ensure_ascii=False)

    print(f"[OK] Step03 complete — classified {len(files)} files")

if __name__ == "__main__":
    main()
