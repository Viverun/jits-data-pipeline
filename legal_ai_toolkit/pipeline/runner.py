import os
import json
from pathlib import Path
from tqdm import tqdm

class BaseStep:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        if not self.input_dir.exists():
            print(f"[ERROR] Input directory not found: {self.input_dir}")
            return

        files = list(self.input_dir.glob("*.json"))
        if not files:
            print(f"[WARNING] No .json files found in {self.input_dir}")
            return

        print(f"Processing {len(files)} files from {self.input_dir} to {self.output_dir}...")
        for file in tqdm(files):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                processed_data = self.process_item(data)

                if processed_data:
                    out_path = self.output_dir / file.name
                    with open(out_path, "w", encoding="utf-8") as out:
                        json.dump(processed_data, out, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[ERROR] Error processing {file.name}: {str(e)}")

    def process_item(self, data):
        raise NotImplementedError("Subclasses must implement process_item")
