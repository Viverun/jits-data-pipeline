import os
import json
import re
from pathlib import Path

PROCESSED_DIR = "processed/judgments"

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
    "Payment of Gratuity", "Industrial Disputes", "Umadevi", "Service Law"
]

CRIMINAL_KEYWORDS = ["bail", "fir", "accused", "offence", "custody", "conviction", "acquittal", "sentence", "quashing"]
CIVIL_KEYWORDS = ["suit", "decree", "injunction", "arbitration", "plaintiff", "defendant", "specific performance"]
SERVICE_KEYWORDS = ["seniority", "promotion", "DPC", "regularization", "suspension", "departmental inquiry", "pension", "retiral", "back wages", "reinstatement", "daily wage"]

def detect_signals(text):
    signals = {"criminal": [], "civil": [], "service": []}
    # Check for Writ Petition signals (often Service)
    if re.search(r"\b(C\.?W\.?P\.?|Writ Petition)\b", text, re.I):
        signals["service"].append("Writ Petition")

    for s in CRIMINAL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I): signals["criminal"].append(s)
    for s in CIVIL_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I): signals["civil"].append(s)
    for s in SERVICE_STATUTES:
        if re.search(rf"\b{s}\b", text, re.I): signals["service"].append(s)
    for k in CRIMINAL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I): signals["criminal"].append(k)
    for k in CIVIL_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I): signals["civil"].append(k)
    for k in SERVICE_KEYWORDS:
        if re.search(rf"\b{k}\b", text, re.I): signals["service"].append(k)
    
    for k in signals: signals[k] = list(set(signals[k]))
    return signals

def classify(signals):
    has_crim = any(s in CRIMINAL_STATUTES for s in signals["criminal"])
    has_civ = any(s in CIVIL_STATUTES for s in signals["civil"])
    has_serv = any(s in SERVICE_STATUTES for s in signals["service"])

    # 1. Strict Statute Priority
    if has_serv: return "service", "high"
    if has_crim and has_civ: return "mixed", "high"
    if has_crim: return "criminal", "high"
    if has_civ: return "civil", "high"

    # 2. Keyword Density with Service Bias (since CWPs are common)
    counts = {"service": len(signals["service"]), "criminal": len(signals["criminal"]), "civil": len(signals["civil"])}
    max_domain = max(counts, key=counts.get)
    
    if counts[max_domain] >= 1:
        # If it's a tie between Civil and Service, and we have "Writ Petition", pick Service
        if max_domain == "civil" and counts["service"] == counts["civil"] and "Writ Petition" in signals["service"]:
            return "service", "medium"
        return max_domain, "medium" if counts[max_domain] >= 2 else "low"

    return "unknown", "low"

def main():
    files = list(Path(PROCESSED_DIR).glob("*.json"))
    stats = {"service": 0, "criminal": 0, "civil": 0, "mixed": 0, "unknown": 0}
    for file in files:
        with open(file, "r", encoding="utf-8") as f: data = json.load(f)
        signals = detect_signals(data["text"])
        domain, conf = classify(signals)
        data["classification"] = {"domain": domain, "confidence": conf, "signals": signals}
        stats[domain] += 1
        with open(file, "w", encoding="utf-8") as out: json.dump(data, out, indent=2, ensure_ascii=False)
    print(f"✅ Re-classified {len(files)} files. Service: {stats['service']}, Unknown: {stats['unknown']}")

if __name__ == "__main__":
    main()
