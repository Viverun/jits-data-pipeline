"""Legal AI Toolkit - Zero-ML Pipeline for Indian Legal Documents"""

__version__ = "1.0.0"

from .pipeline.orchestrator import PipelineOrchestrator
from .analytics.audit import DataAuditor
from .utils.data_access import load_processed_judgments, load_clusters

__all__ = ["PipelineOrchestrator", "DataAuditor", "load_processed_judgments", "load_clusters"]
