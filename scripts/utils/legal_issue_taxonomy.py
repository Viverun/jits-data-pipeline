import re

class LegalIssueTaxonomy:
    """
    Rule-based legal issue taxonomy for Indian courts
    """

    TAXONOMY = {

        # ────────────── CRIMINAL ──────────────

        "bail": {
            "keywords": [
                "bail", "anticipatory bail", "regular bail", "interim bail"
            ],
            "sections": [
                "437", "438", "439", "167"
            ],
            "statute": "CrPC / BNSS"
        },

        "quashing": {
            "keywords": [
                "quash", "quashing", "inherent powers"
            ],
            "sections": [
                "482"
            ],
            "statute": "CrPC / BNSS"
        },

        "sentencing": {
            "keywords": [
                "sentence", "sentencing", "quantum of punishment"
            ],
            "sections": [
                "302", "376", "420"
            ],
            "statute": "IPC / BNS"
        },

        "evidence_admissibility": {
            "keywords": [
                "admissibility", "electronic evidence", "confession",
                "forensic", "witness credibility"
            ],
            "sections": [
                "65B", "24", "27", "45"
            ],
            "statute": "IEA / BSA"
        },

        # ────────────── CIVIL ──────────────

        "limitation": {
            "keywords": [
                "limitation", "time barred", "delay", "condonation"
            ],
            "sections": [
                "3", "5"
            ],
            "statute": "Limitation Act"
        },

        "injunction": {
            "keywords": [
                "injunction", "temporary injunction", "status quo"
            ],
            "sections": [
                "36", "37", "38", "39"
            ],
            "statute": "Specific Relief Act"
        },

        "specific_performance": {
            "keywords": [
                "specific performance", "contract enforcement"
            ],
            "sections": [
                "10", "16"
            ],
            "statute": "Specific Relief Act"
        },

        "arbitration": {
            "keywords": [
                "arbitration", "arbitral award", "section 34",
                "set aside award"
            ],
            "sections": [
                "11", "34", "36"
            ],
            "statute": "Arbitration Act"
        },

        # ────────────── PROCEDURAL ──────────────

        "jurisdiction": {
            "keywords": [
                "jurisdiction", "territorial jurisdiction",
                "pecuniary jurisdiction"
            ],
            "sections": [
                "9", "20"
            ],
            "statute": "CPC"
        },

        "maintainability": {
            "keywords": [
                "maintainable", "maintainability", "locus standi",
                "cause of action"
            ],
            "sections": [
                "9", "11"
            ],
            "statute": "CPC"
        }
    }

    @classmethod
    def extract(cls, text: str):
        issues = {}

        for issue, data in cls.TAXONOMY.items():
            found_keywords = []
            found_sections = []

            for kw in data["keywords"]:
                if re.search(rf'\b{kw}\b', text, re.IGNORECASE):
                    found_keywords.append(kw)

            for sec in data["sections"]:
                if re.search(rf'\b{sec}\b', text):
                    found_sections.append(sec)

            if found_keywords or found_sections:
                issues[issue] = {
                    "statute": data["statute"],
                    "keywords": found_keywords,
                    "sections": found_sections,
                    "confidence": cls._confidence(found_keywords, found_sections)
                }

        return issues

    @staticmethod
    def _confidence(keywords, sections):
        if keywords and sections:
            return "high"
        if keywords or sections:
            return "medium"
        return "low"
