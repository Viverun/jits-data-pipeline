import json
import os
import random
from pathlib import Path

PROCESSED_DIR = "processed/judgments"

def audit_samples(samples_per_domain=2):
    files = list(Path(PROCESSED_DIR).glob("*.json"))
    
    # Group files by domain
    domain_groups = {}
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            domain = data.get("classification", {}).get("domain", "unknown")
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append((file.name, data))

    print("🧪 Classification Accuracy Audit (Random Samples)\n")
    print("="*80)

    for domain in sorted(domain_groups.keys()):
        print(f"\n📂 DOMAIN: {domain.upper()}")
        samples = random.sample(domain_groups[domain], min(len(domain_groups[domain]), samples_per_domain))
        
        for filename, data in samples:
            signals = data.get("classification", {}).get("signals", {})
            confidence = data.get("classification", {}).get("confidence", "low")
            text_snippet = data.get("text", "")[:500].replace("\n", " ")
            
            print(f"\n📄 File: {filename}")
            print(f"   Confidence: {confidence}")
            print(f"   Signals Found: {signals}")
            print(f"   Snippet: {text_snippet}...")
            print("-" * 40)

if __name__ == "__main__":
    audit_samples()
