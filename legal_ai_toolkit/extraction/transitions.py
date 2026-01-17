import re
from datetime import datetime
from legal_ai_toolkit.utils.mappings import IPCBNSTransitionDB

class TransitionExtractor:
    """
    Extracts IPC→BNS transition pairs with legal safeguards.
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
        is_pre_bns = False
        if judgment_date:
            try:
                jd = datetime.strptime(judgment_date, "%Y-%m-%d")
                if jd < datetime(2024, 7, 1):
                    is_pre_bns = True
            except ValueError:
                pass

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
                    "confidence": "high",
                    "context_snippet": match.group(0)[:150]
                }
                if is_pre_bns:
                    transition["temporal_note"] = "BNS mentioned in pre-enactment judgment. Verify applicability."
                transitions.append(transition)

        # --- 2. INFERRED PAIRS ---
        if not is_pre_bns:
            ipc_sections = set(re.findall(self.IPC_ONLY_PATTERN, text_lower, re.IGNORECASE))
            for ipc in ipc_sections:
                official = IPCBNSTransitionDB.get(ipc)
                if official and "bns" in official:
                    transitions.append({
                        "ipc": ipc,
                        "bns": official["bns"],
                        "source": "inferred_from_ipc_only",
                        "validated": False,
                        "risk": official["risk"],
                        "confidence": "low",
                        "requires_judicial_confirmation": True,
                        "note": f"Inferred from standalone IPC {ipc} mention. Not validated by text."
                    })
        else:
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
