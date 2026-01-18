#metadata.py
import re

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

# Enhanced patterns for parties and bench
PETITIONER_RESPONDENT_PATTERNS = [
    r'([A-Z][A-Za-z\s.&,]+?)\s+(?:v[s]?\.?|versus)\s+([A-Z][A-Za-z\s.&,]+?)(?:\s+CASE|$|\n)',
    r'Petitioner\s*[:\-]\s*([A-Z][A-Za-z\s.&,]+)',
    r'Appellant\s*[:\-]\s*([A-Z][A-Za-z\s.&,]+)',
]

RESPONDENT_PATTERNS = [
    r'Respondent\s*[:\-]\s*([A-Z][A-Za-z\s.&,]+)',
]

BENCH_PATTERNS = [
    r'CORAM\s*:\s*(.+?)(?:\n\n|$)',
    r'BEFORE\s*:\s*(.+?)(?:\n\n|$)',
    r'HON\'BLE\s+(.+?J\.)(?:\n|$)',
    r'BENCH\s*:\s*(.+?)(?:\n\n|$)',
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

    # Extract court
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

    # Extract case number
    for pattern in CASE_NO_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["case_number"] = match.group(0).strip()
            break

    # Extract decision date
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["decision_date"] = match.group(1).strip()
            break

    # Extract petitioner/respondent
    for pattern in PETITIONER_RESPONDENT_PATTERNS:
        match = re.search(pattern, header)
        if match:
            if 'v' in match.group(0).lower() or 'versus' in match.group(0).lower():
                # Pattern with "v." or "versus"
                parts = re.split(r'\s+(?:v[s]?\.?|versus)\s+', match.group(0), flags=re.I)
                if len(parts) >= 2:
                    metadata["petitioner"] = parts[0].strip()
                    metadata["respondent"] = parts[1].strip()
                    break
            else:
                # Pattern with "Petitioner:" or "Appellant:"
                metadata["petitioner"] = match.group(1).strip()

    # If petitioner found but not respondent, try to find respondent separately
    if "petitioner" in metadata and "respondent" not in metadata:
        for pattern in RESPONDENT_PATTERNS:
            match = re.search(pattern, header)
            if match:
                metadata["respondent"] = match.group(1).strip()
                break

    # Extract bench composition
    for pattern in BENCH_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["bench"] = match.group(1).strip()
            break

    return metadata

