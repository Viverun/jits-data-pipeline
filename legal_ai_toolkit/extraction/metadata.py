import re
from .runner import BaseStep

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
    r"IN THE ([A-Z ]+) HIGH COURT"
]

DATE_PATTERNS = [
    r"on\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"Date of Decision[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Decided on[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"Dated[:\s]+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
    r"([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"([A-Z]+\s+[0-9]{1,2},\s+[0-9]{4})"
]

CASE_NO_PATTERNS = [
    r"(Criminal|Civil|Writ|Appeal|Revision|Arb\. Case|LPA|SLP)[^\n]{0,40}No\.?\s*[0-9/ -]+",
    r"Case No\.?\s*[0-9/ -]+",
    r"([A-Z]+\s+APPEAL\s+NO\.\s+[0-9/ -]+)"
]

def extract_header_metadata(text: str):
    lines = text.split("\n")[:50]
    header = " ".join(lines).upper()

    metadata = {
        "court": None,
        "court_level": None,
        "case_number": None,
        "decision_date": None,
        "jurisdiction": "India"
    }

    for pattern in COURT_PATTERNS:
        match = re.search(pattern, header)
        if match:
            metadata["court"] = match.group(0).strip().title()
            if "SUPREME" in metadata["court"].upper():
                metadata["court_level"] = "SC"
            elif "HIGH" in metadata["court"].upper():
                metadata["court_level"] = "HC"
            else:
                metadata["court_level"] = "DISTRICT"
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

