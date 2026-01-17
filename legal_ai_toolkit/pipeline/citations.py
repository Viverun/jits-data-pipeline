from .runner import BaseStep
from legal_ai_toolkit.extraction.citations import CitationExtractor
from legal_ai_toolkit.utils.database import PrecedentDatabase

class CitationExtractionStep(BaseStep):
    def process_item(self, data):
        text = data.get("text", "")
        if "annotations" not in data:
            data["annotations"] = {}

        # Extract citations
        citations = CitationExtractor.extract(text)

        # Match against landmark database
        matched_landmarks = []
        for citation in citations:
            citation_text = citation.get("raw", "")
            precedent = PrecedentDatabase.match_citation(citation_text)
            if precedent:
                matched_landmarks.append(precedent)
                citation["is_landmark"] = True
                citation["precedent_id"] = precedent["precedent_id"]
            else:
                citation["is_landmark"] = False

        data["annotations"]["citations"] = citations
        data["annotations"]["matched_landmarks"] = matched_landmarks

        # Find potentially relevant precedents based on issues
        if "issues" in data.get("annotations", {}):
            issues = list(data["annotations"]["issues"].keys())
            sections = []
            if "statutory_transitions" in data:
                sections = data["statutory_transitions"].get("ipc_detected", [])

            relevant_precedents = PrecedentDatabase.find_relevant_precedents(issues, sections)
            data["annotations"]["suggested_precedents"] = relevant_precedents[:5]  # Top 5

        return data
