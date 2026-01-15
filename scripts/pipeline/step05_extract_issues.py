import os
import json
from scripts.utils.legal_issue_taxonomy import LegalIssueTaxonomy

IN_DIR = "../processed/judgments"
OUT_DIR = "../annotations/issues"

os.makedirs(OUT_DIR, exist_ok=True)

for file in os.listdir(IN_DIR):
    if not file.endswith(".json"):
        continue

    path = os.path.join(IN_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        judgment = json.load(f)

    judgment_id = judgment["judgment_id"]
    text = json.dumps(judgment["text"], ensure_ascii=False)

    issues = LegalIssueTaxonomy.extract(text)

    output = {
        "judgment_id": judgment_id,
        "issue_count": len(issues),
        "issues": issues
    }

    with open(
        os.path.join(OUT_DIR, f"{judgment_id}.json"),
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Issues extracted for {judgment_id}")
