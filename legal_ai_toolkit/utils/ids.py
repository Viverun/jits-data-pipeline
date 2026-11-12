import hashlib
import re


DOMAIN_CODES = {
    "criminal": "CR",
    "civil": "CV",
    "service": "SV",
    "mixed": "MX",
    "unknown": "UN",
}

COURT_CODE_MAP = {
    "supreme court": "SC",
    "allahabad": "ALL",
    "bombay": "BOM",
    "delhi": "DEL",
    "madras": "MAD",
    "calcutta": "CAL",
    "kerala": "KER",
    "karnataka": "KAR",
    "karnatka": "KAR",
    "gujarat": "GUJ",
    "rajasthan": "RAJ",
    "patna": "PAT",
    "andhra pradesh": "AND",
    "telangana": "TEL",
    "punjab and haryana": "PNH",
    "punjab": "PNH",
    "haryana": "PNH",
    "himachal pradesh": "HIM",
    "madhya pradesh": "MPD",
    "orissa": "ORI",
    "odisha": "ORI",
    "gauhati": "GAU",
    "assam": "ASM",
    "jharkhand": "JHA",
    "chhattisgarh": "CHA",
    "meghalaya": "MEG",
    "jammu": "JKH",
    "kashmir": "JKH",
    "uttarakhand": "UTK",
    "sikkim": "SIK",
    "tripura": "TRI",
    "manipur": "MAN",
    "central administrative tribunal": "CAT",
    "state administrative tribunal": "SAT",
    "armed forces tribunal": "AFT",
    "national green tribunal": "NGT",
    "consumer disputes redressal commission": "CDR",
    "industrial court": "IND",
    "labour court": "LAB",
    "family court": "FAM",
    "motor accident claims tribunal": "MAC",
}

COURT_STOPWORDS = {
    "the",
    "high",
    "court",
    "courts",
    "of",
    "at",
    "in",
    "for",
    "and",
    "bench",
    "principal",
    "seat",
    "new",
    "present",
    "dated",
    "date",
    "decision",
    "judgment",
    "reserved",
    "order",
    "case",
    "petition",
    "application",
    "appeal",
    "civil",
    "criminal",
    "miscellaneous",
    "misc",
    "no",
    "afr",
    "vide",
    "against",
    "respondents",
    "common",
    "given",
    "keeping",
    "view",
    "representations",
    "received",
    "various",
    "quarters",
    "observations",
    "made",
    "ble",
}


def resolve_court_code(court_name: str) -> str:
    """Resolve a stable court code from noisy extracted court names."""
    if not court_name or str(court_name).upper() == "UNKNOWN":
        return "UNK"

    normalized = re.sub(r"[^a-z0-9\s]+", " ", str(court_name).lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()

    for keyword, code in COURT_CODE_MAP.items():
        if keyword in normalized:
            return code

    words = [
        word for word in normalized.split()
        if len(word) > 2 and word not in COURT_STOPWORDS
    ]
    return words[0][:3].upper() if words else "UNK"

def generate_judgment_id(
    court_level: str,
    court_code: str,
    year: int,
    domain: str,
    text: str,
    seq: int = None
) -> str:
    """
    Generate deterministic JITS judgment ID
    """

    court_level = court_level.upper()
    court_code = court_code.upper()
    domain = DOMAIN_CODES.get(domain.lower(), "UN")
    try:
        year_part = f"{int(year):04d}" if int(year) >= 0 else "0000"
    except (TypeError, ValueError):
        year_part = "0000"

    if seq is None:
        # Deterministic hash-based fallback
        hash_part = hashlib.sha1(text.encode("utf-8")).hexdigest()[:6].upper()
        seq_part = hash_part
    else:
        seq_part = f"{seq:06d}"

    return f"IN-{court_level}-{court_code}-{year_part}-{domain}-{seq_part}"
