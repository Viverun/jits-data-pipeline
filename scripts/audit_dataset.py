import argparse
from legal_ai_toolkit.analytics.audit import DataAuditor
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Audit the JITS dataset for quality and accuracy.")
    parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments", help="Path to processed JSON files")
    parser.add_argument("--clusters", default="annotations/similarity/clusters.json", help="Path to clusters.json")
    parser.add_argument("--edges", default="annotations/similarity/edges.jsonl", help="Path to edges.jsonl")
    parser.add_argument("--samples", type=int, default=3, help="Samples per domain for classification audit")

    args = parser.parse_args()

    auditor = DataAuditor(
        processed_dir=args.processed_dir,
        cluster_file=args.clusters,
        edge_file=args.edges
    )

    print("=== STARTING COMPREHENSIVE JITS AUDIT ===")

    # 1. Basic Quality & Metadata Accuracy
    auditor.audit_quality()

    # 2. Extract Landmark citation statistics
    auditor.audit_landmarks()

    # 3. Check for specific unmapped statutory sections
    auditor.check_unmapped_ipc()

    # 4. Analyze relationship graph edges
    auditor.analyze_edges()

    # 5. Review sample classifications
    auditor.audit_classification_samples(samples_per_domain=args.samples)

    # 6. Validate link integrity across files
    auditor.validate_referential_integrity()

    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    main()
