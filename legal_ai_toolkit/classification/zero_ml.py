import re
from typing import Dict, List, Tuple

class ZeroMLClassifier:
    """
    Court-safe, deterministic classifier.
    Implements cause-title authority and balanced signal scoring.
    """

    CAUSE_TITLE_PATTERNS = {
        "criminal": [
            r"\bCRIMINAL\s+APPEAL\b",
            r"\bCRL\.?\s*(APPEAL|MISC|REVISION)\b",
            r"\bBAIL\s+(APPLICATION|PETITION)\b",
            r"\bSTATE\s+VS\.\s+",
            r"\bU\/S\s+\d+\s+IPC\b.*\bVS\.",
        ],
        "civil": [
            r"\bCIVIL\s+APPEAL\b",
            r"\bC\.?A\.?\s+NO\.?\s+\d+\b",
            r"\bARBITRATION\s+PETITION\b",
            r"\bORIGINAL\s+SUIT\b",
            r"\bSPECIFIC\s+PERFORMANCE\b",
        ],
        "writ_supervisory": [
            r"\bWRIT\s+PETITION\b",
            r"\bARTICLE\s+226\b",
            r"\bARTICLE\s+227\b",
        ]
    }

    PROCEDURAL_VERBS = {"apply", "invoke", "grant", "reject", "quash", "uphold", "set aside", "remand"}
    CRIMINAL_KEYWORDS = {"accused", "prosecution", "bail", "convict", "sentence", "offence", "charge-sheet", "FIR"}
    CIVIL_KEYWORDS = {"plaintiff", "defendant", "injunction", "damages", "contract", "arbitration", "decree", "suit"}

    IPC_SECTION_PAT = r"(?:IPC|Indian Penal Code|Penal Code)\s+(\d+[A-Z\-]*)"
    CrPC_SECTION_PAT = r"(?:CrPC|Cr\.P\.C\.|Code of Criminal Procedure)\s+(\d+[A-Z\-]*)"
    CPC_SECTION_PAT = r"(?:CPC|C\.P\.C\.|Code of Civil Procedure)\s+(\d+[A-Z\-]*)"

    def classify_judgment_domain(self, text: str) -> Dict:
        """
        Main classification function with layered logic.
        """
        reasoning = []
        text_lower = text.lower()

        # --- PHASE 1: CAUSE TITLE ANALYSIS (Authoritative) ---
        header = text[:1500]  # First ~1500 chars for cause title
        locked_domain = self._analyze_cause_title(header)
        if locked_domain:
            reasoning.append(f"Domain locked by cause title: {locked_domain}")
            return {
                "domain": locked_domain,
                "confidence": "high",
                "reasoning": reasoning,
                "cause_title_locked": True
            }

        # --- PHASE 2: EXTRACT SIGNALS FOR 2-OF-3 RULE ---
        signals = self._extract_signals(text_lower)

        # --- PHASE 3: APPLY 2-OF-3 RULE ---
        domain, conf, rule_reason = self._apply_2_of_3_rule(signals)
        reasoning.extend(rule_reason)

        if domain == "unknown" and len(reasoning) == 0:
            reasoning.append("Insufficient signals for classification.")

        return {
            "domain": domain,
            "confidence": conf,
            "reasoning": reasoning,
            "cause_title_locked": False,
            "signals": {  # For audit trail
                "criminal_score": signals["criminal_score"],
                "civil_score": signals["civil_score"],
                "sections_found": signals["sections_found"]
            }
        }

    def _analyze_cause_title(self, header: str) -> str:
        """Analyze header for authoritative cause title patterns."""
        header_upper = header.upper()
        for domain, patterns in self.CAUSE_TITLE_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, header_upper):
                    return domain
        return ""

    def _extract_signals(self, text_lower: str) -> Dict:
        """Extract all classification signals."""
        signals = {
            "has_procedural_verb": any(verb in text_lower for verb in self.PROCEDURAL_VERBS),
            "criminal_keyword_count": sum(1 for kw in self.CRIMINAL_KEYWORDS if kw in text_lower),
            "civil_keyword_count": sum(1 for kw in self.CIVIL_KEYWORDS if kw in text_lower),
            "has_ipc_section": bool(re.search(self.IPC_SECTION_PAT, text_lower, re.IGNORECASE)),
            "has_crpc_section": bool(re.search(self.CrPC_SECTION_PAT, text_lower, re.IGNORECASE)),
            "has_cpc_section": bool(re.search(self.CPC_SECTION_PAT, text_lower, re.IGNORECASE)),
            "criminal_score": 0,
            "civil_score": 0,
            "sections_found": []
        }

        # Count sections
        for pat in [self.IPC_SECTION_PAT, self.CrPC_SECTION_PAT]:
            signals["sections_found"].extend(re.findall(pat, text_lower, re.IGNORECASE))
        # Scoring
        signals["criminal_score"] = (signals["has_ipc_section"] or signals["has_crpc_section"]) * 2
        signals["criminal_score"] += min(2, signals["criminal_keyword_count"])  # Cap keyword influence

        signals["civil_score"] = signals["has_cpc_section"] * 2
        signals["civil_score"] += min(2, signals["civil_keyword_count"])

        return signals

    def _apply_2_of_3_rule(self, signals: Dict) -> Tuple[str, str, List[str]]:
        """
        Implement the 2-of-3 rule for robust classification.
        """
        reasoning = []

        criminal_signals = [
            signals["has_ipc_section"] or signals["has_crpc_section"],
            signals["criminal_keyword_count"] >= 1,
            signals["has_procedural_verb"]
        ]
        civil_signals = [
            signals["has_cpc_section"],
            signals["civil_keyword_count"] >= 1,
            signals["has_procedural_verb"]
        ]

        criminal_score = sum(criminal_signals)
        civil_score = sum(civil_signals)

        if criminal_score >= 2 and civil_score < 2:
            reasoning.append(f"Criminal signals strong ({criminal_score}/3 factors).")
            return "criminal", "high", reasoning
        elif civil_score >= 2 and criminal_score < 2:
            reasoning.append(f"Civil signals strong ({civil_score}/3 factors).")
            return "civil", "high", reasoning
        elif criminal_score >= 2 and civil_score >= 2:
            reasoning.append(f"Mixed strong signals (C:{criminal_score}, V:{civil_score}).")
            return "mixed", "medium", reasoning
        elif criminal_score == 1 and civil_score == 0:
            return "criminal", "low", ["Single weak criminal signal."]
        elif civil_score == 1 and criminal_score == 0:
            return "civil", "low", ["Single weak civil signal."]
        else:
            return "unknown", "low", ["Insufficient or contradictory signals."]

# Singleton instance for easy import
classifier = ZeroMLClassifier()
def classify_judgment_domain(text: str) -> dict:
    """Public interface function."""
    return classifier.classify_judgment_domain(text)
