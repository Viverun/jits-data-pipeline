from .runner import BaseStep
from legal_ai_toolkit.classification.zero_ml import classifier


def classify_judgment(data):
    """Classify a judgment using the canonical zero-ML classifier."""
    return classifier.classify(data)


class ClassificationStep(BaseStep):
    def process_item(self, data):
        if "text" not in data:
            return None

        data["classification"] = classify_judgment(data)
        return data
