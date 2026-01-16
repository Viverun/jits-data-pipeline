import re

class LegalIssueTaxonomy:
    TAXONOMY = {
        # --- CRIMINAL ---
        "bail": {
            "keywords": ["bail", "anticipatory bail", "regular bail", "interim bail"],
            "sections": ["437", "438", "439", "167"],
            "statute": "CrPC / BNSS"
        },
        "quashing": {
            "keywords": ["quash", "quashing", "inherent powers"],
            "sections": ["482"],
            "statute": "CrPC / BNSS"
        },
        "sentencing": {
            "keywords": ["sentence", "sentencing", "quantum of punishment"],
            "sections": ["302", "376", "420", "304B", "395"],
            "statute": "IPC / BNS"
        },
        # --- SERVICE MATTERS (NEW) ---
        "seniority_promotion": {
            "keywords": ["seniority", "promotion", "DPC", "selection list", "Article 16"],
            "sections": [],
            "statute": "Service Rules / Constitution"
        },
        "pension_gratuity": {
            "keywords": ["pension", "gratuity", "retiral benefits", "family pension"],
            "sections": [],
            "statute": "Pension Rules"
        },
        "disciplinary_proceedings": {
            "keywords": ["departmental inquiry", "suspension", "misconduct", "termination"],
            "sections": ["311"],
            "statute": "Service Rules / Article 311"
        },
        # --- CIVIL ---
        "specific_performance": {
            "keywords": ["specific performance", "sale agreement", "contract enforcement"],
            "sections": ["10", "16", "20"],
            "statute": "Specific Relief Act"
        },
        "arbitration": {
            "keywords": ["arbitration", "arbitral award", "section 34", "set aside award"],
            "sections": ["11", "34", "36"],
            "statute": "Arbitration Act"
        },
        # --- PROCEDURAL ---
        "jurisdiction": {
            "keywords": ["jurisdiction", "territorial", "pecuniary"],
            "sections": ["9", "20"],
            "statute": "CPC"
        },
        "limitation": {
            "keywords": ["limitation", "time barred", "delay", "condonation"],
            "sections": ["3", "5"],
            "statute": "Limitation Act"
        }
    }

    @classmethod
    def extract(cls, text: str):
        issues = {}
        for issue, data in cls.TAXONOMY.items():
            found_keywords = [kw for kw in data["keywords"] if re.search(rf'\b{kw}\b', text, re.IGNORECASE)]
            found_sections = [sec for sec in data["sections"] if re.search(rf'\b{sec}\b', text)]
            if found_keywords or found_sections:
                issues[issue] = {
                    "statute": data["statute"],
                    "keywords": found_keywords,
                    "sections": found_sections,
                    "confidence": "high" if found_keywords and found_sections else "medium"
                }
        return issues
