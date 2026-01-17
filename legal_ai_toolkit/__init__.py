"""Legal AI Toolkit - Zero-ML Pipeline for Indian Legal Documents"""

__version__ = "1.0.0"

from legal_ai_toolkit.pipeline.ingestion import ingest_judgment
from legal_ai_toolkit.pipeline.classification import classify_judgment
from legal_ai_toolkit.pipeline.extraction import extract_features
from legal_ai_toolkit.pipeline.clustering import cluster_judgments

__all__ = ["ingest_judgment", "classify_judgment", "extract_features", "cluster_judgments"]
