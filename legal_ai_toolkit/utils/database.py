import re
import json
from pathlib import Path


class PrecedentDatabase:
    """
    Authoritative landmark judgment database
    Integrates with your citation extraction
    """

    LANDMARKS = {}

    @classmethod
    def _ensure_loaded(cls):
        if not cls.LANDMARKS:
            data_path = Path(__file__).parent.parent / "data" / "landmarks.json"
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    cls.LANDMARKS = json.load(f)
            else:
                # Fallback to empty or minimal set if file missing
                cls.LANDMARKS = {}

    @staticmethod
    def _normalize_for_match(text: str) -> str:
        """Helper to normalize text for matching"""
        if not text:
            return ""
        # Lowercase, remove special chars, normalize whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @classmethod
    def match_citation(cls, citation_text: str):
        """Match extracted citation to known landmark"""
        cls._ensure_loaded()
        citation_upper = citation_text.upper()
        citation_norm = cls._normalize_for_match(citation_text)

        for prec_id, data in cls.LANDMARKS.items():
            # 1. Match by short name (normalized)
            short_name_norm = cls._normalize_for_match(data["short_name"])
            if short_name_norm and short_name_norm in citation_norm:
                return {
                    "precedent_id": prec_id,
                    **data,
                    "matched_by": "short_name"
                }

            # 2. Match by aliases
            for alias in data.get("aliases", []):
                alias_norm = cls._normalize_for_match(alias)
                if alias_norm and alias_norm in citation_norm:
                    return {
                        "precedent_id": prec_id,
                        **data,
                        "matched_by": "alias"
                    }

            # 3. Match by year and common reporters
            if str(data["year"]) in citation_text:
                reporters = ["SCC", "AIR", "SCR", "JT", "SCALE", "ACC"]
                for rep in reporters:
                    if rep in citation_upper:
                        return {
                            "precedent_id": prec_id,
                            **data,
                            "matched_by": f"year_{rep.lower()}"
                        }

        return None

    @classmethod
    def find_relevant_precedents(cls, issues: list, sections: list):
        """Find precedents relevant to given issues/sections"""
        cls._ensure_loaded()
        relevant = []

        for prec_id, data in cls.LANDMARKS.items():
            # Check issue overlap
            issue_match = any(issue in data["issues"] for issue in issues)

            # Check provision overlap
            section_match = any(
                any(sec in prov for sec in sections)
                for prov in data["provisions"]
            )

            if issue_match or section_match:
                relevance_score = 0
                if issue_match:
                    relevance_score += 2
                if section_match:
                    relevance_score += 1

                relevant.append({
                    "precedent_id": prec_id,
                    **data,
                    "relevance_score": relevance_score
                })

        # Sort by relevance
        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant

    @classmethod
    def get_all_precedents(cls):
        """Get all precedents as list"""
        cls._ensure_loaded()
        return [
            {"precedent_id": pid, **data}
            for pid, data in cls.LANDMARKS.items()
        ]
