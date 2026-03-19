import hashlib


DOMAIN_CODES = {
    "criminal": "CR",
    "civil": "CV",
    "service": "SV",
    "mixed": "MX",
    "unknown": "UN",
}

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

    if seq is None:
        # Deterministic hash-based fallback
        hash_part = hashlib.sha1(text.encode("utf-8")).hexdigest()[:6].upper()
        seq_part = hash_part
    else:
        seq_part = f"{seq:06d}"

    return f"IN-{court_level}-{court_code}-{year}-{domain}-{seq_part}"
