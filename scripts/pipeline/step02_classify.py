from opennyai import Pipeline
from opennyai.utils import Data
import os
import json

# Directories
input_dir = "../raw/judgments/unclassified"
output_dir = "../interim/cleaned"
os.makedirs(output_dir, exist_ok=True)

docs = []
filenames = []

for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        with open(os.path.join(input_dir, file), "r", encoding="utf-8") as f:
            docs.append(f.read())
            filenames.append(file)

data = Data(docs)

pipeline = Pipeline(
    components=["Rhetorical_Role", "Summarizer"],
    use_gpu=False,
    verbose=True
)

results = pipeline(data)

for i, result in enumerate(results):
    out = {
        "source_file": filenames[i],
        "rhetorical_roles": result.get("Rhetorical_Role"),
        "summary": result.get("summary"),
        "created_at": "pre-classification"
    }

    out_path = os.path.join(
        output_dir,
        filenames[i].replace(".txt", ".json")
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Cleaned {filenames[i]}")
