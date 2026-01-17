from .runner import BaseStep
from legal_ai_toolkit.extraction.metadata import extract_header_metadata

class MetadataExtractionStep(BaseStep):
    def process_item(self, data):
        text = data.get("text", "")
        metadata = extract_header_metadata(text)
        data["metadata"] = metadata
        return data
