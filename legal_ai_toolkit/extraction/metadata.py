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

EXPLICIT_DATE_PATTERNS = [
    r"\bSigning Date\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\b(?:Digitally\s+signed\s+by\s+[A-Z .]+\s+Date|Date)\s*[:\-]?\s*((?:19|20)\d{2}[./-][0-9]{1,2}[./-][0-9]{1,2})\b(?![./-]\d)",
    r"\b(?:Date of Decision|Decision Date|Decided on|Pronounced on|Reserved on|Uploaded on|Announced on)\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\b(?:Date of Decision|Decision Date|Decided on|Pronounced on|Reserved on|Uploaded on|Announced on)\s*[:\-]?\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"\bDATE OF JUDGMENT\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\b(?:CAV\s+JUDGMENT|JUDGMENT|ORDER)\s+DATED\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\b(?:vs\.?|versus)\b[^\n]{0,160}\bon\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})",
    r"\bOrder on Board on\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\bOrder made in\b[^\n]{0,120}\b([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\bdt\.?\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\bPatna High Court\s+[A-Z][A-Za-z.() /-]{1,40}\s+No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?(?:\(\d+\))?\s+([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{4})(?:\s+\d+(?:/\d+)?)?\b",
    r"\b([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\s+Index\s*:",
    r"\bDate\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"\bDate\s*[:\-]?\s*([0-9]{1,2}[-/](?:[A-Za-z]{3,9}|[0-9]{1,2})[-/](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"^Order(?:\s+No\.?)?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b",
    r"^Dated\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b",
    r"^Dated\s*:\s*([A-Za-z]+\s+[0-9]{1,2},\s+[0-9]{4})\b",
    r"^Dated(?:\s+on)?\s+this\s+the\s+([0-9]{1,2}(?:st|nd|rd|th|%)?\s+day\s+of\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})\b",
    r"^Dated\s+the\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})\b",
    r"\bon\s+this\s+the\s+([0-9]{1,2}(?:st|nd|rd|th|%)?\s+day\s+of\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})\b",
    r"^((?:19|20)\d{2}\.\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-9]{1,2})\b",
]

FALLBACK_LINE_DATE_PATTERNS = [
    r"^([0-9]{1,2}[./-][0-9]{1,2}[./-](?:[0-9]{4}|[0-9]{2}))\b(?![./-]\d)",
    r"^([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})\b",
    r"^([A-Z]+\s+[0-9]{1,2},\s+[0-9]{4})\b",
]

CASE_NO_PATTERNS = [
    r"\b((?:MAC\.?\s*APPL\.?|W\.?\s*P\.?\s*\(\s*[A-Z]+\s*\)|W\.?\s*P\.?|C\/FA)\s*[0-9]+/[0-9]{4}(?:\s*\([^)]+\))?)",
    r"\b((?:Writ\s+Petition(?:\s*\([A-Za-z.]+\))?|Civil\s+Writ\s+Petition|Criminal\s+Writ\s+Petition)\s+Nos?\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?(?:\s*&\s*BATCH)?)",
    r"\b((?:Writ\s+Petition\s*\(\s*(?:Crl\.?|Civil|Criminal)\s*\)\s*(?:Diary\s+)?No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?))",
    r"\b((?:W\.?\s*P\.?|WP)\s*No\.?\s*[A-Z0-9./()-]+(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\s*\([^)]+\))?)",
    r"\b((?:OMP(?:\s*\([^)]+\))?|A\.?\s*P\.?)\s*No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
    r"\b((?:W\.?\s*P\.?(?:\(\s*[A-Z.]+\s*\))?|W\.?\s*A\.?(?:\(\s*[A-Z.]+\s*\))?|C\.?\s*M\.?\s*A\.?(?:\(\s*[A-Z.]+\s*\))?)\s*Nos?\.?\s*[A-Z0-9./()-]+(?:\s*(?:to|and|&|,)\s*[A-Z0-9./()-]+)+(?:\s+of\s+\d{4}))",
    r"\b((?:W\.?\s*P\.?\s*\(\s*[A-Z.]+\s*\)|W\.?\s*P\s*\([A-Z.]+\)|O\.?\s*P\.?\s*\(\s*[A-Z.]+\s*\))\s*(?:No\.?\s*)?[0-9]+/[0-9]{4}(?:\s*\([^)]+\))?)",
    r"\b((?:Cr\.?\s*M\.?\s*P\.?|M\.?\s*Cr\.?\s*C\.?|MCRC|H\.?\s*C\.?\s*P\.?(?:\([A-Z.]+\))?|HCP(?:\([A-Z.]+\))?|Bail\s*Appl\.?|Bail\s*Application|Cr\.?\s*A\.?|Crl\.?\s*O\.?\s*P\.?(?:\([A-Z.]+\))?)\s*Nos?\.?\s*[A-Z0-9./(), &\[\]-]+(?:\s*(?:to|and|&|,)\s*[A-Z0-9./(), &\[\]-]+)*(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\[[A-Z0-9]+\])?(?:\s*\([^)]+\))?)",
    r"\b((?:C\.?W\.?P\.?|CRLMC|CRL\.?\s*PETN\.?|CRL\.?\s*O\.?\s*P\.?|Crl\.R\.C(?:\(MD\))?|Crl\.R\.P\.?|C\.M\.A\.?|M\.?\s*A\.?|MACP|MAC\s+Petition|MFA|FAO|LPA|SLP|O\.A\.?|A\.S\.|S\.A\.|C\.A\.|CRL\.?\s*A\.?|CRL\.?\s*M\.?\s*C\.?|Arb\.?\s*O\.?\s*P\.?(?:\([^)]+\))?)\s*No\.?\s*[A-Z0-9./()-]+(?:\s*(?:of|/)\s*(?:19|20)\d{2})?(?:\s*\([^)]+\))?)",
    r"\b((?:First\s+Appeal|Second\s+Appeal|Special\s+Civil\s+Application|C\.?\s*Misc\.?|CR\.?\s*WJC)\s*No\.?\s*[A-Z0-9./()-]+(?:\s*(?:to|and|&|,)\s*[A-Z0-9./()-]+)*(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\(\d+\))?)",
    r"\b((?:Civil|Criminal)\s+(?:Writ\s+Petition|Appeal|Revision)\s+No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?(?:\s*\([^)]+\))?)",
    r"\b((?:Case|Claim\s+Case|Petition)\s+No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
]

LINE_CASE_NO_PATTERNS = [
    r"^\s*((?:Case\s*[:\-]+\s*)?(?:[A-Z][A-Z0-9 .()&/-]{2,90})\s+No\.?\s*[-:]?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?(?:\s*\([^)]+\))?)\s*$",
    r"^\s*((?:W\.?\s*P\.?\s*\(\s*[A-Z.]+\s*\)|W\.?\s*P\s*\([A-Z.]+\)|O\.?\s*P\.?\s*\(\s*[A-Z.]+\s*\)|"
    r"C\.?W\.?P\.?|CRLMC|CRL\.?\s*PETN\.?|CRL\.?\s*O\.?\s*P\.?|Crl\.R\.C(?:\(MD\))?|Crl\.R\.P\.?|"
    r"C\.M\.A\.?|M\.?\s*A\.?|MACP|MAC\s+Petition|MAC\.?\s*APPL\.?|MFA|FAO|LPA|SLP|O\.A\.?|A\.S\.|S\.A\.|"
    r"C\.A\.|CRL\.?\s*A\.?|CRL\.?\s*M\.?\s*C\.?|C\/FA|Arb\.?\s*O\.?\s*P\.?(?:\([^)]+\))?)\s*(?:No\.?\s*)?[A-Z0-9./()-]+(?:\s*(?:of|/)\s*(?:19|20)\d{2})?(?:\s*\([^)]+\))?)\s*$",
    # The multi-number tail that used to follow the character class here -
    # (?:\s*(?:to|and|&|,)\s*[A-Z0-9./(), &\[\]-]+)* - was redundant and
    # quadratic-to-exponential: its separators (space, "," and "&", plus the
    # letters of "to"/"and" under IGNORECASE) are all inside the class already,
    # so the same text could be partitioned in exponentially many ways and every
    # one of them was retried whenever the overall match failed. Candidates
    # reach this pattern via _clean_header_line, which collapses runs of
    # whitespace to a single space, so the class covers every separator the
    # group could have matched and dropping it accepts exactly the same lines.
    r"^\s*((?:W\.?\s*P\.?|WP|Cr\.?\s*M\.?\s*P\.?|M\.?\s*Cr\.?\s*C\.?|MCRC|H\.?\s*C\.?\s*P\.?(?:\([A-Z.]+\))?|HCP(?:\([A-Z.]+\))?|Bail\s*Appl\.?|Bail\s*Application|Cr\.?\s*A\.?|Crl\.?\s*O\.?\s*P\.?(?:\([A-Z.]+\))?)\s*Nos?\.?\s*[A-Z0-9./(), &\[\]-]+(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\[[A-Z0-9]+\])?(?:\s*\([^)]+\))?)\s*$",
    r"^\s*((?:First\s+Appeal|Second\s+Appeal|Special\s+Civil\s+Application|C\.?\s*Misc\.?|CR\.?\s*WJC)\s*No\.?\s*[A-Z0-9./()-]+(?:\s*(?:to|and|&|,)\s*[A-Z0-9./()-]+)*(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\(\d+\))?)\s*$",
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
    "%Y/%m/%d",
    "%Y.%m.%d",
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
    "%d-%b-%Y",
    "%d-%B-%Y",
    "%d/%b/%Y",
    "%d/%B/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y %B %d",
    "%Y %b %d",
)

HEADER_LINE_SCAN_LIMIT = 60
HEADER_CHAR_SCAN_LIMIT = 6000
UNKNOWN_HEADER_LINE_SCAN_LIMIT = 180
UNKNOWN_HEADER_CHAR_SCAN_LIMIT = 20000
MAX_COURT_LINE_LENGTH = 160
COURT_CONTEXT_PADDING = 80
MAX_STRUCTURED_COURT_LINE_LENGTH = 600
EMBEDDED_COURT_HEADER_HINTS = (
    "page ",
    "page no",
    "hc-nic",
    "created on",
    "digitally signed",
    "signature not verified",
    "downloaded on",
    "uploaded on",
    "order portal",
    "dhc server",
    "qr code",
    "dt.",
    "main case",
    "proceedings sheet",
    "cav judgment",
)
COURT_SIGNAL_PATTERN = re.compile(
    r"court|tribunal|commission|judicature|khc|phhc|dhc|bhc|mhc|aphc|tshc|mphc|jhc|jhhc|cghc|gahc|uhc|hhc|ker|ohc",
    re.I,
)
NEGATIVE_COURT_REFERENCE_HINTS = (
    "order passed by the high court",
    "judgment passed by the high court",
    "judgment of the high court",
    "order of the high court",
    "direction given by the high court",
    "appeals are lodged against the order passed by the high court",
    "appeal against the order passed by the high court",
    "revision before the high court",
    "order passed by the supreme court",
    "judgment passed by the supreme court",
    "judgment of the supreme court",
    "order of the supreme court",
    "direction given by the supreme court",
    "decision of the supreme court",
    "of the supreme court in",
)
NEUTRAL_CITATION_COURT_RULES = [
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]KHC(?:-[A-Z]+)?[/:]", "Karnataka High Court", "HC", "neutral_citation_khc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]PHHC(?:-[A-Z]+)?[/:]", "Punjab And Haryana High Court", "HC", "neutral_citation_phhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]DHC(?:-[A-Z]+)?[/:]", "Delhi High Court", "HC", "neutral_citation_dhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]MHC(?:-[A-Z]+)?[/:]", "Madras High Court", "HC", "neutral_citation_mhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]BHC(?:-[A-Z]+)?[/:]", "Bombay High Court", "HC", "neutral_citation_bhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]APHC(?:-[A-Z]+)?[/:]", "Andhra Pradesh High Court", "HC", "neutral_citation_aphc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]TSHC(?:-[A-Z]+)?[/:]", "Telangana High Court", "HC", "neutral_citation_tshc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]MPHC(?:-[A-Z]+)?[/:]", "Madhya Pradesh High Court", "HC", "neutral_citation_mphc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]JHC(?:-[A-Z]+)?[/:]", "Jharkhand High Court", "HC", "neutral_citation_jhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]JHHC(?:-[A-Z]+)?[/:]", "Jharkhand High Court", "HC", "neutral_citation_jhhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]CGHC(?:-[A-Z]+)?[/:]", "Chhattisgarh High Court", "HC", "neutral_citation_cghc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]GAHC(?:-[A-Z]+)?[/:]", "Gauhati High Court", "HC", "neutral_citation_gahc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]UHC(?:-[A-Z]+)?[/:]", "Uttarakhand High Court", "HC", "neutral_citation_uhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]HHC(?:-[A-Z]+)?[/:]", "Himachal Pradesh High Court", "HC", "neutral_citation_hhc"),
    (r"\b(?:Neutral Citation Number\s*[:\-]?\s*)?(?:NC\s*:?\s*)?(?:19|20)\d{2}[/:]KER(?:-[A-Z]+)?[/:]", "Kerala High Court", "HC", "neutral_citation_ker"),
    (r"\bNEUTRAL CITATION\s+R/[A-Z.]+/\d+/\d{4}\b", "Gujarat High Court", "HC", "neutral_citation_gujarat_r"),
    (r"\bNEUTRAL CITATION\s+[CR]/[A-Z][A-Z0-9.()/-]+/\d{4}\b", "Gujarat High Court", "HC", "neutral_citation_gujarat_case_tag"),
    (r"\b(?:19|20)\d{2}:RJ-(?:JP|JD):[0-9A-Z-]+\b", "Rajasthan High Court", "HC", "neutral_citation_rajasthan_rj"),
]

COURT_RULES = [
    ("central administrative tribunal", "Central Administrative Tribunal", "TR"),
    ("state administrative tribunal", "State Administrative Tribunal", "TR"),
    ("consumer disputes redressal commission", "Consumer Disputes Redressal Commission", "TR"),
    ("central information commission", "Central Information Commission", "TR"),
    ("arbitration tribunal", "Arbitration Tribunal", "TR"),
    ("armed forces tribunal", "Armed Forces Tribunal", "TR"),
    ("national green tribunal", "National Green Tribunal", "TR"),
    ("industrial court", "Industrial Court", "TR"),
    ("labour court", "Labour Court", "TR"),
    ("family court", "Family Court", "TR"),
    ("district court", "District Court", "TR"),
    ("sessions court", "Sessions Court", "TR"),
    ("supreme court", "Supreme Court Of India", "SC"),
    ("allahabad high court", "Allahabad High Court", "HC"),
    ("bombay high court", "Bombay High Court", "HC"),
    ("delhi high court", "Delhi High Court", "HC"),
    ("madras high court", "Madras High Court", "HC"),
    ("calcutta high court", "Calcutta High Court", "HC"),
    ("kerala high court", "Kerala High Court", "HC"),
    ("karnataka high court", "Karnataka High Court", "HC"),
    ("gujarat high court", "Gujarat High Court", "HC"),
    ("rajasthan high court", "Rajasthan High Court", "HC"),
    ("patna high court", "Patna High Court", "HC"),
    ("andhra pradesh high court", "Andhra Pradesh High Court", "HC"),
    ("telangana high court", "Telangana High Court", "HC"),
    ("punjab and haryana high court", "Punjab And Haryana High Court", "HC"),
    ("himachal pradesh high court", "Himachal Pradesh High Court", "HC"),
    ("madhya pradesh high court", "Madhya Pradesh High Court", "HC"),
    ("orissa high court", "Orissa High Court", "HC"),
    ("odisha high court", "Orissa High Court", "HC"),
    ("gauhati high court", "Gauhati High Court", "HC"),
    ("jharkhand high court", "Jharkhand High Court", "HC"),
    ("chhattisgarh high court", "Chhattisgarh High Court", "HC"),
    ("uttarakhand high court", "Uttarakhand High Court", "HC"),
    ("jammu and kashmir high court", "Jammu And Kashmir High Court", "HC"),
    ("meghalaya high court", "Meghalaya High Court", "HC"),
    ("manipur high court", "Manipur High Court", "HC"),
    ("tripura high court", "Tripura High Court", "HC"),
    ("sikkim high court", "Sikkim High Court", "HC"),
]

HIGH_COURT_LOCATION_RULES = [
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
    ("chandigarh", "Punjab And Haryana High Court", "HC"),
    ("himachal pradesh", "Himachal Pradesh High Court", "HC"),
    ("madhya pradesh", "Madhya Pradesh High Court", "HC"),
    ("orissa", "Orissa High Court", "HC"),
    ("odisha", "Orissa High Court", "HC"),
    ("gauhati", "Gauhati High Court", "HC"),
    ("assam", "Gauhati High Court", "HC"),
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

UNKNOWN_PRIORITY_LINE_PATTERNS = (
    re.compile(r"neutral citation", re.I),
    re.compile(r"\b(?:19|20)\d{2}:RJ-(?:JP|JD):[0-9A-Z-]+\b", re.I),
    re.compile(r"Andhra HC \(Pre-Telangana\)", re.I),
    re.compile(r":::\s*Uploaded on", re.I),
    re.compile(r"http://www\.judis\.nic\.in", re.I),
    re.compile(r"\b(?:CRM-M|CRWP|CRR-\d+)\b", re.I),
    re.compile(r"\bGHTY\b", re.I),
    re.compile(r"Court No\.\s*0?1\s+rpan/", re.I),
    re.compile(r"signature not verified", re.I),
    re.compile(r"signed by:", re.I),
    re.compile(r"Panchal ::: Uploaded on", re.I),
    re.compile(r"district\s*&\s*sessions\s+judge", re.I),
    re.compile(r"(?:additional\s+chief|chief|additional)?\s*metropolitan\s+magistrate", re.I),
    re.compile(r"\bscch-\d+\b", re.I),
    re.compile(r"\b(?:m\.v\.c\.?\s*no\.?|mvc\s+\d+/\d+)\b", re.I),
)

STRUCTURED_TRIAL_COURT_RULES = [
    (
        r"court of\s+district\s*&\s*sessions\s+judge,?\s*(?:patiala\s+house|saket|tis\s+hazari|karkardooma|rohini|dwarka)\s+court.*came up for hearing before the sessions court",
        "Sessions Court",
        "TR",
        "structured_trial_sessions_transfer",
    ),
    (
        r"\b(?:additional\s+chief|chief|additional)?\s*metropolitan\s+magistrate(?:-\d+)?\b.*\b(?:case\s+no\.|c\.c\.\s*no\.|complaint\s+case\s+no\.|ni\s+act|saket\s+courts?|patiala\s+house\s+courts?|new\s+delhi)\b",
        "District Court",
        "TR",
        "structured_trial_magistrate_caption",
    ),
    (
        r"\b(?:m\.v\.c\.?\s*no\.?|mvc\s+\d+/\d+)\b.{0,80}\bscch-\d+\b|\bscch-\d+\b.{0,80}\b(?:m\.v\.c\.?\s*no\.?|mvc\s+\d+/\d+)\b",
        "Motor Accident Claims Tribunal",
        "TR",
        "structured_trial_mact_scch",
    ),
]


def _clean_header_line(line: str) -> str:
    cleaned = re.sub(r"\s+", " ", line).strip()
    cleaned = cleaned.lstrip("*+%#:-. ")
    return cleaned


def _normalize_search_text(text: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9\s]+", " ", text).lower()
    return re.sub(r"\s+", " ", normalized).strip()


def _iter_line_segments(line: str):
    cleaned = _clean_header_line(line)
    if not cleaned:
        return

    seen = set()
    if len(cleaned) <= MAX_COURT_LINE_LENGTH:
        seen.add(cleaned)
        yield cleaned

    for match in COURT_SIGNAL_PATTERN.finditer(cleaned):
        start = max(0, match.start() - COURT_CONTEXT_PADDING)
        end = min(len(cleaned), start + MAX_COURT_LINE_LENGTH)
        segment = cleaned[start:end].strip()
        if segment and segment not in seen:
            seen.add(segment)
            yield segment

    if not seen:
        yield cleaned[:MAX_COURT_LINE_LENGTH].strip()


def _iter_court_candidates(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]
    cleaned_lines = cleaned_lines[:HEADER_LINE_SCAN_LIMIT]
    seen = set()

    for idx, line in enumerate(cleaned_lines):
        for segment in _iter_line_segments(line):
            if segment not in seen:
                seen.add(segment)
                yield segment

        if idx + 1 < len(cleaned_lines):
            combined = f"{line} {cleaned_lines[idx + 1]}"
            for segment in _iter_line_segments(combined):
                if segment not in seen:
                    seen.add(segment)
                    yield segment


def _build_high_court_location_matchers():
    """Compile the location rules once instead of on every candidate segment.

    This runs against every header segment of every judgment - tens of segments
    each - so rebuilding sixty pattern strings per call dominated metadata
    extraction.
    """
    matchers = []
    for keyword, court_name, court_level in HIGH_COURT_LOCATION_RULES:
        location_pattern = re.escape(keyword).replace(r"\ ", r"\s+")
        matchers.append((
            keyword,
            re.compile(rf"\b{location_pattern}\s+high court\b"),
            re.compile(rf"\bhigh court(?: of judicature)?(?: at| of)?\s+{location_pattern}\b"),
            court_name,
            court_level,
        ))
    return matchers


HIGH_COURT_LOCATION_MATCHERS = _build_high_court_location_matchers()


def _match_high_court_location_rule(normalized_text: str):
    if "high court" not in normalized_text:
        return None

    for keyword, before_re, after_re, court_name, court_level in HIGH_COURT_LOCATION_MATCHERS:
        # Both patterns require the keyword literally, and the search text has
        # already been lowercased and whitespace-collapsed, so a keyword that
        # is not present as a substring cannot match either pattern.
        if keyword not in normalized_text:
            continue
        if before_re.search(normalized_text):
            return court_name, court_level
        if after_re.search(normalized_text):
            return court_name, court_level

    return None


def _looks_like_embedded_court_header_candidate(raw_candidate: str) -> bool:
    lowered = raw_candidate.lower()
    return any(hint in lowered for hint in EMBEDDED_COURT_HEADER_HINTS)


def _has_embedded_high_court_case_caption(normalized_text: str, location_pattern: str) -> bool:
    court_match = re.search(
        rf"\b(?:(?:the\s+)?high court(?: of judicature)?(?: at| of)?\s+{location_pattern}(?:\s+at\s+[a-z]+)?|"
        rf"{location_pattern}\s+high court)\b",
        normalized_text,
    )
    if not court_match:
        return False

    tail_tokens = normalized_text[court_match.end():].split()
    stopwords = {"the", "at", "of", "and", "for", "in", "on"}
    weak_labels = {
        "case",
        "cases",
        "date",
        "dated",
        "decision",
        "judgment",
        "letter",
        "memo",
        "notification",
        "order",
        "portal",
        "server",
    }

    for idx, token in enumerate(tail_tokens[:16]):
        if token not in {"no", "nos"}:
            continue

        label_tokens = [part for part in tail_tokens[:idx] if part not in stopwords]
        if not label_tokens:
            return False

        if all(part in weak_labels for part in label_tokens):
            return False

        return any(re.fullmatch(r"\d{1,7}[a-z]?", part) for part in tail_tokens[idx + 1:idx + 6])

    return False


def _is_structured_court_rule_match(raw_candidate: str, normalized_text: str, matched):
    court_name, court_level = matched
    if court_level not in {"HC", "SC"}:
        return True

    if court_name == "Supreme Court Of India":
        if re.search(r"^(?:in the|before the)?\s*supreme court(?: of india)?\b", normalized_text):
            return True
        return bool(
            re.search(
                r"\bsupreme court of india\b\s+(?:civil|criminal|writ|special leave|review|transfer|curative)\b",
                normalized_text,
            )
        )

    if not court_name.endswith("High Court"):
        return True

    location = _normalize_search_text(court_name[:-len("High Court")].strip())
    if not location:
        return True

    location_pattern = re.escape(location).replace(r"\ ", r"\s+")
    if re.search(
        rf"^(?:\d+\s+)?(?:in the|before the)?\s*(?:the\s+)?(?:{location_pattern}\s+high court|high court(?: of judicature)?(?: at| of)?\s+{location_pattern})\b",
        normalized_text,
    ):
        return True

    if re.search(
        rf"^(?:\d+\s+)?(?:the\s+)?(?:public prosecutor|additional public prosecutor|special public prosecutor|government pleader|registrar(?: general)?|advocate general)\s+high court(?: of judicature)?(?: at| of)?\s+{location_pattern}\b",
        normalized_text,
    ):
        return True

    if re.search(
        rf"\b(?:(?:the\s+)?high court(?: of judicature)?(?: at| of)?\s+{location_pattern}|{location_pattern}\s+high court)\b\s+"
        r"(?:w\.?\s*p\.?|wp\.?|m\.?\s*cr\.?\s*c\.?|mcrc|cr\.?\s*m\.?\s*p\.?|crl\.?\s*o\.?\s*p\.?|"
        r"cr\.?\s*a\.?|bail\s*appl\.?|h\.?\s*c\.?\s*p\.?|hcp(?:\([a-z.]+\))?|case\s+no\.?|cwjc)",
        normalized_text,
    ):
        return True

    return (
        _looks_like_embedded_court_header_candidate(raw_candidate)
        and _has_embedded_high_court_case_caption(normalized_text, location_pattern)
    )


def _match_court_rule(normalized_text: str):
    for keyword, court_name, court_level in COURT_RULES:
        if keyword in normalized_text:
            return court_name, court_level

    matched = _match_high_court_location_rule(normalized_text)
    if matched:
        return matched

    return None


def _match_neutral_citation_court(raw_text: str):
    for pattern, court_name, court_level, reason in NEUTRAL_CITATION_COURT_RULES:
        if re.search(pattern, raw_text, re.I):
            return court_name, court_level, reason
    return None


def _infer_special_high_court(header_text: str):
    lowered = header_text.lower()

    if re.search(r"\bAndhra HC \(Pre-Telangana\)", header_text, re.I):
        return "Andhra Pradesh High Court", "HC", "andhra_pre_telangana"

    bombay_uploader_signature = "::: uploaded on" in lowered and "::: downloaded on" in lowered
    bombay_uploader_case_token = re.search(
        r"\b(?:wp\d+[-.]\d+|wp\s*(?:no\.)?\s*\d+\s+of\s+\d{4}|arbp-\d+(?:[-.]\d+)?|carbpl-\d+(?:[-.]\d+)?|"
        r"cri\.?\s*wp\s+\d+\s+of\s+\d{4}|adms-\d+-\d{4})\b",
        header_text,
        re.I,
    )
    bombay_uploader_file_token = re.search(
        r"\b(?:ppn|ssm|panchal)\b[^\n]{0,80}\.(?:doc|docx|odt|sxw)\b|\b(?:wp|arbp|carbpl|cri\.?\s*wp)\b[^\n]{0,80}\.(?:doc|docx|odt|sxw)\b",
        header_text,
        re.I,
    )

    if (
        bombay_uploader_signature
        and (
            re.search(r"\b(?:wp\d+-\d{4}|adms-\d+-\d{4}|final\.doc)\b", header_text, re.I)
            or bombay_uploader_case_token
            or bombay_uploader_file_token
        )
    ):
        return "Bombay High Court", "HC", "bombay_colon_uploader"

    if (
        re.search(r"(?:http://www\.)?judis\.nic\.in", header_text, re.I)
        and re.search(
            r"\b(?:This Criminal Revision(?: Case)?|Civil Miscellaneous Appeal|These Civil Miscellaneous Appeals|"
            r"The present Civil Miscellaneous Appeal|C\.M\.A\.Nos?\.|Crl\.R\.C(?:\(MD\))?Nos?\.|W\.P\.Nos?\.|"
            r"W\.A\.Nos?\.|Crl\.O\.P\.Nos?\.|Crl\.R\.P\.Nos?\.|S\.A\.No\.|A\.S\.No\.)",
            header_text,
            re.I,
        )
    ):
        return "Madras High Court", "HC", "madras_judis_portal"

    if re.search(r"\b(?:location\s*:\s*)?ohc,\s*cuttack\b", header_text, re.I) or re.search(r"\bABLAPL\b", header_text, re.I):
        return "Orissa High Court", "HC", "orissa_ohc_cuttack"

    if re.search(r"\bmhc\.tn\.gov\.in/judis\b", header_text, re.I):
        return "Madras High Court", "HC", "madras_mhc_portal"

    if re.search(r"\b(?:CRM-M|CRWP|CRR-\d+)\b", header_text, re.I):
        return "Punjab And Haryana High Court", "HC", "punjab_haryana_case_type"

    if re.search(r"\bCivil Writ Petition No\.\s*\d+\s+of\s+\d{4}\s*\(O&M\)", header_text, re.I):
        return "Punjab And Haryana High Court", "HC", "punjab_haryana_om_caption"

    if re.search(r"\bCrl Petn No\.\s*\d+\s+of\s+\d{4}\b", header_text, re.I) and re.search(r"\bShillong\b", header_text, re.I):
        return "Meghalaya High Court", "HC", "meghalaya_shillong_petition"

    if (
        "signature not verified" in lowered
        and "signed by:" in lowered
        and (
            re.search(r"W\.?\s*P\.?\s*\(\s*(?:C|CRL)\s*\)", header_text, re.I)
            or re.search(r"\bCRL\.?\s*M\.?C\.?\b", header_text, re.I)
            or re.search(r"\bCRL\.?\s*A\.?\b", header_text, re.I)
            or re.search(r"\bLPA\b", header_text, re.I)
        )
        and "supreme court" not in lowered
    ):
        return "Delhi High Court", "HC", "delhi_signature_bundle"

    if re.search(r"\bDelhi High Court Order Portal\b", header_text, re.I) and re.search(r"\bDHC Server\b", header_text, re.I):
        return "Delhi High Court", "HC", "delhi_order_portal"

    if (
        "::: downloaded on" in lowered
        and ":::cis" in lowered
        and (
            re.search(r"\bstate of h\.p\b", header_text, re.I)
            or re.search(r"\bCWP\s+No\.", header_text, re.I)
            or re.search(r"\bCMP\s+No\.", header_text, re.I)
        )
    ):
        return "Himachal Pradesh High Court", "HC", "himachal_cis_bundle"

    if re.search(r"^Court No\.\s*0?1\s+rpan/\d+\s+CRM\s*\(A\)\s*\d+\s+of\s+\d{4}", header_text, re.I | re.M):
        return "Calcutta High Court", "HC", "calcutta_rpan_court_no"

    if re.search(r"\bLocation\s*:\s*(?:HIGH COURT OF ORISSA|ORISSA HIGH COURT),\s*CUTTACK\b", header_text, re.I):
        return "Orissa High Court", "HC", "orissa_signed_location"

    if re.search(r"\bTapabrata Chakraborty,\s*J\.", header_text, re.I):
        return "Calcutta High Court", "HC", "calcutta_tapabrata_judge"

    if re.search(r"\(Soumen Sen,\s*J\.\)\s*\(Uday Kumar,\s*J\.\)", header_text, re.I):
        return "Calcutta High Court", "HC", "calcutta_soumen_uday_bench"

    if (
        re.search(r"All parties shall act on the server cop(?:y|ies) of this order", header_text, re.I)
        and (
            re.search(r"\bCRM\s*\(A\)\b", header_text, re.I)
            or re.search(r"\bTapabrata Chakraborty,\s*J\.", header_text, re.I)
            or re.search(r"\bSoumen Sen,\s*J\.", header_text, re.I)
        )
    ):
        return "Calcutta High Court", "HC", "calcutta_server_copy"

    if re.search(r"\bDistrict Magistrate,\s*Srinagar\b", header_text, re.I) or re.search(
        r"\b(?:J&K|Jammu\s*&\s*Kashmir)\s+High Court\b", header_text, re.I
    ):
        return "Jammu And Kashmir High Court", "HC", "jk_srinagar_context"

    if re.search(r"\bCrl\.R\.PNO\.\d+\s+of\s+\d{4}\b", header_text, re.I) and re.search(r"\bAluva\b", header_text, re.I):
        return "Kerala High Court", "HC", "kerala_crlrp_aluva"

    if re.search(r"\bBEFORE THE HON'?BLE MR\.JUSTICE UB SAHA\b", header_text, re.I):
        return "Gauhati High Court", "HC", "gauhati_ub_saha"

    if re.search(r"\bGHTY\b", header_text, re.I):
        return "Gauhati High Court", "HC", "gauhati_ghty"

    if re.search(r"Additional Public Prosecutor,\s*Assam for the State", header_text, re.I):
        return "Gauhati High Court", "HC", "gauhati_assam_app"

    if re.search(r"Page No\.#\s*\d+/\d+", header_text, re.I) and re.search(r"\b(?:Assam|Nagaon)\b", header_text, re.I):
        return "Gauhati High Court", "HC", "gauhati_page_no_assam"

    if re.search(r"Per the Hon'?ble Sri Justice A\.Abhishek Reddy", header_text, re.I):
        return "Telangana High Court", "HC", "telangana_abhishek_reddy"

    # Bombay High Court orders often retain this uploader stamp even when the caption is stripped.
    if (
        re.search(r"Per,\s*Shree Chandrashekhar,\s*CJ\s*:", header_text, re.I)
        and re.search(r"Panchal ::: Uploaded on", header_text, re.I)
        and re.search(r"(?:Writ Petition(?: \(Stamp\))? No\.|WP-\d+-\d{4})", header_text, re.I)
    ):
        return "Bombay High Court", "HC", "bombay_panchal_uploader"

    if re.search(r"\bW\.P\.\(C\)\s*\d+/\d{4}\b", header_text, re.I) and (
        re.search(r"\bRAJIV\s+SAHAI\s+ENDLAW\b", header_text, re.I)
        or re.search(r"\bA\.K\.\s*SIKRI\b", header_text, re.I)
    ):
        return "Delhi High Court", "HC", "delhi_wp_c_bench"

    if re.search(r"\bHIGH COURT OF ANDHRA PRADESH\s*:\s*AMARAVATI\b", header_text, re.I) and re.search(
        r"\bMAIN CASE\b",
        header_text,
        re.I,
    ):
        return "Andhra Pradesh High Court", "HC", "andhra_amaravati_main_case"

    return None


def _iter_unknown_priority_candidates(lines):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]
    if not cleaned_lines:
        return []

    candidates = []
    seen = set()
    bounded_lines = cleaned_lines[:UNKNOWN_HEADER_LINE_SCAN_LIMIT]

    for idx, line in enumerate(bounded_lines):
        segments = [line]
        if idx + 1 < len(bounded_lines):
            segments.append(f"{line} {bounded_lines[idx + 1]}")

        for segment in segments:
            if not segment or segment in seen or len(segment) > MAX_STRUCTURED_COURT_LINE_LENGTH:
                continue
            if any(pattern.search(segment) for pattern in UNKNOWN_PRIORITY_LINE_PATTERNS):
                seen.add(segment)
                candidates.append(segment)

    return candidates


def _match_structured_trial_court(lines):
    for candidate in _iter_unknown_priority_candidates(lines):
        for pattern, court_name, court_level, reason in STRUCTURED_TRIAL_COURT_RULES:
            if re.search(pattern, candidate, re.I):
                return court_name, court_level, reason
    return None


def _match_embedded_sessions_transfer(candidate: str):
    pattern, court_name, court_level, reason = STRUCTURED_TRIAL_COURT_RULES[0]
    if re.search(pattern, candidate, re.I):
        return court_name, court_level, reason
    return None


def _infer_trial_court_from_context(header_text: str):
    if not header_text:
        return None

    narrative_pattern = re.compile(
        r"\b(?:filed\s+(?:with|before)|pending\s+before|passed\s+by|challenged|approached|seeking|stay|quashing|"
        r"order\s+dated|judgment\s+dated|respondent|petitioner|appellant|learned\s+counsel|complaint\s+filed)\b",
        re.I,
    )
    structured_reference_pattern = re.compile(
        r"\b(?:case\s+no\.|court\s+no\.|c\.c\.\s*no\.|complaint\s+case\s+no\.|ni\s+act|courts\b|new\s+delhi|"
        r"court\s+of|judge\b|suit\s+no\.|m\.v\.c\.|mvc\b)\b",
        re.I,
    )

    cleaned_lines = [_clean_header_line(line) for line in header_text.splitlines() if line.strip()]
    for idx, line in enumerate(cleaned_lines[:40]):
        candidates = [line]
        if idx + 1 < len(cleaned_lines):
            candidates.append(f"{line} {cleaned_lines[idx + 1]}")

        for candidate in candidates:
            if len(candidate) > 320:
                continue

            lowered = candidate.lower()
            is_narrative = bool(narrative_pattern.search(candidate))
            has_structured_reference = bool(structured_reference_pattern.search(candidate))

            if re.search(r"\bdistrict\s*&\s*sessions\s+judge\b", candidate, re.I):
                if not is_narrative or "court of" in lowered:
                    return "Sessions Court", "TR"

            if re.search(r"\b(?:assistant|principal|additional)\s+sessions\s+judge\b", candidate, re.I):
                if not is_narrative or has_structured_reference:
                    return "Sessions Court", "TR"

            if re.search(r"\b(?:[IVXL]+|\d+|[A-Z])\s*Addl\.?\s*City\s+Civil\s*&\s*Sessions\s+Judge\b", candidate, re.I):
                if not is_narrative or "pronounced by me in the open court" in lowered:
                    return "Sessions Court", "TR"

            if re.search(r"\b(?:acmm|cmm|cj\s*m|cjmf|jmfc|metropolitan\s+magistrate)\b", candidate, re.I):
                if not is_narrative and has_structured_reference:
                    return "District Court", "TR"

            if re.search(r"\b(?:patiala\s+house|saket|tis\s+hazari|karkardooma|rohini|dwarka)\s+court\b", candidate, re.I):
                if ("court of" in lowered or "magistrate" in lowered or "judge" in lowered) and not is_narrative:
                    return "District Court", "TR"

    return None


def _is_negative_court_reference(normalized_text: str) -> bool:
    return any(hint in normalized_text for hint in NEGATIVE_COURT_REFERENCE_HINTS)


def _looks_like_judge_line(line: str) -> bool:
    return bool(re.match(r"^[A-Z][A-Za-z .,&'()[\]-]{2,100},\s*(?:J\.?|JJ\.?|C\.J\.?|CJI\.?)$", line))


def _infer_supreme_court(lines, header_text: str):
    normalized_header = _normalize_search_text(header_text)
    if not normalized_header:
        return None

    leading_lines = [_clean_header_line(line) for line in lines if line.strip()][:5]
    leading_caption = " ".join(_clean_header_line(line) for line in lines[:8] if line.strip())
    normalized_caption = _normalize_search_text(leading_caption)
    caption_head = normalized_caption[:400]
    leading_text = header_text[:2000]
    normalized_leading = _normalize_search_text(leading_text)

    if re.search(r"\b(?:supreme court of india|in the supreme court)\b", leading_text, re.I):
        return "Supreme Court Of India", "SC"

    if "original jurisdiction" in caption_head or "article 32" in caption_head:
        return "Supreme Court Of India", "SC"

    first_line = next((_clean_header_line(line) for line in lines if line.strip()), "")
    leading_excerpt = normalized_leading[:600]
    deeper_leading_excerpt = normalized_leading[:2500]

    if "chief justice of india" in normalized_header:
        return "Supreme Court Of India", "SC"

    if any(
        re.search(r"^(?:\d+\.?\s*)?special leave granted\b", line, re.I)
        or re.search(r"^(?:\d+\.?\s*)?leave granted\b", line, re.I)
        for line in leading_lines
    ):
        return "Supreme Court Of India", "SC"

    appeal_signal = re.search(
        r"\b(?:civil|criminal)\s+appeal(?:s)?\b|\b(?:special leave|transfer|review|curative)\s+petition\b|"
        r"\bC\.A\.?\s*No\.?\s*\d+/\d{4}\b|\bSLP\s*\([A-Z]\)\s*No\.?\s*\d+/\d{4}\b",
        deeper_leading_excerpt,
    )
    challenge_signal = re.search(
        r"\b(?:appeals?\s+are\s+lodged\s+against|challenge(?:d|ing)?\s+the\s+order\s+passed\s+by\s+the\s+high\s+court)\b",
        deeper_leading_excerpt,
    )
    if re.search(r"\bC\.A\.?\s*No\.?\s*\d+/\d{4}\s*@\s*SLP\([A-Z]\)\s*No\.?\s*\d+/\d{4}\b", leading_text, re.I):
        return "Supreme Court Of India", "SC"

    if re.search(r"^[A-Z][A-Za-z .()[\]-]{2,120},\s*CJI\.?\b", first_line, re.I):
        return "Supreme Court Of India", "SC"

    if re.search(r"^[A-Z][A-Za-z .()[\]-]{2,120},\s*J\.?\s*\d*\s*Leave granted\b", first_line, re.I):
        return "Supreme Court Of India", "SC"

    if (
        re.search(r"Writ Petition\s*\(Crl\.?\)\s*(?:Diary\s+)?No\.?\s*\d+\s+of\s+\d{4}", leading_text, re.I)
        and re.search(r"Signature Not Verified\s+Digitally signed by\s+CHETAN KUMAR", leading_text, re.I)
    ):
        return "Supreme Court Of India", "SC"

    if appeal_signal and ("high court" not in normalized_leading and "tribunal" not in normalized_leading):
        return "Supreme Court Of India", "SC"

    if _looks_like_judge_line(first_line) and "leave granted" in leading_excerpt:
        return "Supreme Court Of India", "SC"

    if _looks_like_judge_line(first_line) and (appeal_signal or challenge_signal):
        return "Supreme Court Of India", "SC"

    return None


def extract_court_metadata(lines, header_text=""):
    for candidate in _iter_unknown_priority_candidates(lines):
        embedded_trial_match = _match_embedded_sessions_transfer(candidate)
        if embedded_trial_match:
            return embedded_trial_match

    priority_text = ""
    for candidate in _iter_court_candidates(lines):
        matched = _match_neutral_citation_court(candidate)
        if matched:
            return matched

    if header_text:
        priority_text = "\n".join(_iter_priority_lines(lines))

        matched = _infer_supreme_court(lines, priority_text or header_text)
        if matched:
            return matched[0], matched[1], "supreme_court_inference"

        if priority_text:
            matched = _match_neutral_citation_court(priority_text)
            if matched:
                return matched

            matched = _infer_special_high_court(priority_text)
            if matched:
                return matched

        matched = _match_neutral_citation_court(header_text[:2000])
        if matched:
            return matched

        matched = _infer_special_high_court(header_text[:2000])
        if matched:
            return matched

    for candidate in _iter_court_candidates(lines):
        normalized = _normalize_search_text(candidate)

        if not any(token in normalized for token in ("court", "tribunal", "commission", "judicature")):
            continue

        if _is_negative_court_reference(normalized):
            continue

        matched = _match_court_rule(normalized)
        if matched and _is_structured_court_rule_match(candidate, normalized, matched):
            return matched[0], matched[1], "court_rule"

    if header_text:
        matched = _infer_trial_court_from_context(header_text[:2500])
        if matched:
            return matched[0], matched[1], "trial_court_context"

    return "UNKNOWN", "UNKNOWN", None


def extract_unknown_court_metadata(lines, header_text=""):
    priority_candidates = _iter_unknown_priority_candidates(lines)
    priority_text = "\n".join(priority_candidates)

    if priority_text:
        matched = _match_neutral_citation_court(priority_text)
        if matched:
            return matched

        matched = _infer_special_high_court(priority_text)
        if matched:
            return matched

    matched = _match_neutral_citation_court(header_text[:4000])
    if matched:
        return matched

    matched = _infer_special_high_court(header_text[:12000])
    if matched:
        return matched

    for candidate in _iter_court_candidates(lines):
        normalized = _normalize_search_text(candidate)

        if not any(token in normalized for token in ("court", "tribunal", "commission", "judicature")):
            continue

        if _is_negative_court_reference(normalized):
            continue

        matched = _match_court_rule(normalized)
        if matched and _is_structured_court_rule_match(candidate, normalized, matched):
            return matched[0], matched[1], "court_rule"

    matched = _match_structured_trial_court(lines)
    if matched:
        return matched

    return "UNKNOWN", "UNKNOWN", None


def _normalize_case_number(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip(" ,.;:")
    normalized = re.sub(r"^\s*in\s+(?=[A-Z])", "", normalized, flags=re.I)
    normalized = re.sub(r"\bPage\s+\d+\s+of\s+\d+\b", "", normalized, flags=re.I)
    normalized = re.sub(r"\bNo\.?\s*-\s*", "No. ", normalized, flags=re.I)
    normalized = re.sub(r"\s*&\s*BATCH\b.*$", "", normalized, flags=re.I)
    normalized = re.sub(r"\s+Between:?$", "", normalized, flags=re.I)
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,.;:")
    return normalized or "UNKNOWN"


def _is_bad_case_number_candidate(value: str) -> bool:
    normalized = _normalize_search_text(value)
    if normalized.startswith(("respondent ", "respondents ", "petitioner ", "petitioners ", "appellant ", "appellants ")):
        return True
    if normalized.startswith(("no ", "no.", "nos ", "nos.")):
        return True
    if re.search(r"\b(?:index|contents)\b", normalized):
        return True
    if "page" in normalized and re.search(r"\b(?:particulars|heading|serial|sr)\b", normalized):
        return True
    return bool(
        re.search(
            r"\b(?:fir|crime|case crime|court|respondent|petitioner|appellant|accused|defendant|plaintiff|"
            r"witness|issue|para|paragraph|page|annexure|exhibit|police station)\s+no\b",
            normalized,
        )
    )


def _extract_neutral_citation_case_tag(text: str):
    match = re.search(r"\bNEUTRAL CITATION\s+([CR]/[A-Z][A-Z0-9.()/-]+/\d{4})\b", text, re.I)
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_patna_embedded_case_tag(text: str):
    match = re.search(
        r"\bPatna High Court\s+((?:[A-Z][A-Za-z.()/-]{0,20}(?:\s+[A-Z][A-Za-z.()/-]{1,20}){0,5})\s+No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?(?:\(\d+\))?)",
        text,
        re.I,
    )
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_karnataka_neutral_citation_case_tag(text: str):
    match = re.search(
        r"\bNC\s*:?\s*(?:19|20)\d{2}:KHC(?:-[A-Z]+)?:\d+\s+((?:[A-Z][A-Za-z.()/-]{0,20}(?:\s+[A-Z][A-Za-z.()/-]{0,20}){0,4})\s+No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
        text,
        re.I,
    )
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_mphc_neutral_citation_case_tag(text: str):
    match = re.search(
        r"\b(?:19|20)\d{2}:MPHC(?:-[A-Z]+)?:\d+\s+(?:\d+\s+)?([A-Z]{1,6}-\d{1,6}-\d{2,4})\b",
        text,
        re.I,
    )
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_bare_header_case_tag(text: str):
    match = re.search(
        r"\b((?:CRM\s*\([A-Z.]+\)|MAT|CRIR|Cr\.?\s*M\.?\s*P\s*\([A-Z.]+\)|FMA|CRR|CRA|RVW|APO|SAT)\s*(?:No\.?\s*)?[A-Z0-9./()-]+(?:\s*(?:to|and|&)\s*[A-Z0-9./()-]+)*\s+of\s+\d{4})\b",
        text,
        re.I,
    )
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_high_court_embedded_case_tag(text: str):
    # Keep this extractor bounded: broad alternations on very long OCR text can backtrack heavily.
    text = text[:2500]
    high_court_pattern = re.compile(
        r"\b(?:(?:the\s+)?high court(?: of judicature)?(?: at| of)?\s+[A-Z][A-Za-z.& ]+(?:\s+at\s+[A-Z][A-Za-z.& ]+)?|"
        r"[A-Z][A-Za-z.& ]+\s+high court)\b",
        re.I,
    )
    cleaned_lines = [_clean_header_line(line) for line in text.splitlines() if line.strip()]

    for idx, line in enumerate(cleaned_lines[:40]):
        candidates = [line]
        if idx + 1 < len(cleaned_lines):
            candidates.append(f"{line} {cleaned_lines[idx + 1]}")

        for candidate in candidates:
            if not _looks_like_embedded_court_header_candidate(candidate):
                continue

            court_match = high_court_pattern.search(candidate)
            if not court_match:
                continue

            tail = candidate[court_match.end():].strip(" :-")
            extracted = _extract_case_number_match(tail)
            if extracted:
                return extracted

    match = re.search(
        r"\b(?:(?:the\s+)?high court(?: of judicature)?(?: at| of)?\s+[A-Z][A-Za-z.& ]+|[A-Z][A-Za-z.& ]+\s+high court)\s+"
        r"((?:CWJC|W\.?\s*P\.?|WP|M\.?\s*Cr\.?\s*C\.?|MCRC|Cr\.?\s*M\.?\s*P\.?|Crl\.?\s*O\.?\s*P\.?(?:\([A-Z.]+\))?|"
        r"Cr\.?\s*A\.?|H\.?\s*C\.?\s*P\.?(?:\([A-Z.]+\))?|HCP(?:\([A-Z.]+\))?)\s*Nos?\.?\s*[A-Z0-9./(), &\[\]-]+"
        r"(?:\s*(?:to|and|&|,)\s*[A-Z0-9./(), &\[\]-]+)*(?:/\d{2,4}|\s+of\s+\d{2,4})(?:\[[A-Z0-9]+\])?)",
        text,
        re.I,
    )
    if match:
        return _normalize_case_number(match.group(1))

    return None


def _extract_bombay_uploader_slug_case_tag(text: str):
    match = re.search(
        r"\b([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{1,6}-\d{2,4})(?:-[A-Z0-9]+)?\.(?:docx?|odt)\b",
        text,
        re.I,
    )
    if not match:
        return None
    return _normalize_case_number(match.group(1))


def _extract_madras_portal_case_tag(text: str):
    portal_patterns = (
        r"\b((?:RC(?:\([A-Z]+\))?|Crl\.?R\.?C(?:\([A-Z]+\))?)\s*No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
        r"\b((?:WA(?:\([A-Z.]+\))?|W\.?A\.?(?:\([A-Z.]+\))?)\s*No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
        r"\b((?:CMA(?:\([A-Z.]+\))?|C\.?M\.?A\.?(?:\([A-Z.]+\))?)\s*Nos?\.?\s*[A-Z0-9./(), -]+(?:\s*(?:and|to)\s*[A-Z0-9./(), -]+)?\s+of\s+\d{4})",
        r"\b((?:Tr\.?\s*C\.?M\.?P\.?)\s*Nos?\.?\s*[A-Z0-9./(), -]+(?:\s*(?:and|to)\s*[A-Z0-9./(), -]+)?\s+of\s+\d{4})",
        r"\b((?:W\.?P\.?(?:\([A-Z.]+\))?)\s*Nos?\.?\s*[A-Z0-9./(), -]+(?:\s+of\s+\d{4})(?:,[A-Z0-9./(), -]+\s+of\s+\d{4})*)",
        r"\b((?:W\.?P\.?(?:\([A-Z.]+\))?|WA(?:\([A-Z.]+\))?|W\.?A\.?(?:\([A-Z.]+\))?|CMA(?:\([A-Z.]+\))?|C\.?M\.?A\.?(?:\([A-Z.]+\))?)\s*No\.?\s*[A-Z0-9./()-]+(?:\s+of\s+\d{4})?)",
    )

    for raw_line in text.splitlines()[:40]:
        if not re.search(r"(?:mhc\.tn\.gov\.in/judis|judis\.nic\.in)", raw_line, re.I):
            continue

        cleaned_line = re.sub(
            r"https?://(?:www\.)?mhc\.tn\.gov\.in/judis/?|http://www\.judis\.nic\.in",
            " ",
            raw_line,
            flags=re.I,
        )
        cleaned_line = re.sub(r"\b\d+\s*/\s*\d+\b", " ", cleaned_line)
        cleaned_line = re.sub(r"\s+", " ", cleaned_line).strip()

        for pattern in portal_patterns:
            match = re.search(pattern, cleaned_line, re.I)
            if match:
                return _normalize_case_number(match.group(1))

    return None


def _extract_special_case_number(text: str):
    text = text[:2500]
    for extractor in (
        _extract_neutral_citation_case_tag,
        _extract_patna_embedded_case_tag,
        _extract_high_court_embedded_case_tag,
        _extract_karnataka_neutral_citation_case_tag,
        _extract_madras_portal_case_tag,
    ):
        extracted = extractor(text)
        if extracted:
            return extracted
    return None


def _extract_case_number_match(text: str, patterns=None):
    patterns = patterns or CASE_NO_PATTERNS
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            prefix = text[max(0, match.start() - 40):match.start()]
            label_match = re.search(r"\b(?:respondents?|petitioners?|appellants?)\b", prefix, re.I)
            if label_match:
                label_tail = prefix[label_match.end():].strip(" :-")
                if not label_tail or re.fullmatch(r"[A-Z0-9.()/-]{1,20}(?:\s+[A-Z0-9.()/-]{1,20}){0,2}", label_tail):
                    continue
            candidate = next((group for group in match.groups() if group), match.group(0))
            if re.match(r"^\s*Case\s+No\.?\s*", candidate, re.I) and re.search(r"\b(?:police station|p\.?\s*s\.?)\b", prefix, re.I):
                continue
            if _is_bad_case_number_candidate(candidate):
                continue
            return _normalize_case_number(candidate)
    return None


def _looks_like_case_number_candidate(text: str) -> bool:
    if not text:
        return False

    lowered = text.lower()
    if len(lowered) > 420:
        return False

    # Fast lexical gate before running expensive regex families.
    if re.search(r"\b(?:no\.?|nos\.?|case|petition|appeal|revision|wp|w\.p\.?|cwp|crl|cr\.?|mcrc|slp|lpa|ma|cma|fao|mfa|misc|oa|op)\b", lowered):
        return True

    return bool(re.search(r"/\d{2,4}\b|\bof\s+(?:19|20)\d{2}\b", lowered))


def extract_case_number(lines, header_text: str = ""):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]

    if header_text:
        special_case = _extract_special_case_number(header_text[:2500])
        if special_case:
            return special_case

    line_candidates = []
    seen = set()
    for line in cleaned_lines[:60]:
        if line and line not in seen and len(line) <= 300:
            seen.add(line)
            line_candidates.append(line)

    for pattern in LINE_CASE_NO_PATTERNS:
        for candidate in line_candidates:
            if re.search(r"^\W*(?:respondents?|petitioners?|appellants?)\b", candidate, re.I):
                continue
            if not _looks_like_case_number_candidate(candidate):
                continue
            extracted = _extract_case_number_match(candidate[:300], patterns=[pattern])
            if extracted:
                return extracted

    for idx, line in enumerate(cleaned_lines[:60]):
        for candidate in (line, f"{line} {cleaned_lines[idx + 1]}" if idx + 1 < len(cleaned_lines) else ""):
            if candidate and candidate not in seen and len(candidate) <= 1200:
                seen.add(candidate)
                line_candidates.append(candidate)

    for pattern in CASE_NO_PATTERNS:
        for candidate in line_candidates:
            if re.search(r"^\W*(?:respondents?|petitioners?|appellants?)\b", candidate, re.I):
                continue
            if not _looks_like_case_number_candidate(candidate):
                continue
            extracted = _extract_case_number_match(candidate[:420], patterns=[pattern])
            if extracted:
                return extracted

    if header_text:
        extracted = _extract_case_number_match(header_text[:900])
        if extracted:
            return extracted

        for fallback_extractor in (
            _extract_mphc_neutral_citation_case_tag,
            _extract_bare_header_case_tag,
            _extract_bombay_uploader_slug_case_tag,
        ):
            extracted = fallback_extractor(header_text[:2500])
            if extracted:
                return extracted

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

    cleaned = re.sub(r"(\d{1,2})%", r"\1", cleaned)
    cleaned = re.sub(r'(\d)(st|nd|rd|th)\b', r'\1', cleaned, flags=re.I)
    cleaned = re.sub(
        r"(\d{1,2})\s+day\s+of\s+([A-Za-z]+),?\s+((?:19|20)\d{2})",
        r"\1 \2 \3",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"\b([0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?)\b.*$", "", cleaned).strip()
    cleaned = re.sub(r"^((?:19|20)\d{2})[.,]\s*(?=[A-Za-z])", r"\1 ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,")
    normalized_candidates = [cleaned, cleaned.title()]

    for candidate in normalized_candidates:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

    return cleaned


def _iter_priority_lines(lines, head_limit: int = 40, tail_limit: int = 20):
    cleaned_lines = [_clean_header_line(line) for line in lines if line.strip()]
    if not cleaned_lines:
        return []

    priority_lines = []
    seen = set()

    for line in cleaned_lines[:head_limit] + cleaned_lines[-tail_limit:]:
        if line and line not in seen:
            seen.add(line)
            priority_lines.append(line)

    return priority_lines


def _extract_first_date(patterns, text: str):
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return next(group for group in match.groups() if group)
    return None


def extract_decision_date(lines, header_text: str, fallback_text: str = "") -> str:
    for line in _iter_priority_lines(lines):
        raw_date = _extract_first_date(EXPLICIT_DATE_PATTERNS, line)
        if raw_date:
            return normalize_decision_date(raw_date)

    raw_date = _extract_first_date(EXPLICIT_DATE_PATTERNS, header_text)
    if raw_date:
        return normalize_decision_date(raw_date)

    for line in _iter_priority_lines(lines):
        raw_date = _extract_first_date(FALLBACK_LINE_DATE_PATTERNS, line)
        if raw_date:
            return normalize_decision_date(raw_date)

    # Unknown-year survivors often have date cues deeper in the first pages.
    if fallback_text:
        fallback_header = fallback_text[:UNKNOWN_HEADER_CHAR_SCAN_LIMIT]
        fallback_lines = fallback_header.split("\n")[:UNKNOWN_HEADER_LINE_SCAN_LIMIT]

        for line in _iter_priority_lines(fallback_lines, head_limit=120, tail_limit=60):
            raw_date = _extract_first_date(EXPLICIT_DATE_PATTERNS, line)
            if raw_date:
                return normalize_decision_date(raw_date)

        raw_date = _extract_first_date(EXPLICIT_DATE_PATTERNS, fallback_header)
        if raw_date:
            return normalize_decision_date(raw_date)

        for line in _iter_priority_lines(fallback_lines, head_limit=120, tail_limit=60):
            raw_date = _extract_first_date(FALLBACK_LINE_DATE_PATTERNS, line)
            if raw_date:
                return normalize_decision_date(raw_date)

    return "UNKNOWN"

def extract_header_metadata(text: str):
    header_window = text[:HEADER_CHAR_SCAN_LIMIT]
    lines = header_window.split("\n")[:100]
    header = header_window

    metadata = {
        "court": "UNKNOWN",
        "court_level": "UNKNOWN",
        "case_number": "UNKNOWN",
        "decision_date": "UNKNOWN",
        "jurisdiction": "India"
    }

    court, court_level, court_reason = extract_court_metadata(lines, header)
    if court == "UNKNOWN":
        extended_header = text[:UNKNOWN_HEADER_CHAR_SCAN_LIMIT]
        extended_lines = extended_header.split("\n")[:UNKNOWN_HEADER_LINE_SCAN_LIMIT]
        court, court_level, court_reason = extract_unknown_court_metadata(extended_lines, extended_header)

    metadata["court"] = court
    metadata["court_level"] = court_level
    if court_reason:
        metadata["court_match_reason"] = court_reason

    # Extract case number
    metadata["case_number"] = extract_case_number(lines, header)

    metadata["decision_date"] = extract_decision_date(lines, header, fallback_text=text)

    petitioner, respondent = extract_parties(lines)
    if petitioner:
        metadata["petitioner"] = petitioner
    if respondent:
        metadata["respondent"] = respondent

    bench = extract_bench(lines)
    if bench:
        metadata["bench"] = bench

    return metadata
