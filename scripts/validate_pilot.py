# scripts/validate_pilot.py
import json
import os
import pandas as pd
from pathlib import Path

def generate_validation_report(data_root: str = "C:/Users/khanj/jits-data"):
    """Generates a summary report of the pilot run."""
    processed_dir = Path(data_root) / "processed" / "judgments"
    ann_class_dir = Path(data_root) / "annotations" / "classification"
    ann_trans_dir = Path(data_root) / "annotations" / "transitions"

    records = []
    for json_file in processed_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            judgment = json.load(f)
        jid = judgment["judgment_id"]

        # Get classification
        class_file = ann_class_dir / f"{jid}.json"
        classification = json.loads(class_file.read_text()) if class_file.exists() else {}

        # Get transitions
        trans_file = ann_trans_dir / f"{jid}.json"
        transitions = json.loads(trans_file.read_text()) if trans_file.exists() else {}

        records.append({
            "judgment_id": jid,
            "domain": judgment.get("domain"),
            "domain_confidence": classification.get("confidence"),
            "cause_title_locked": classification.get("cause_title_locked", False),
            "transition_count": transitions.get("transition_count", 0),
            "contains_explicit_bns": transitions.get("contains_bns", False),
            "critical_changes_count": len(transitions.get("critical_changes", [])),
            "split": judgment.get("split", "unknown")
        })

    df = pd.DataFrame(records)
    report_path = Path(data_root) / "pilot_validation_report.csv"
    df.to_csv(report_path, index=False)

    # Print summary to console
    print("\n" + "="*60)
    print("Pilot Run Validation Summary")
    print("="*60)
    print(f"Total Judgments Processed: {len(df)}")
    print(f"\nDomain Distribution:")
    print(df["domain"].value_counts())
    print(f"\nTransitions Found:")
    print(f"  - Judgments with any transition: {(df['transition_count'] > 0).sum()}")
    print(f"  - Judgments with explicit BNS mention: {df['contains_explicit_bns'].sum()}")
    print(f"  - Total critical changes flagged: {df['critical_changes_count'].sum()}")
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    generate_validation_report()