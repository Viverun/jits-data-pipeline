import os
import json
from scripts.utils.transition_extractor import TransitionExtractor

IN_DIR = "../processed/judgments"
OUT_DIR = "../annotations/transitions"

os.makedirs(OUT_DIR, exist_ok=True)

extractor = TransitionExtractor()

for file in os.listdir(IN_DIR):
    if not file.endswith(".json"):
        continue

    path = os.path.join(IN_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        judgment = json.load(f)

    judgment_id = judgment["judgment_id"]
    text = json.dumps(judgment["text"], ensure_ascii=False)

    transitions = extractor.extract(text)

    output = {
        "judgment_id": judgment_id,
        "transition_count": len(transitions),
        "contains_bns": any(t["source"] == "explicit" for t in transitions),
        "critical_changes": [
            t for t in transitions if t["risk"] == "high"
        ],
        "transitions": transitions
    }

    with open(
        os.path.join(OUT_DIR, f"{judgment_id}.json"),
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Transitions extracted for {judgment_id}")
