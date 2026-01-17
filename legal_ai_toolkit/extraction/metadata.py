import re
from ..pipeline.runner import BaseStep

COURT_PATTERNS = [
    r"SUPREME COURT OF INDIA",
    r"HIGH COURT OF JUDICATURE AT ([A-Z ]+)",
    r"HIGH COURT OF ([A-Z ]+)",
    r"([A-Z ]+) HIGH COURT",
    r"HIGH COURT AT ([A-Z ]+)",
    r"HIGH COURT - ([A-Z ]+)",
    r"IN THE COURT OF ([A-Z ]+)",
    r"DISTRICT COURT",
    r"SESSIONS COURT",
    r"BEFORE THE ([A-Z ]+) HIGH COURT",
    r"IN THE ([A-Z ]+) HIGH COURT",
    r"CENTRAL ADMINISTRATIVE TRIBUNAL",
    r"STATE ADMINISTRATIVE TRIBUNAL",
    r"CONSUMER DISPUTES REDRESSAL COMMISSION",
    r"ARBITRATION TRIBUNAL",
    r"ARMED FORCES TRIBUNAL",
    r"NATIONAL GREEN TRIBUNAL",
    r"INDUSTRIAL COURT",
    r"LABOUR COURT",
    r"FAMILY COURT"
]

DATE_PATTERNS = [
    r"on\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"Date of Decision[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Decided on[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Dated[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"([A-Z]+\s+[0-9]{1,2},\s+[0-9]{4})",
    r"DATED\s*:\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{4})",
    r"PRONOUNCED ON\s*[:\s]*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{4})"
]

CASE_NO_PATTERNS = [
    r"(Criminal|Civil|Writ|Appeal|Revision|Arb\. Case|LPA|SLP|OA|MA)[^\n]{0,40}No\.?\s*[0-9/ -]+",
    r"Case No\.?\s*[0-9/ -]+",
    r"([A-Z]+\s+APPEAL\s+NO\.\s+[0-9/ -]+)",
    r"O\.A\.\s*No\.\s*[0-9/ -]+"
]

def extract_header_metadata(text: str):
    lines = text.split("\n")[:100]  # Increased search range
    header = " ".join(lines).upper()

    metadata = {
        "court": "UNKNOWN",
        "court_level": "UNKNOWN",
        "case_number": "UNKNOWN",
        "decision_date": "UNKNOWN",
        "jurisdiction": "India"
    }

    for pattern in COURT_PATTERNS:
        match = re.search(pattern, header)
        if match:
            metadata["court"] = match.group(0).strip().title()
            court_upper = metadata["court"].upper()
            if "SUPREME" in court_upper:
                metadata["court_level"] = "SC"
            elif "HIGH" in court_upper:
                metadata["court_level"] = "HC"
            elif any(x in court_upper for x in ["TRIBUNAL", "COMMISSION", "COURT"]):
                metadata["court_level"] = "TRIBUNAL/LOWER"
            break

    for pattern in CASE_NO_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["case_number"] = match.group(0).strip()
            break

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["decision_date"] = match.group(1).strip()
            break

    return metadata

