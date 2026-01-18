from .runner import BaseStep
from legal_ai_toolkit.extraction.citations import CitationExtractor
from legal_ai_toolkit.utils.database import PrecedentDatabase
import re

def extract_case_name(metadata):
    """Extract case name from metadata for self-citation exclusion."""
    # Try to get from petitioner/respondent
    if "petitioner" in metadata and "respondent" in metadata:
        petitioner = metadata["petitioner"]
        respondent = metadata["respondent"]
        return f"{petitioner} v. {respondent}"

    # Try to parse from case_number if it contains parties
    case_no = metadata.get("case_number", "")
    match = re.search(r'(.+?)\s+v[s]?\.?\s+(.+)', case_no, re.I)
    if match:
        return f"{match.group(1)} v. {match.group(2)}"

    return None

class CitationExtractionStep(BaseStep):
    def process_item(self, data):
        text = data.get("text", "")
        judgment_id = data.get("judgment_id", "unknown")
        metadata = data.get("metadata", {})

        if "annotations" not in data:
            data["annotations"] = {}

        # Extract case name for self-citation exclusion
        current_case_name = extract_case_name(metadata)

        # Extract citations with self-citation exclusion
        citations = CitationExtractor.extract(
            text,
            judgment_id=judgment_id,
            current_case_name=current_case_name
        )

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
