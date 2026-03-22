"""
ID Regeneration Step

This step regenerates judgment IDs AFTER classification is complete,
ensuring the domain field in the ID is accurate.

This step runs AFTER:
- Metadata extraction (provides court_level, court_code, year)
- Classification (provides domain)

Before this step: TEMP_ABC123DEF456
After this step:  IN-HC-DEL-2023-CV-ABC123 (with correct domain)
"""

import re
from datetime import datetime
from .runner import BaseStep
from legal_ai_toolkit.utils.ids import generate_judgment_id, resolve_court_code

YEAR_HINT_PATTERNS = [
    r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?((?:19|20)\d{2}[/:](?:KHC|PHHC|DHC|MHC|BHC|APHC|TSHC|MPHC|JHC|JHHC|CGHC|GAHC|UHC|HHC|KER)(?:-[A-Z]+)?[/:][0-9A-Z-]+)",
    r"\[((?:19|20)\d{2}:(?:RJ-(?:JP|JD)|KHC|PHHC|DHC|MHC|BHC|APHC|TSHC|MPHC|JHC|JHHC|CGHC|GAHC|UHC|HHC|KER)[0-9A-Z:-]*)\]",
    r"\b((?:19|20)\d{2}:RJ-(?:JP|JD):[0-9A-Z-]+)\b",
    r"\b(?:NC\s*:?\s*)?((?:19|20)\d{2}):(?:KHC|PHHC|DHC|MHC|BHC|APHC|TSHC|MPHC|JHC|JHHC|CGHC|GAHC|UHC|HHC|KER)\b",
    r"(?:Date of Decision|Decision Date|Decided on|Pronounced on|Uploaded on|Reserved on|Order(?:\s+No\.)?|dt\.?)\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"\bSigning Date\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"\bDate\s*[:\-]?\s*((?:19|20)\d{2}[./-][0-9]{1,2}[./-][0-9]{1,2})",
    r"\bDate\s*[:\-]?\s*([0-9]{1,2}[-/](?:[A-Za-z]{3,9}|[0-9]{1,2})[-/][0-9]{4})",
    r"JUDGMENT\s+DATED\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"\(Uploaded on\s+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"\(Downloaded on\s+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Order\s+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"(?:Date of Decision|Decided on|Pronounced on|Uploaded on|Reserved on|Order(?:\s+No\.)?|dt\.?)\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"dated\s+the\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"((?:19|20)\d{2}\.\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-9]{1,2})",
]


class IDRegenerationStep(BaseStep):
    """Regenerate judgment IDs after classification is available."""

    def _extract_year_from_date(self, date_str):
        """Extract year from decision date string."""
        if not date_str or date_str == "UNKNOWN":
            return None

        # Try to extract 4-digit year
        match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if match:
            year = int(match.group(0))
            if 1850 <= year <= datetime.now().year:
                return year

        return None

    def _infer_year_from_text(self, text):
        header_text = text[:12000]
        for pattern in YEAR_HINT_PATTERNS:
            match = re.search(pattern, header_text, re.I)
            if not match:
                continue

            for group in match.groups():
                year = self._extract_year_from_date(group)
                if year is not None:
                    return year

        return 0

    def _infer_year_from_case_number(self, case_number):
        """Recover a plausible year from a parsed case number when dates are missing."""
        if not case_number or case_number == "UNKNOWN":
            return None

        years = [
            int(match.group(0))
            for match in re.finditer(r"\b(19|20)\d{2}\b", case_number)
        ]
        valid_years = [year for year in years if 1850 <= year <= datetime.now().year]
        if not valid_years:
            return None

        # Composite case numbers often mention prior connected matters; keep the most recent one.
        return max(valid_years)

    def process_item(self, data):
        """
        Regenerate ID with proper metadata AND classification.

        Args:
            data: Judgment data with metadata and classification

        Returns:
            Updated data with proper semantic ID
        """
        metadata = data.get("metadata", {})
        classification = data.get("classification", {})
        text = data.get("text", "")

        # Extract ID components
        court_level = metadata.get("court_level", "UNK")
        court_code = resolve_court_code(metadata.get("court", "UNK"))
        year = self._extract_year_from_date(metadata.get("decision_date", "UNKNOWN"))
        if year is None:
            year = self._infer_year_from_text(text)
        if not year:
            year = self._infer_year_from_case_number(metadata.get("case_number", "UNKNOWN")) or 0

        # ✅ NOW we have classification domain available
        domain = classification.get("domain", "unknown")

        # Generate proper semantic ID
        proper_id = generate_judgment_id(
            court_level=court_level,
            court_code=court_code,
            year=year,
            domain=domain,
            text=text
        )

        # Track ID change for audit trail
        old_id = data.get("judgment_id", "UNKNOWN")
        data["judgment_id"] = proper_id

        # Add to provenance tracking
        if "provenance" not in data:
            data["provenance"] = {}

        data["provenance"]["id_history"] = {
            "temporary_id": old_id if old_id.startswith("TEMP_") else None,
            "final_id": proper_id,
            "regeneration_step": "id_regeneration"
        }

        self.logger.info(f"ID regenerated: {old_id} → {proper_id}")

        return data
