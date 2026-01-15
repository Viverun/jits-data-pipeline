import re

class CitationExtractor:

    PATTERNS = {
        "AIR": r'AIR\s+(\d{4})\s+SC\s+(\d+)',
        "SCC": r'\((\d{4})\)\s+\d+\s+SCC\s+(\d+)',
        "SCR": r'\((\d{4})\)\s+\d+\s+SCR\s+(\d+)',
        "JT": r'\((\d{4})\)\s+\d+\s+JT\s+(\d+)',
        "SCALE": r'\((\d{4})\)\s+\d+\s+Scale\s+(\d+)',
        "HC": r'\d{4}\s+\(\d+\)\s+(KLT|Bom|Del|Mad|Cal)\s+(\d+)'
    }

    CASE_NAME = r'([A-Z][a-zA-Z\s]+)\s+(?:vs\.?|v\.?|versus)\s+([A-Z][a-zA-Z\s]+)'

    @classmethod
    def extract(cls, text: str):
        citations = []

        for reporter, pattern in cls.PATTERNS.items():
            for m in re.finditer(pattern, text):
                citations.append({
                    "reporter": reporter,
                    "year": m.group(1),
                    "page": m.group(2),
                    "raw": m.group(0)
                })

        for m in re.finditer(cls.CASE_NAME, text):
            citations.append({
                "case_name": f"{m.group(1)} v. {m.group(2)}",
                "raw": m.group(0)
            })

        return citations
