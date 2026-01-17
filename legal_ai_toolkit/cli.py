import argparse
from .pipeline.orchestrator import PipelineOrchestrator
from .analytics.reporting import ReportGenerator
from .analytics.audit import DataAuditor
from .utils.demo import ShowcasePreparer

def main():
    parser = argparse.ArgumentParser(description="Legal AI Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run the full data pipeline")
    pipeline_parser.add_argument("--raw-dir", default=None, help="Directory with raw text files (defaults to package data)")
    pipeline_parser.add_argument("--step", choices=["ingest", "metadata", "classify", "transitions", "issues", "citations", "similarity", "cluster", "consolidate"], help="Run a specific step instead of full pipeline")
    pipeline_parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate operational report")
    report_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    report_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    report_parser.add_argument("--output-dir", default="operational_reports")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit dataset quality and metrics")
    audit_parser.add_argument("--type", choices=["quality", "landmarks", "unmapped", "edges", "samples", "clusters"], default="quality")
    audit_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    audit_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    audit_parser.add_argument("--edge-file", default="annotations/similarity/edges.jsonl")

    # Showcase command
    showcase_parser = subparsers.add_parser("showcase", help="Prepare demo showcase clusters")
    showcase_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    showcase_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    showcase_parser.add_argument("--output-dir", default="demo_showcase")

    args = parser.parse_args()

    if args.command == "pipeline":
        orchestrator = PipelineOrchestrator(raw_dir=args.raw_dir)
        if args.step:
            orchestrator.run_step(args.step, workers=args.workers)
        else:
            orchestrator.run_full_pipeline(workers=args.workers)
    elif args.command == "report":
        generator = ReportGenerator(args.cluster_file, args.processed_dir, args.output_dir)
        generator.generate()
    elif args.command == "audit":
        auditor = DataAuditor(args.processed_dir, cluster_file=args.cluster_file, edge_file=args.edge_file)
        if args.type == "quality":
            auditor.audit_quality()
        elif args.type == "landmarks":
            auditor.audit_landmarks()
        elif args.type == "unmapped":
            auditor.check_unmapped_ipc()
        elif args.type == "edges":
            auditor.analyze_edges()
        elif args.type == "samples":
            auditor.audit_classification_samples()
        elif args.type == "clusters":
            auditor.summarize_clusters()
    elif args.command == "showcase":
        preparer = ShowcasePreparer(args.cluster_file, args.processed_dir, args.output_dir)
        preparer.prepare()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
