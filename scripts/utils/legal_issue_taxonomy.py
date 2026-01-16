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
        text_lower = text.lower()
        
        for issue, data in cls.TAXONOMY.items():
            found_keywords = []
            for kw in data["keywords"]:
                # Count keyword occurrences to avoid false positives
                pattern = rf'\b{re.escape(kw)}\b'
                matches = re.findall(pattern, text_lower)
                if len(matches) >= 1:  # At least 1 occurrence
                    found_keywords.append(kw)
            
            found_sections = []
            for sec in data["sections"]:
                patterns = [
                    rf'\bArticle\s+{sec}\b',
                    rf'\bSection\s+{sec}\b',
                    rf'\bu/s\s+{sec}\b'
                ]
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        found_sections.append(sec)
                        break
            
            # CRITICAL FIX: Only add issue if evidence is strong enough
            if not (found_keywords or found_sections):
                continue
            
            # Calculate confidence with stricter thresholds
            confidence = "low"
            if found_keywords and found_sections:
                confidence = "high"
            elif len(found_keywords) >= 2:  # Multiple keyword mentions
                confidence = "medium"
            elif len(found_sections) >= 1:
                confidence = "medium"
            
            # FILTER: Only include medium/high confidence issues
            if confidence in ["medium", "high"]:
                issues[issue] = {
                    "statute": data["statute"],
                    "keywords": found_keywords,
                    "sections": found_sections,
                    "confidence": confidence,
                    "keyword_count": len(found_keywords),
                    "mention_count": sum(len(re.findall(rf'\b{re.escape(kw)}\b', text_lower)) for kw in found_keywords)
                }
        return issues
