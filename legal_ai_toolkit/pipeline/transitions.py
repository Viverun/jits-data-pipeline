import re
from .runner import BaseStep
from legal_ai_toolkit.utils.mappings import IPCBNSTransitionDB
from legal_ai_toolkit.utils.section_extraction import extract_legal_sections_v2

# v0.2.4: Aggressive noise filter for years and common procedural numbers
NOISE_SECTIONS = {
    "1860", "1872", "1973", "2023", "2024", "2019", "1959", "1961", "1983", "1984", "1993", "1994", "1996", "1999", "2001", "2003", "2008", "2012", "2013", "2014", "2016", "2018", "2022",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
}

IPC_PATTERN = re.compile(
    r'(?:section|sections|u/s|under section)\s+([\dA-Z,\s]+)',
    re.IGNORECASE
)

def extract_ipc_sections(text):
    found = set()
    for match in IPC_PATTERN.finditer(text):
        parts = match.group(1)
        for sec in re.split(r"[,\s]+", parts):
            sec = sec.strip().upper()
            if sec and sec[0].isdigit() and sec not in NOISE_SECTIONS:
                if not (len(sec) == 4 and sec.startswith(("19", "20"))):
                    found.add(f"IPC {sec}")
    return sorted(found)

class TransitionStep(BaseStep):
    def process_item(self, data):
        classification = data.get("classification", {})
        domain = classification.get("domain")

        if domain not in {"criminal", "mixed", "service"}: # Added service as PC Act is common there
            return data

        text = data.get("text", "")
        extracted = extract_legal_sections_v2(text)

        ipc_sections = extracted['ipc']

        # We still store extracted sections for other acts in the data
        data["extracted_sections"] = {
            "crpc": extracted['crpc'],
            "iea": extracted['iea'],
            "pc_act": extracted['pc_act'],
            "ni_act": extracted['ni_act']
        }

        mapped = []
        unmapped = []

        for ipc in ipc_sections:
            transition = IPCBNSTransitionDB.get(ipc)

            if transition:
                if "bns" in transition:
                    mapped.append({
                        "ipc": f"IPC {ipc}",
                        "bns": f"BNS {transition['bns']}",
                        "change_type": transition['type'],
                        "risk": transition['risk'],
                        "offense": transition['offense']
                    })
                else:
                    unmapped.append(f"IPC {ipc}")
            else:
                unmapped.append(f"IPC {ipc}")

        data["statutory_transitions"] = {
            "mapped": mapped,
            "unmapped_ipc": unmapped,
            "summary": {
                "total_ipc_found": len(ipc_sections),
                "mapped_count": len(mapped),
                "unmapped_count": len(unmapped)
            }
        }

        return data
