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
from .runner import BaseStep
from legal_ai_toolkit.utils.ids import generate_judgment_id


class IDRegenerationStep(BaseStep):
    """Regenerate judgment IDs after classification is available."""

    def _extract_year_from_date(self, date_str):
        """Extract year from decision date string."""
        if not date_str or date_str == "UNKNOWN":
            from datetime import datetime
            return datetime.now().year

        # Try to extract 4-digit year
        match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if match:
            return int(match.group(0))

        from datetime import datetime
        return datetime.now().year

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
        court_code = metadata.get("court", "UNK")[:3]
        year = self._extract_year_from_date(metadata.get("decision_date", "UNKNOWN"))

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
