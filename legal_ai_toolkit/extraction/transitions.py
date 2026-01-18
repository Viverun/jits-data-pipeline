"""
IPC to BNS Transition Extractor

REFACTORED (Phase 4):
- Now uses SectionExtractor from sections.py for consistent section detection
- Cleaner pattern matching
- Better temporal validation
- Integration with new extraction modules
"""
import re
from datetime import datetime
from typing import List, Dict, Optional
from legal_ai_toolkit.extraction.sections import SectionExtractor
from legal_ai_toolkit.utils.mappings import IPCBNSTransitionDB


class TransitionExtractor:
    """
    Extracts IPC→BNS transition pairs with legal safeguards.

    IMPROVEMENTS:
    - Uses SectionExtractor for consistent section detection
    - Cleaner explicit pair detection
    - Better temporal guardrails
    - Proper validation against official mapping
    """

    # BNS enactment date
    BNS_ENACTMENT_DATE = datetime(2024, 7, 1)

    # Patterns for finding explicit IPC→BNS pairs in text
    EXPLICIT_TRANSITION_PATTERNS = [
        # "IPC 498-A (now BNS 123)"
        r'IPC\s+(\d+[A-Z\-]*)\s*(?:\(|,|;|\.)\s*(?:now\s+)?(?:BNS|Bharatiya Nyaya Sanhita)\s+(\d+[A-Z\-]*)',
        # "Section 498-A IPC ... Section 123 BNS"
        r'Section\s+(\d+[A-Z\-]*)\s+(?:IPC|Indian Penal Code).{0,100}?Section\s+(\d+[A-Z\-]*)\s+(?:BNS|Bharatiya Nyaya Sanhita)',
        # "BNS 123 (formerly IPC 498-A)"
        r'BNS\s+(\d+[A-Z\-]*)\s*(?:\(|,|;|\.)\s*(?:earlier|formerly|previously)\s+(?:IPC|Indian Penal Code)\s+(\d+[A-Z\-]*)',
    ]

    @classmethod
    def extract(cls, text: str, judgment_date: Optional[str] = None) -> List[Dict]:
        """
        Extract IPC→BNS transitions from judgment text.

        Args:
            text: Judgment text to analyze
            judgment_date: Date in YYYY-MM-DD format (for temporal validation)

        Returns:
            List of transition dictionaries with validation metadata
        """
        transitions = []

        # --- TEMPORAL GUARDRAIL ---
        is_pre_bns = cls._is_pre_bns_judgment(judgment_date)

        # --- 1. EXTRACT EXPLICIT TRANSITION PAIRS ---
        explicit_transitions = cls._extract_explicit_pairs(text, is_pre_bns)
        transitions.extend(explicit_transitions)

        # --- 2. INFER TRANSITIONS FROM STANDALONE IPC SECTIONS ---
        # Only infer for post-BNS judgments
        if not is_pre_bns:
            inferred_transitions = cls._infer_from_ipc_sections(text)
            transitions.extend(inferred_transitions)
        else:
            # For pre-BNS judgments, just record IPC sections as background
            background_sections = cls._record_pre_bns_sections(text)
            transitions.extend(background_sections)

        # --- 3. DEDUPLICATE ---
        return cls._deduplicate(transitions)

    @classmethod
    def _is_pre_bns_judgment(cls, judgment_date: Optional[str]) -> bool:
        """Check if judgment is before BNS enactment."""
        if not judgment_date:
            return False

        try:
            jd = datetime.strptime(judgment_date, "%Y-%m-%d")
            return jd < cls.BNS_ENACTMENT_DATE
        except ValueError:
            return False

    @classmethod
    def _extract_explicit_pairs(cls, text: str, is_pre_bns: bool) -> List[Dict]:
        """Extract explicitly mentioned IPC→BNS transition pairs."""
        transitions = []

        for pattern in cls.EXPLICIT_TRANSITION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ipc = match.group(1).upper()
                bns = match.group(2).upper() if len(match.groups()) > 1 else None

                # Validate against official mapping
                official = IPCBNSTransitionDB.get(ipc)
                is_validated = bool(official and official.get("bns") == bns)

                transition = {
                    "ipc": ipc,
                    "bns": bns,
                    "source": "explicit_pair",
                    "validated": is_validated,
                    "risk": official.get("risk", "unknown") if official else "unknown",
                    "confidence": "high",
                    "context_snippet": match.group(0)[:150]
                }

                if is_pre_bns:
                    transition["temporal_warning"] = "BNS mentioned in pre-enactment judgment. Verify applicability."

                transitions.append(transition)

        return transitions

    @classmethod
    def _infer_from_ipc_sections(cls, text: str) -> List[Dict]:
        """Infer BNS sections from standalone IPC mentions using SectionExtractor."""
        transitions = []

        # Use our new SectionExtractor
        sections = SectionExtractor.extract(text)

        # Filter for IPC sections only
        ipc_sections = [s for s in sections if s.get("act") == "IPC"]

        for section_obj in ipc_sections:
            ipc = section_obj.get("section", "").upper()

            # Look up official mapping
            official = IPCBNSTransitionDB.get(ipc)

            if official and "bns" in official:
                transitions.append({
                    "ipc": ipc,
                    "bns": official["bns"],
                    "source": "inferred_from_ipc",
                    "validated": False,  # Inferred, not explicitly stated
                    "risk": official.get("risk", "medium"),
                    "confidence": "low",
                    "requires_judicial_confirmation": True,
                    "note": f"Inferred from standalone IPC {ipc} mention. Not validated by judgment text."
                })

        return transitions

    @classmethod
    def _record_pre_bns_sections(cls, text: str) -> List[Dict]:
        """Record IPC sections from pre-BNS judgments as background only."""
        transitions = []

        # Use our new SectionExtractor
        sections = SectionExtractor.extract(text)

        # Filter for IPC sections
        ipc_sections = [s for s in sections if s.get("act") == "IPC"]

        for section_obj in ipc_sections:
            ipc = section_obj.get("section", "").upper()

            transitions.append({
                "ipc": ipc,
                "bns": None,
                "source": "pre_bns_background",
                "validated": False,
                "risk": "none",
                "confidence": "low",
                "note": "Pre-BNS judgment. IPC section recorded as background only."
            })

        return transitions

    @staticmethod
    def _deduplicate(transitions: List[Dict]) -> List[Dict]:
        """Remove duplicate transitions."""
        seen = set()
        unique = []

        for t in transitions:
            key = (t.get("ipc"), t.get("bns"))
            if key not in seen:
                seen.add(key)
                unique.append(t)

        return unique
