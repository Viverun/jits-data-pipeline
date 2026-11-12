import argparse
import json
from pathlib import Path


def rebuild_raw_corpus(input_file: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0

    with input_file.open("r", encoding="utf-8") as infile:
        for line_no, line in enumerate(infile, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            judgment_id = record.get("judgment_id")
            text = record.get("text", "")

            if not judgment_id or not text.strip():
                raise ValueError(f"Missing judgment_id or text at line {line_no}")

            out_path = output_dir / f"{judgment_id}.txt"
            out_path.write_text(text.rstrip() + "\n", encoding="utf-8")
            written += 1

    return written


def main():
    parser = argparse.ArgumentParser(description="Rebuild raw judgment .txt files from train.jsonl")
    parser.add_argument("--input-file", default="train.jsonl")
    parser.add_argument("--output-dir", default="legal_ai_toolkit/data/raw/judgments")
    args = parser.parse_args()

    input_file = Path(args.input_file)
    output_dir = Path(args.output_dir)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    written = rebuild_raw_corpus(input_file, output_dir)
    print(f"Rebuilt {written} raw judgment files in {output_dir}")


if __name__ == "__main__":
    main()
