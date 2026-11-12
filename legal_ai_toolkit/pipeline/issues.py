from .runner import BaseStep
from legal_ai_toolkit.utils.taxonomy import LegalIssueTaxonomy

class IssueExtractionStep(BaseStep):
    def process_item(self, data):
        text = data.get("text", "")
        # Ensure annotations object exists
        if "annotations" not in data:
            data["annotations"] = {}

        # Extract issues using the taxonomy utility
        issues = LegalIssueTaxonomy.extract(text)
        data["annotations"]["issues"] = issues
        return data
