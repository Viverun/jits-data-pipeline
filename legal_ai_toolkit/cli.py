import argparse

def main():
    parser = argparse.ArgumentParser(description="Legal AI Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run the full data pipeline")
    pipeline_parser.add_argument("--raw-dir", default=None, help="Directory with raw text files (defaults to package data)")
    pipeline_parser.add_argument("--step", choices=["ingest", "metadata", "issues", "classify", "id_regen", "transitions", "citations", "similarity", "cluster", "consolidate"], help="Run a specific step instead of full pipeline")
    pipeline_parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate operational report")
    report_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    report_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    report_parser.add_argument("--output-dir", default="operational_reports")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit dataset quality and metrics")
    audit_parser.add_argument("--type", choices=["quality", "landmarks", "unmapped", "edges", "samples", "clusters", "coherence", "integrity"], default="quality")
    audit_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    audit_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    audit_parser.add_argument("--edge-file", default="annotations/similarity/edges.jsonl")

    # Showcase command
    showcase_parser = subparsers.add_parser("showcase", help="Prepare demo showcase clusters")
    showcase_parser.add_argument("--cluster-file", default="annotations/similarity/clusters_refined.json")
    showcase_parser.add_argument("--processed-dir", default="legal_ai_toolkit/data/judgments")
    showcase_parser.add_argument("--output-dir", default="demo_showcase")

    # Dashboard command
    subparsers.add_parser("dashboard", help="Launch the CLI dashboard")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download additional judgments using the resumable Indian Kanoon crawler")
    download_parser.add_argument("--output-dir", default="legal_ai_toolkit/data/raw/judgments", help="Directory to store raw judgment .txt files")
    download_parser.add_argument("--checkpoint-file", default="download_checkpoint.json", help="Checkpoint JSON for resumable crawling")
    download_parser.add_argument("--manifest-file", default="download_manifest.jsonl", help="JSONL manifest of downloaded source documents")
    download_parser.add_argument("--target-total", type=int, default=3200, help="Stop once the raw corpus reaches this many .txt files")
    download_parser.add_argument("--per-query", type=int, default=40, help="Maximum search results to fetch per query")
    download_parser.add_argument("--max-queries", type=int, default=0, help="Optional cap on how many queries to attempt this run")
    download_parser.add_argument("--query-file", default=None, help="Optional JSON/JSONL/plaintext query file")
    download_parser.add_argument("--query-profile", choices=["default", "deep"], default="default", help="Built-in query catalog to use when --query-file is not provided")
    download_parser.add_argument("--shuffle", action="store_true", help="Shuffle the default query plan")
    download_parser.add_argument("--dry-run", action="store_true", help="Print the planned queries without downloading")

    args = parser.parse_args()

    if args.command == "pipeline":
        from .pipeline.orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator(raw_dir=args.raw_dir)
        if args.step:
            orchestrator.run_step(args.step, workers=args.workers)
        else:
            orchestrator.run_full_pipeline(workers=args.workers)
    elif args.command == "report":
        from .analytics.reporting import ReportGenerator
        generator = ReportGenerator(args.cluster_file, args.processed_dir, args.output_dir)
        generator.generate()
    elif args.command == "audit":
        from .analytics.audit import DataAuditor
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
        elif args.type == "coherence":
            auditor.validate_similarity_coherence()
        elif args.type == "integrity":
            auditor.validate_referential_integrity()
    elif args.command == "showcase":
        from .utils.demo import ShowcasePreparer
        preparer = ShowcasePreparer(args.cluster_file, args.processed_dir, args.output_dir)
        preparer.prepare()
    elif args.command == "dashboard":
        from .cli_dashboard import main as run_dashboard
        run_dashboard()
    elif args.command == "download":
        from .extraction import IndianKanoonDownloader, build_expansion_queries, load_queries_from_file

        queries = (
            load_queries_from_file(args.query_file)
            if args.query_file
            else build_expansion_queries(shuffle=args.shuffle, profile=args.query_profile)
        )
        if args.max_queries and args.max_queries > 0:
            queries = queries[:args.max_queries]

        if args.dry_run:
            print(f"Planned queries: {len(queries)}")
            for item in queries[:25]:
                print(f"- [{item['category']}] {item['query']}")
            if len(queries) > 25:
                print(f"... and {len(queries) - 25} more")
            return

        downloader = IndianKanoonDownloader(
            output_dir=args.output_dir,
            checkpoint_file=args.checkpoint_file,
            manifest_file=args.manifest_file,
        )

        remaining_queries = [item for item in queries if item["query"] not in downloader.completed_queries]

        starting_count = downloader.count_saved_files()
        print(f"Starting raw corpus size: {starting_count}")
        print(f"Target raw corpus size: {args.target_total}")
        print(f"Planned queries in catalog: {len(queries)}")
        print(f"Remaining queries after checkpoint: {len(remaining_queries)}")
        if args.query_file:
            print(f"Query catalog source: {args.query_file}")
        else:
            print(f"Query catalog profile: {args.query_profile}")

        if not remaining_queries:
            print("Query catalog exhausted for the current checkpoint. Use a new query profile, a query file, or a fresh checkpoint.")
            return

        for item in remaining_queries:
            current_total = downloader.count_saved_files()
            if current_total >= args.target_total:
                print(f"Reached target corpus size: {current_total}")
                break

            downloader.search_and_download(
                item["query"],
                item["category"],
                max_results=args.per_query,
            )

        final_total = downloader.count_saved_files()
        print("\nDownload run complete!")
        print(f"  Raw files: {final_total}")
        print(f"  Newly added this run: {final_total - starting_count}")
        print(f"  Total downloaded docs tracked: {downloader.progress.get('total_downloaded', 0)}")
        print(f"  Duplicate doc IDs skipped: {downloader.progress.get('duplicate_doc_ids', 0)}")
        print(f"  Duplicate texts skipped: {downloader.progress.get('duplicate_texts', 0)}")
        print(f"  Short-content skips: {downloader.progress.get('short_content', 0)}")
        print(f"  Failed downloads: {downloader.progress.get('failed_downloads', 0)}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
