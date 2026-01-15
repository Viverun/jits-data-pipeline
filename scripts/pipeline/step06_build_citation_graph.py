import os
import json
from scripts.utils.citation_extractor import CitationExtractor
from scripts.utils.citation_normalizer import CitationNormalizer

IN_DIR = "../processed/judgments"
OUT_DIR = "../annotations/citations"
PER_JUDGMENT = f"{OUT_DIR}/per_judgment"

os.makedirs(PER_JUDGMENT, exist_ok=True)

edges = []

for file in os.listdir(IN_DIR):
    if not file.endswith(".json"):
        continue

    path = os.path.join(IN_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        judgment = json.load(f)

    judgment_id = judgment["judgment_id"]
    text = json.dumps(judgment["text"], ensure_ascii=False)

    citations = CitationExtractor.extract(text)
    normalized = []

    for c in citations:
        cid = CitationNormalizer.normalize(c)
        normalized.append(cid)

        edges.append({
            "from": judgment_id,
            "to": cid,
            "relation": "cites"
        })

    with open(
        f"{PER_JUDGMENT}/{judgment_id}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump({
            "judgment_id": judgment_id,
            "citation_count": len(normalized),
            "citations": normalized
        }, f, indent=2)

# Save global edge list
with open(f"{OUT_DIR}/edges.jsonl", "w") as f:
    for e in edges:
        f.write(json.dumps(e) + "\n")

print("Citation graph built successfully")
