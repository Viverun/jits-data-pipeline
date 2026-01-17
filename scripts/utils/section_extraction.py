import sys
import os
import json
import argparse
from legal_ai_toolkit.utils.section_extraction import extract_legal_sections_v2

def main():
    parser = argparse.ArgumentParser(description="Extract legal sections from text.")
    parser.add_argument("source", help="Path to text file or raw text")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    text = ""
    if os.path.exists(args.source):
        with open(args.source, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.source

    sections = extract_legal_sections_v2(text)

    if args.json:
        print(json.dumps(sections, indent=2))
    else:
        print("Extracted Legal Sections:")
        print("=========================")
        for act, found in sections.items():
            if act == 'other_acts':
                continue
            if found:
                print(f"{act.upper()}: {', '.join(found)}")

if __name__ == "__main__":
    main()
