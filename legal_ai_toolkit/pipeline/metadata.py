from .runner import BaseStep
from legal_ai_toolkit.extraction.metadata import extract_header_metadata

class MetadataExtractionStep(BaseStep):
    """
    Extract metadata from judgment headers.

    NOTE: This step does NOT regenerate IDs. ID regeneration happens
    in IDRegenerationStep AFTER classification is complete, ensuring
    the domain field in the ID is accurate.
    """

    def process_item(self, data):
        text = data.get("text", "")
        metadata = extract_header_metadata(text)
        data["metadata"] = metadata

        # Keep the temporary ID from ingestion
        # It will be regenerated in IDRegenerationStep (after classification)

        return data
