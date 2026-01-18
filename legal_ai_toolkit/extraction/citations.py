"""
Citation Extractor for Indian Legal Judgments

IMPROVEMENTS:
1. Self-citation exclusion - excludes references to the current case
2. Expanded citation patterns (AIR, SCC, ACC, SCR, etc.)
3. Case name extraction with context awareness
4. Filters out procedural references (State vs. Accused patterns)
5. Deduplication of citations
"""
import re
from typing import List, Dict, Optional


class CitationExtractor:
    """Extracts legal citations from judgment text."""

    # Citation reporter patterns (format: Reporter Year Volume Page)
    PATTERNS = {
        "AIR": r'AIR\s+(\d{4})\s+(SC|All|Bom|Cal|Del|Mad|Ker|Kant|Pat|Guj|Raj|MP|HP|Ori|AP|Punj|J&K)\s+(\d+)',
        "SCC": r'(\d{4})\s+\(?\d+\)?\s+SCC\s+(\d+)',
        "SCR": r'(\d{4})\s+\(?\d+\)?\s+SCR\s+(\d+)',
        "ACC": r'(\d{4})\s+\((\d+)\)\s+ACC\s+(\d+)',
        "JT": r'(\d{4})\s+\(?\d+\)?\s+JT\s+(\d+)',
        "SCALE": r'(\d{4})\s+\(?\d+\)?\s+SCALE\s+(\d+)',
        "KLT": r'(\d{4})\s+\(?\d+\)?\s+KLT\s+(\d+)',
        "BomCR": r'(\d{4})\s+\(?\d+\)?\s+Bom\s*CR\s+(\d+)',
        "DelLT": r'(\d{4})\s+\(?\d+\)?\s+Del\s*LT\s+(\d+)',
        "MadLJ": r'(\d{4})\s+\(?\d+\)?\s+Mad\s*LJ\s+(\d+)',
    }

    # Case name pattern - requires proper case name format
    # Excludes common procedural patterns like "State vs. Accused"
    CASE_NAME_PATTERN = r'(?:In|in)\s+([A-Z][a-zA-Z\s&.]+?)\s+(?:vs?\.?|versus)\s+([A-Z][a-zA-Z\s&.]+?)(?:\s+(?:\d{4}|\(|,|;))'

    # Patterns to exclude (procedural references, not actual citations)
    EXCLUDE_PATTERNS = [
        r'State\s+vs?\.?\s+\w+\s+(?:and|&)',  # "State vs. Accused and Others"
        r'appellant[s]?.*vs?\.?\s+State',  # "Appellant vs. State"
        r'Session\s+Trial\s+No',  # Session Trial references
        r'Case\s+Crime\s+No',  # Crime case numbers
    ]

    @classmethod
    def extract(cls, text: str, judgment_id: Optional[str] = None, current_case_name: Optional[str] = None) -> List[Dict]:
        """
        Extract citations from judgment text.

        Args:
            text: The judgment text to extract citations from
            judgment_id: Optional ID of the current judgment (for self-citation exclusion)
            current_case_name: Optional case name of current judgment (for self-citation exclusion)

        Returns:
            List of citation dictionaries with metadata
        """
        citations = []
        seen = set()  # For deduplication

        # Extract reporter citations (AIR, SCC, etc.)
        for reporter, pattern in cls.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                citation_text = match.group(0)

                # Skip if already seen
                if citation_text in seen:
                    continue

                # Extract components based on pattern groups
                groups = match.groups()
                year = groups[0]

                # Handle different group structures
                if len(groups) == 3:
                    court_or_volume = groups[1]
                    page = groups[2]
                else:
                    court_or_volume = None
                    page = groups[1] if len(groups) > 1 else groups[0]

                citation = {
                    "type": "reporter",
                    "reporter": reporter,
                    "year": year,
                    "page": page,
                    "raw": citation_text,
                    "start_pos": match.start(),
                    "end_pos": match.end()
                }

                if court_or_volume and court_or_volume.isdigit():
                    citation["volume"] = court_or_volume
                elif court_or_volume:
                    citation["court"] = court_or_volume

                citations.append(citation)
                seen.add(citation_text)

        # Extract case name citations
        for match in re.finditer(cls.CASE_NAME_PATTERN, text):
            # Normalize whitespace in extracted groups
            petitioner = re.sub(r'\s+', ' ', match.group(1)).strip()
            respondent = re.sub(r'\s+', ' ', match.group(2)).strip()

            # Additional cleanup for known prefixes
            petitioner = re.sub(r'^(?:Smt\.|Shri|Sri|Km\.)\s+', '', petitioner)

            citation_text = f"{petitioner} v. {respondent}"

            # Skip if already seen
            if citation_text in seen:
                continue

            # Exclude procedural references
            if cls._is_procedural_reference(match.group(0)):
                continue

            # Exclude self-citations (check petitioner and respondent separately)
            if current_case_name:
                if cls._is_self_citation(petitioner, current_case_name):
                    continue
                if cls._is_self_citation(respondent, current_case_name):
                    continue
                if cls._is_self_citation(citation_text, current_case_name):
                    continue

            citation = {
                "type": "case_name",
                "petitioner": petitioner,
                "respondent": respondent,
                "case_name": citation_text,
                "raw": match.group(0),
                "start_pos": match.start(),
                "end_pos": match.end()
            }

            citations.append(citation)
            seen.add(citation_text)

        return citations

    @staticmethod
    def _is_procedural_reference(text: str) -> bool:
        """Check if text matches procedural reference patterns (not actual citations)."""
        for pattern in CitationExtractor.EXCLUDE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _is_self_citation(citation_text: str, current_case_name: str) -> bool:
        """Check if citation refers to the current case (self-citation)."""
        # Normalize for comparison
        def normalize(text):
            # Lowercase
            text = text.lower()
            # Replace vs./v./versus with just 'v'
            text = re.sub(r'\bvs?\.?\b|\bversus\b', 'v', text)
            # Remove dots and extra spaces
            text = re.sub(r'\.', '', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

        citation_normalized = normalize(citation_text)
        current_normalized = normalize(current_case_name)

        # Check if they match (substring or exact match)
        return current_normalized in citation_normalized or citation_normalized in current_normalized


class CitationNormalizer:
    """Normalizes citations to standard formats."""

    @staticmethod
    def normalize(citation: Dict) -> str:
        """
        Normalize a citation to a standard string format.

        Args:
            citation: Citation dictionary from CitationExtractor

        Returns:
            Normalized citation string
        """
        if citation.get("type") == "reporter":
            reporter = citation.get("reporter", "UNK")
            year = citation.get("year", "0000")
            page = citation.get("page", "0")

            if "volume" in citation:
                return f"{reporter}_{year}_VOL{citation['volume']}_P{page}"
            else:
                return f"{reporter}_{year}_P{page}"

        elif citation.get("type") == "case_name":
            case_name = citation.get("case_name", "Unknown")
            # Replace spaces with underscores, remove special chars
            normalized = re.sub(r'[^\w\s]', '', case_name)
            normalized = re.sub(r'\s+', '_', normalized).upper()
            return normalized

        return "UNKNOWN_CITATION"

    @staticmethod
    def to_standard_format(citation: Dict) -> Optional[str]:
        """
        Convert citation to standard legal citation format.

        Args:
            citation: Citation dictionary

        Returns:
            Standard citation string (e.g., "AIR 2015 SC 123")
        """
        if citation.get("type") == "reporter":
            parts = [citation.get("reporter", "")]

            if "year" in citation:
                parts.append(citation["year"])

            if "court" in citation:
                parts.append(citation["court"])
            elif "volume" in citation:
                parts.append(f"({citation['volume']})")

            if "page" in citation:
                parts.append(citation["page"])

            return " ".join(parts)

        elif citation.get("type") == "case_name":
            return citation.get("case_name")

        return None
