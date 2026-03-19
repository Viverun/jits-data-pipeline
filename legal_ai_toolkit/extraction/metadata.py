#metadata.py
import re
from datetime import datetime

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

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d %B, %Y",
    "%d %B %Y",
    "%d %b, %Y",
    "%d %b %Y",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%d.%m.%y",
    "%B %d, %Y",
    "%b %d, %Y",
)

HEADER_LINE_SCAN_LIMIT = 40
MAX_COURT_LINE_LENGTH = 160

COURT_RULES = [
    ("central administrative tribunal", "Central Administrative Tribunal", "TR"),
    ("state administrative tribunal", "State Administrative Tribunal", "TR"),
    ("consumer disputes redressal commission", "Consumer Disputes Redressal Commission", "TR"),
    ("arbitration tribunal", "Arbitration Tribunal", "TR"),
    ("armed forces tribunal", "Armed Forces Tribunal", "TR"),
    ("national green tribunal", "National Green Tribunal", "TR"),
    ("industrial court", "Industrial Court", "TR"),
    ("labour court", "Labour Court", "TR"),
    ("family court", "Family Court", "TR"),
    ("district court", "District Court", "TR"),
    ("sessions court", "Sessions Court", "TR"),
    ("supreme court", "Supreme Court Of India", "SC"),
    ("allahabad", "Allahabad High Court", "HC"),
    ("bombay", "Bombay High Court", "HC"),
    ("delhi", "Delhi High Court", "HC"),
    ("madras", "Madras High Court", "HC"),
    ("calcutta", "Calcutta High Court", "HC"),
    ("kerala", "Kerala High Court", "HC"),
    ("karnataka", "Karnataka High Court", "HC"),
    ("karnatka", "Karnataka High Court", "HC"),
    ("gujarat", "Gujarat High Court", "HC"),
    ("rajasthan", "Rajasthan High Court", "HC"),
    ("patna", "Patna High Court", "HC"),
    ("andhra pradesh", "Andhra Pradesh High Court", "HC"),
    ("telangana", "Telangana High Court", "HC"),
    ("punjab and haryana", "Punjab And Haryana High Court", "HC"),
    ("himachal pradesh", "Himachal Pradesh High Court", "HC"),
    ("madhya pradesh", "Madhya Pradesh High Court", "HC"),
    ("orissa", "Orissa High Court", "HC"),
    ("odisha", "Orissa High Court", "HC"),
    ("gauhati", "Gauhati High Court", "HC"),
    ("assam", "Assam High Court", "HC"),
    ("jharkhand", "Jharkhand High Court", "HC"),
    ("chhattisgarh", "Chhattisgarh High Court", "HC"),
    ("uttarakhand", "Uttarakhand High Court", "HC"),
    ("jammu", "Jammu And Kashmir High Court", "HC"),
    ("kashmir", "Jammu And Kashmir High Court", "HC"),
    ("meghalaya", "Meghalaya High Court", "HC"),
    ("manipur", "Manipur High Court", "HC"),
    ("tripura", "Tripura High Court", "HC"),
    ("sikkim", "Sikkim High Court", "HC"),
]


def _clean_header_line(line: str) -> str:
    cleaned = re.sub(r"\s+", " ", line).strip()
    cleaned = cleaned.lstrip("*+%#:-. ")
    return cleaned


def _iter_court_candidates(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]
    cleaned_lines = cleaned_lines[:HEADER_LINE_SCAN_LIMIT]

    for idx, line in enumerate(cleaned_lines):
        if len(line) <= MAX_COURT_LINE_LENGTH:
            yield line

        if idx + 1 < len(cleaned_lines):
            combined = f"{line} {cleaned_lines[idx + 1]}"
            if len(combined) <= MAX_COURT_LINE_LENGTH:
                yield combined


def extract_court_metadata(lines):
    for candidate in _iter_court_candidates(lines):
        normalized = re.sub(r"[^A-Za-z0-9\s]+", " ", candidate).lower()
        normalized = re.sub(r"\s+", " ", normalized).strip()

        if not any(token in normalized for token in ("court", "tribunal", "commission")):
            continue

        for keyword, court_name, court_level in COURT_RULES:
            if keyword in normalized:
                return court_name, court_level

    return "UNKNOWN", "UNKNOWN"


def extract_case_number(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]
    patterns = [
        r"^(?:\d+\s*)?(?:O\.?A\.?|M\.?A\.?|LPA|SLP|FAO|RFA|RSA|MCRC|BLAPL|CRL\.?\s*M\.?C\.?|CRL\.?\s*A\.?|W\.?P\.?\s*\([A-Z.]*\)|W\.?P\.?|C\.?W\.?P\.?|ARB\.?\s*P\.?|ARB\.?\s*CASE)\b.*$",
        r"^(?:\d+\s*)?(?:CRIMINAL|CIVIL|WRIT|APPEAL|REVISION)[^\n]{0,80}\bNO\.?\s*[A-Z0-9/(). -]+$",
        r"^CASE\s+NO\.?\s*[A-Z0-9/(). -]+$",
    ]

    for line in cleaned_lines[:25]:
        if len(line) > 160:
            continue
        for pattern in patterns:
            if re.search(pattern, line, re.I):
                return line

    return "UNKNOWN"


def extract_parties(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]

    for line in cleaned_lines[:20]:
        if len(line) > 180:
            continue
        match = re.search(r"^(.+?)\s+(?:v(?:s)?\.?|versus)\s+(.+?)(?:\s+on\b|$)", line, re.I)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    petitioner = None
    respondent = None
    for line in cleaned_lines[:30]:
        if len(line) > 180:
            continue
        pet_match = re.search(r"^(?:Petitioner|Appellant)\s*[:\-]\s*(.+)$", line, re.I)
        if pet_match and not petitioner:
            petitioner = pet_match.group(1).strip()

        resp_match = re.search(r"^Respondent\s*[:\-]\s*(.+)$", line, re.I)
        if resp_match and not respondent:
            respondent = resp_match.group(1).strip()

    return petitioner, respondent


def extract_bench(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]

    for line in cleaned_lines[:20]:
        if len(line) > 180:
            continue

        coram_match = re.search(r"^(?:CORAM|BEFORE|BENCH)\s*[:\-]+\s*(.+)$", line, re.I)
        if coram_match and coram_match.group(1).strip():
            return coram_match.group(1).strip()

    honble_lines = []
    for line in cleaned_lines[:20]:
        if "HON'BLE" in line.upper() and len(line) <= 180:
            honble_lines.append(line)

    if honble_lines:
        return " | ".join(honble_lines[:3])

    return None


def normalize_decision_date(raw_date: str) -> str:
    """Normalize extracted decision dates to ISO format when possible."""
    if not raw_date:
        return "UNKNOWN"

    cleaned = raw_date.strip()
    if not cleaned or cleaned.upper() == "UNKNOWN":
        return "UNKNOWN"

    cleaned = re.sub(r'(\d)(st|nd|rd|th)\b', r'\1', cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,")
    normalized_candidates = [cleaned, cleaned.title()]

    for candidate in normalized_candidates:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

    return cleaned

def extract_header_metadata(text: str):
    lines = text.split("\n")[:100]
    header = "\n".join(lines[:HEADER_LINE_SCAN_LIMIT])

    metadata = {
        "court": "UNKNOWN",
        "court_level": "UNKNOWN",
        "case_number": "UNKNOWN",
        "decision_date": "UNKNOWN",
        "jurisdiction": "India"
    }

    metadata["court"], metadata["court_level"] = extract_court_metadata(lines)

    # Extract case number
    metadata["case_number"] = extract_case_number(lines)

    # Extract decision date
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, header, re.I)
        if match:
            metadata["decision_date"] = normalize_decision_date(match.group(1))
            break

    petitioner, respondent = extract_parties(lines)
    if petitioner:
        metadata["petitioner"] = petitioner
    if respondent:
        metadata["respondent"] = respondent

    bench = extract_bench(lines)
    if bench:
        metadata["bench"] = bench

    return metadata
