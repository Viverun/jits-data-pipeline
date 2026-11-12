import re
from typing import Dict, Iterable, List, Optional, Tuple


class ZeroMLClassifier:
    """
    Court-safe, deterministic classifier with explicit service-domain support.

    The classifier prefers authoritative cause-title patterns when they are
    specific enough, then falls back to multi-signal evidence across
    statutes/sections, keywords, and extracted issues.
    """

    CAUSE_TITLE_PATTERNS = {
        "criminal": [
            r"\bCRIMINAL\s+APPEAL\b",
            r"\bCRIMINAL\s+MISC",
            r"\bCRL\.?\s*(APPEAL|MISC|REVISION)\b",
            r"\bBAIL\s+(APPLICATION|PETITION)\b",
            r"\bSTATE\s+VS\.?\s+",
            r"\bSTATE\s+V\.?\s+",
        ],
        "civil": [
            r"\bCIVIL\s+APPEAL\b",
            r"\bCIVIL\s+REVISION\b",
            r"\bC\.?A\.?\s+NO\.?\s+\d+\b",
            r"\bARBITRATION\s+PETITION\b",
            r"\bORIGINAL\s+SUIT\b",
            r"\bSPECIFIC\s+PERFORMANCE\b",
        ],
        "service": [
            r"\bCENTRAL\s+ADMINISTRATIVE\s+TRIBUNAL\b",
            r"\bSTATE\s+ADMINISTRATIVE\s+TRIBUNAL\b",
            r"\bSERVICE\s+MATTERS?\b",
            r"\bDISCIPLINARY\s+PROCEEDINGS?\b",
        ],
    }

    WRIT_SUPERVISORY_PATTERNS = [
        r"\bWRIT\s+PETITION\b",
        r"\bC\.?W\.?P\.?\b",
        r"\bARTICLE\s+226\b",
        r"\bARTICLE\s+227\b",
    ]

    CRIMINAL_STATUTES = [
        (r"\bI\.?P\.?C\.?\b", "IPC"),
        (r"\bCr\.?P\.?C\.?\b", "CrPC"),
        (r"\bB\.?N\.?S\.?\b", "BNS"),
        (r"\bB\.?N\.?S\.?S\.?\b", "BNSS"),
        (r"\bIndian Penal Code\b", "Indian Penal Code"),
        (r"\bCode of Criminal Procedure\b", "Code of Criminal Procedure"),
        (r"\bNDPS\b", "NDPS"),
        (r"\bPOCSO\b", "POCSO"),
        (r"\bUAPA\b", "UAPA"),
        (r"\bPMLA\b", "PMLA"),
    ]
    CIVIL_STATUTES = [
        (r"\bC\.?P\.?C\.?\b", "CPC"),
        (r"\bCode of Civil Procedure\b", "Code of Civil Procedure"),
        (r"\bContract Act\b", "Contract Act"),
        (r"\bArbitration\b", "Arbitration"),
        (r"\bSpecific Relief\b", "Specific Relief"),
        (r"\bTransfer of Property\b", "Transfer of Property"),
        (r"\bSuccession Act\b", "Succession Act"),
        (r"\bLimitation Act\b", "Limitation Act"),
        (r"\bNegotiable Instruments\b", "Negotiable Instruments"),
        (r"\bMotor Vehicles Act\b", "Motor Vehicles Act"),
    ]
    SERVICE_STATUTES = [
        (r"\bArticle\s+311\b", "Article 311"),
        (r"\bArticle\s+16\b", "Article 16"),
        (r"\bFundamental Rules?\b", "Fundamental Rules"),
        (r"\bPension Rules?\b", "Pension Rules"),
        (r"\bService Rules?\b", "Service Rules"),
        (r"\bIndustrial Disputes\b", "Industrial Disputes"),
        (r"\bPayment of Gratuity\b", "Payment of Gratuity"),
        (r"\bAdministrative Tribunal\b", "Administrative Tribunal"),
    ]

    CRIMINAL_KEYWORDS = {
        "accused",
        "prosecution",
        "bail",
        "convict",
        "sentence",
        "offence",
        "offense",
        "charge-sheet",
        "fir",
        "custody",
        "acquittal",
    }
    CIVIL_KEYWORDS = {
        "plaintiff",
        "defendant",
        "injunction",
        "damages",
        "contract",
        "arbitration",
        "decree",
        "suit",
        "specific performance",
    }
    SERVICE_KEYWORDS = {
        "seniority",
        "promotion",
        "regularization",
        "reinstatement",
        "pension",
        "gratuity",
        "retiral benefits",
        "departmental inquiry",
        "disciplinary proceedings",
        "suspension",
        "misconduct",
        "superannuation",
        "service benefits",
        "back wages",
    }

    CRIMINAL_ISSUES = {"bail", "quashing", "sentencing"}
    CIVIL_ISSUES = {"specific_performance", "arbitration", "jurisdiction", "limitation"}
    SERVICE_ISSUES = {
        "seniority_promotion",
        "pension_gratuity",
        "disciplinary_proceedings",
        "reinstatement_service",
        "service_conditions",
        "tenure_appointment",
    }

    IPC_SECTION_PAT = r"(?:IPC|Indian Penal Code|Penal Code)\s+(\d+[A-Z\-]*)"
    CRPC_SECTION_PAT = r"(?:CrPC|Cr\.P\.C\.|Code of Criminal Procedure)\s+(\d+[A-Z\-]*)"
    CPC_SECTION_PAT = r"(?:CPC|C\.P\.C\.|Code of Civil Procedure)\s+(\d+[A-Z\-]*)"
    ARTICLE_311_PAT = r"\bArticle\s+311\b"

    def classify(self, data: Dict) -> Dict:
        text = data.get("text", "")
        issues = data.get("annotations", {}).get("issues", {})
        return self.classify_judgment_domain(text=text, issues=issues)

    def classify_judgment_domain(self, text: str, issues: Optional[Dict] = None) -> Dict:
        issues = issues or {}
        reasoning: List[str] = []
        header = text[:1500]

        locked_domain = self._analyze_cause_title(header)
        signals = self._extract_signals(text, issues)
        evidence = self._build_evidence(signals)
        scores = {domain: sum(domain_evidence.values()) for domain, domain_evidence in evidence.items()}

        if locked_domain:
            reasoning.append(f"Domain locked by cause title: {locked_domain}")
            return {
                "domain": locked_domain,
                "confidence": "high",
                "reasoning": reasoning,
                "cause_title_locked": True,
                "signals": signals,
                "scores": scores,
            }

        if signals["writ_supervisory"] and (
            evidence["service"]["statute_or_section"] or
            evidence["service"]["keywords"] or
            evidence["service"]["issues"]
        ):
            evidence["service"]["writ_context"] = True
            scores["service"] = sum(evidence["service"].values())
            reasoning.append("Writ-supervisory posture paired with independent service signals.")

        domain, confidence, decision_reason = self._decide_domain(scores, evidence)
        reasoning.extend(decision_reason)

        return {
            "domain": domain,
            "confidence": confidence,
            "reasoning": reasoning,
            "cause_title_locked": False,
            "signals": signals,
            "scores": scores,
        }

    def _analyze_cause_title(self, header: str) -> str:
        header_upper = header.upper()
        for domain, patterns in self.CAUSE_TITLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, header_upper):
                    return domain
        return ""

    def _extract_signals(self, text: str, issues: Dict) -> Dict:
        issue_names = set(issues.keys()) if isinstance(issues, dict) else set(issues or [])
        signals = {
            "criminal": [],
            "civil": [],
            "service": [],
            "writ_supervisory": [],
        }

        self._extend_matches(signals["criminal"], text, self.CRIMINAL_STATUTES)
        self._extend_matches(signals["civil"], text, self.CIVIL_STATUTES)
        self._extend_matches(signals["service"], text, self.SERVICE_STATUTES)

        if re.search(self.IPC_SECTION_PAT, text, re.IGNORECASE):
            signals["criminal"].append("IPC section")
        if re.search(self.CRPC_SECTION_PAT, text, re.IGNORECASE):
            signals["criminal"].append("CrPC section")
        if re.search(self.CPC_SECTION_PAT, text, re.IGNORECASE):
            signals["civil"].append("CPC section")
        if re.search(self.ARTICLE_311_PAT, text, re.IGNORECASE):
            signals["service"].append("Article 311")

        for keyword in sorted(self.CRIMINAL_KEYWORDS):
            if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                signals["criminal"].append(keyword)
        for keyword in sorted(self.CIVIL_KEYWORDS):
            if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                signals["civil"].append(keyword)
        for keyword in sorted(self.SERVICE_KEYWORDS):
            if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                signals["service"].append(keyword)

        for issue_name in sorted(issue_names):
            if issue_name in self.CRIMINAL_ISSUES:
                signals["criminal"].append(f"issue:{issue_name}")
            if issue_name in self.CIVIL_ISSUES:
                signals["civil"].append(f"issue:{issue_name}")
            if issue_name in self.SERVICE_ISSUES:
                signals["service"].append(f"issue:{issue_name}")

        for pattern in self.WRIT_SUPERVISORY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                signals["writ_supervisory"].append(pattern)

        for key in signals:
            signals[key] = sorted(set(signals[key]))

        return signals

    def _build_evidence(self, signals: Dict) -> Dict[str, Dict[str, bool]]:
        return {
            "criminal": {
                "statute_or_section": self._has_any(signals["criminal"], {"section", "IPC", "CrPC", "BNS", "BNSS", "Code of Criminal Procedure", "Indian Penal Code", "NDPS", "POCSO", "UAPA", "PMLA"}),
                "keywords": self._has_keyword_matches(
                    signals["criminal"],
                    {"IPC", "CrPC", "BNS", "BNSS", "Indian Penal Code", "Code of Criminal Procedure", "NDPS", "POCSO", "UAPA", "PMLA", "IPC section", "CrPC section"},
                ),
                "issues": self._has_issue_evidence(signals["criminal"]),
            },
            "civil": {
                "statute_or_section": self._has_any(signals["civil"], {"section", "CPC", "Code of Civil Procedure", "Contract Act", "Arbitration", "Specific Relief", "Transfer of Property", "Succession Act", "Limitation Act", "Negotiable Instruments", "Motor Vehicles Act"}),
                "keywords": self._has_keyword_matches(
                    signals["civil"],
                    {"CPC", "Code of Civil Procedure", "Contract Act", "Arbitration", "Specific Relief", "Transfer of Property", "Succession Act", "Limitation Act", "Negotiable Instruments", "Motor Vehicles Act", "CPC section"},
                ),
                "issues": self._has_issue_evidence(signals["civil"]),
            },
            "service": {
                "statute_or_section": self._has_any(signals["service"], {"Article 311", "Article 16", "Fundamental Rules", "Pension Rules", "Service Rules", "Industrial Disputes", "Payment of Gratuity", "Administrative Tribunal"}),
                "keywords": self._has_keyword_matches(
                    signals["service"],
                    {"Article 311", "Article 16", "Fundamental Rules", "Pension Rules", "Service Rules", "Industrial Disputes", "Payment of Gratuity", "Administrative Tribunal"},
                ),
                "issues": self._has_issue_evidence(signals["service"]),
                "writ_context": False,
            },
        }

    def _decide_domain(self, scores: Dict[str, int], evidence: Dict[str, Dict[str, bool]]) -> Tuple[str, str, List[str]]:
        reasoning: List[str] = []
        strong_domains = [domain for domain, score in scores.items() if score >= 2]

        if len(strong_domains) >= 2:
            reasoning.append(
                "Multiple domains have strong evidence: "
                + ", ".join(f"{domain}={scores[domain]}" for domain in sorted(strong_domains))
            )
            return "mixed", "medium", reasoning

        if len(strong_domains) == 1:
            domain = strong_domains[0]
            confidence = "high" if scores[domain] >= 3 else "medium"
            reasoning.append(f"{domain.capitalize()} evidence is strongest ({scores[domain]} signals).")
            return domain, confidence, reasoning

        best_domain = max(scores, key=scores.get)
        if scores[best_domain] == 1:
            reasoning.append(f"Single weak {best_domain} signal.")
            return best_domain, "low", reasoning

        return "unknown", "low", ["Insufficient or contradictory signals."]

    @staticmethod
    def _extend_matches(dest: List[str], text: str, patterns: Iterable[Tuple[str, str]]) -> None:
        for pattern, label in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                dest.append(label)

    @staticmethod
    def _has_any(values: List[str], needles: Iterable[str]) -> bool:
        return any(any(needle in value for needle in needles) for value in values)

    @staticmethod
    def _has_issue_evidence(values: List[str]) -> bool:
        return any(value.startswith("issue:") for value in values)

    @staticmethod
    def _has_keyword_matches(values: List[str], excluded: Iterable[str]) -> bool:
        excluded_values = set(excluded)
        return any(
            not value.startswith("issue:")
            and value not in excluded_values
            and "section" not in value
            for value in values
        )


classifier = ZeroMLClassifier()


def classify_judgment_domain(text: str, issues: Optional[Dict] = None) -> dict:
    """Public interface function."""
    return classifier.classify_judgment_domain(text=text, issues=issues)
