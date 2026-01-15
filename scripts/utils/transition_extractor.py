# scripts/utils/transition_extractor.py - CRITICAL FIXES APPLIED
import re
from datetime import datetime
from scripts.utils.ipc_bns_mapping import IPCBNSTransitionDB

class TransitionExtractor:
    """
    Extracts IPC→BNS transition pairs with legal safeguards.
    FIXES APPLIED:
    1. Inferred mappings are LOW confidence, NOT validated.
    2. Added `requires_judicial_confirmation` flag for inferred pairs.
    3. Added basic date-check scaffolding for temporal guardrail.
    """

    # Patterns for finding explicit pairs
    EXPLICIT_PATTERNS = [
        r'IPC\s+(\d+[A-Z\-]*)\s*(?:\(|,|;|\.)\s*(?:now\s+)?(?:BNS|Bharatiya Nyaya Sanhita)\s+(\d+[A-Z\-]*)',
        r'Section\s+(\d+[A-Z\-]*)\s+(?:IPC|Indian Penal Code).{0,100}?Section\s+(\d+[A-Z\-]*)\s+(?:BNS|Bharatiya Nyaya Sanhita)',
        r'BNS\s+(\d+[A-Z\-]*)\s*(?:\(|,|;|\.)\s*(?:earlier|formerly|previously)\s+(?:IPC|Indian Penal Code)\s+(\d+[A-Z\-]*)',
    ]
    # Pattern for finding standalone IPC sections
    IPC_ONLY_PATTERN = r'(?:IPC|Indian Penal Code|Penal Code)\s+(\d+[A-Z\-]*)'

    def extract(self, text: str, judgment_date: str = None) -> list:
        """
        Extract transitions with safety flags.
        :param judgment_date: YYYY-MM-DD format. If before 2024-07-01, inferences are suppressed.
        """
        transitions = []
        text_lower = text.lower()

        # --- TEMPORAL GUARDRAIL ---
        # Check if this is a pre-BNS judgment
        is_pre_bns = False
        if judgment_date:
            try:
                jd = datetime.strptime(judgment_date, "%Y-%m-%d")
                if jd < datetime(2024, 7, 1):
                    is_pre_bns = True
            except ValueError:
                pass  # Keep default if date parsing fails

        # --- 1. EXPLICIT PAIRS (High Value) ---
        for pattern in self.EXPLICIT_PATTERNS:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                ipc, bns = match.group(1), match.group(2)
                official = IPCBNSTransitionDB.get(ipc)

                transition = {
                    "ipc": ipc,
                    "bns": bns,
                    "source": "explicit_pair",
                    "validated": bool(official and official["bns"] == bns),
                    "risk": official.get("risk", "unknown") if official else "unknown",
                    "confidence": "high",  # Explicit mention is high confidence
                    "context_snippet": match.group(0)[:150]  # For audit
                }
                # Add warning if pre-BNS but mentions BNS (rare but possible)
                if is_pre_bns:
                    transition["temporal_note"] = "BNS mentioned in pre-enactment judgment. Verify applicability."
                transitions.append(transition)

        # --- 2. INFERRED PAIRS (LOW CONFIDENCE, NOT VALIDATED) ---
        # Only infer if judgment is POST-BNS enactment
        if not is_pre_bns:
            ipc_sections = set(re.findall(self.IPC_ONLY_PATTERN, text_lower, re.IGNORECASE))
            for ipc in ipc_sections:
                official = IPCBNSTransitionDB.get(ipc)
                if official:
                    transitions.append({
                        "ipc": ipc,
                        "bns": official["bns"],
                        "source": "inferred_from_ipc_only",
                        "validated": False,  # CRITICAL FIX: Changed from True
                        "risk": official["risk"],
                        "confidence": "low",  # CRITICAL FIX: Changed from 'medium'
                        "requires_judicial_confirmation": True,  # NEW SAFETY FLAG
                        "note": f"Inferred from standalone IPC {ipc} mention. Not validated by text."
                    })
        else:
            # Pre-BNS judgment: only collect IPC sections as background, no inference
            ipc_sections = set(re.findall(self.IPC_ONLY_PATTERN, text_lower, re.IGNORECASE))
            for ipc in ipc_sections:
                transitions.append({
                    "ipc": ipc,
                    "bns": None,
                    "source": "pre_bns_background_only",
                    "validated": False,
                    "risk": "none",
                    "confidence": "low",
                    "note": "Pre-BNS judgment. IPC section recorded as background only."
                })

        # --- 3. DEDUPLICATE & RETURN ---
        seen = set()
        unique_transitions = []
        for t in transitions:
            key = (t["ipc"], t.get("bns"))
            if key not in seen:
                seen.add(key)
                unique_transitions.append(t)
        return unique_transitions