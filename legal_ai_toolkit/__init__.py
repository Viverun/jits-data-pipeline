"""Legal AI Toolkit - Zero-ML Pipeline for Indian Legal Documents"""

__version__ = "1.0.0"

__all__ = ["PipelineOrchestrator", "DataAuditor", "load_processed_judgments", "load_clusters"]


def __getattr__(name):
    if name == "PipelineOrchestrator":
        from .pipeline.orchestrator import PipelineOrchestrator
        return PipelineOrchestrator
    if name == "DataAuditor":
        from .analytics.audit import DataAuditor
        return DataAuditor
    if name == "load_processed_judgments":
        from .utils.data_access import load_processed_judgments
        return load_processed_judgments
    if name == "load_clusters":
        from .utils.data_access import load_clusters
        return load_clusters
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
