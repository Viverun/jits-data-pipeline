from .metadata import MetadataExtractionStep
from .classification import ClassificationStep
from .id_regeneration import IDRegenerationStep
from .transitions import TransitionStep
from .issues import IssueExtractionStep
from .citations import CitationExtractionStep
from .consolidation import ConsolidationStep
from ..clustering.similarity import SimilarityProcessor
from ..clustering.centroid import CentroidClusteter
from ..clustering.refinement import ClusterRefiner
import os

class PipelineOrchestrator:
    def __init__(self, raw_dir=None, interim_dir="interim", processed_dir=None, annotations_dir="annotations"):
        pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.raw_dir = raw_dir or os.path.join(pkg_root, "data", "raw", "judgments")
        self.interim_dir = interim_dir
        self.processed_dir = processed_dir or os.path.join(pkg_root, "data", "judgments")
        self.annotations_dir = annotations_dir

    def run_step(self, step_name, workers=1):
        """Run a specific step of the pipeline."""
        normalized_dir = os.path.join(self.interim_dir, "normalized_text")
        headers_dir = os.path.join(self.interim_dir, "headers_extracted")
        classified_dir = os.path.join(self.interim_dir, "classified")
        id_regen_dir = os.path.join(self.interim_dir, "id_regenerated")
        transitions_dir = os.path.join(self.interim_dir, "transitions_extracted")
        issues_dir = os.path.join(self.interim_dir, "issues_extracted")
        citations_dir = os.path.join(self.interim_dir, "citations_extracted")

        if step_name == "ingest":
            from .ingestion import IngestionProcessor
            IngestionProcessor(self.raw_dir, normalized_dir).run(workers=workers)
        elif step_name == "metadata":
            MetadataExtractionStep(normalized_dir, headers_dir).run()
        elif step_name == "issues":
            IssueExtractionStep(headers_dir, issues_dir).run()
        elif step_name == "classify":
            ClassificationStep(issues_dir, classified_dir).run()
        elif step_name == "id_regen" or step_name == "id_regeneration":
            IDRegenerationStep(classified_dir, id_regen_dir).run()
        elif step_name == "transitions":
            TransitionStep(id_regen_dir, transitions_dir).run()
        elif step_name == "citations":
            CitationExtractionStep(transitions_dir, citations_dir).run()
        elif step_name == "similarity":
            signal_dir = os.path.join(self.annotations_dir, "similarity/signals")
            edge_file = os.path.join(self.annotations_dir, "similarity/edges.jsonl")
            SimilarityProcessor(citations_dir, signal_dir, edge_file).run(workers=workers)
        elif step_name == "cluster":
            edge_file = os.path.join(self.annotations_dir, "similarity/edges.jsonl")
            cluster_file = os.path.join(self.annotations_dir, "similarity/clusters.json")
            refined_cluster_file = os.path.join(self.annotations_dir, "similarity/clusters_refined.json")
            signal_dir = os.path.join(self.annotations_dir, "similarity/signals")
            CentroidClusteter(edge_file, cluster_file).run()
            ClusterRefiner(cluster_file, refined_cluster_file, signal_dir).run()
        elif step_name == "consolidate":
            ConsolidationStep(citations_dir, self.processed_dir).run()
        else:
            print(f"Unknown step: {step_name}")

    def run_full_pipeline(self, workers=1):
        print("Starting Full Legal AI Toolkit Pipeline...")

        # Define paths
        normalized_dir = os.path.join(self.interim_dir, "normalized_text")
        headers_dir = os.path.join(self.interim_dir, "headers_extracted")
        issues_dir = os.path.join(self.interim_dir, "issues_extracted")
        classified_dir = os.path.join(self.interim_dir, "classified")
        id_regen_dir = os.path.join(self.interim_dir, "id_regenerated")
        transitions_dir = os.path.join(self.interim_dir, "transitions_extracted")
        citations_dir = os.path.join(self.interim_dir, "citations_extracted")

        # Step 1: Ingestion (generates TEMP_ IDs)
        from .ingestion import IngestionProcessor
        print("\n--- Step 1: Ingestion ---")
        IngestionProcessor(self.raw_dir, normalized_dir).run(workers=workers)

        # Step 2: Metadata Extraction (keeps TEMP_ IDs)
        print("\n--- Step 2: Metadata Extraction ---")
        MetadataExtractionStep(normalized_dir, headers_dir).run()

        # Step 3: Issue Extraction (MOVED UP - before classification)
        print("\n--- Step 3: Issue Extraction ---")
        IssueExtractionStep(headers_dir, issues_dir).run()

        # Step 4: Classification (uses issues as signals)
        print("\n--- Step 4: Classification ---")
        ClassificationStep(issues_dir, classified_dir).run()

        # Step 4.5: ID Regeneration (✅ NEW - AFTER classification)
        print("\n--- Step 4.5: ID Regeneration ---")
        print("  Regenerating IDs with proper court metadata and domain...")
        IDRegenerationStep(classified_dir, id_regen_dir).run()

        # Step 5: Transitions
        print("\n--- Step 5: Statutory Transitions ---")
        TransitionStep(id_regen_dir, transitions_dir).run()

        # Step 6: Citations
        print("\n--- Step 6: Citation Extraction ---")
        CitationExtractionStep(transitions_dir, citations_dir).run()

        # Step 7: Similarity (✅ FIXED - uses stable IDs from id_regen_dir)
        print("\n--- Step 7: Similarity Analysis ---")
        signal_dir = os.path.join(self.annotations_dir, "similarity/signals")
        edge_file = os.path.join(self.annotations_dir, "similarity/edges.jsonl")
        cluster_file = os.path.join(self.annotations_dir, "similarity/clusters.json")
        refined_cluster_file = os.path.join(self.annotations_dir, "similarity/clusters_refined.json")

        # Use citations_dir which has stable IDs (after id_regeneration)
        SimilarityProcessor(citations_dir, signal_dir, edge_file).run(workers=workers)
        CentroidClusteter(edge_file, cluster_file).run()
        ClusterRefiner(cluster_file, refined_cluster_file, signal_dir).run()

        # Step 8: Consolidate
        print("\n--- Step 8: Consolidation ---")
        ConsolidationStep(citations_dir, self.processed_dir).run()

        print("\nPipeline execution complete!")
        print(f"\n📊 Summary:")
        print(f"  - Normalized text: {normalized_dir}")
        print(f"  - Final output: {self.processed_dir}")
        print(f"  - Similarity edges: {edge_file}")
        print(f"  - Clusters: {refined_cluster_file}")
