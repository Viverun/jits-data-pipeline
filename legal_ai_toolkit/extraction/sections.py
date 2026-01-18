"""
Statutory Section Extractor for Indian Legal Judgments

Extracts references to statutory sections from:
- Indian Penal Code (IPC)
- Code of Criminal Procedure (CrPC/Cr.P.C.)
- Indian Evidence Act
- Bhartiya Nyaya Sanhita (BNS) - New criminal code
- Other acts (Dowry Prohibition Act, NDPS Act, etc.)

FEATURES:
1. Handles section ranges (e.g., "Sections 498-A, 304-B")
2. Handles sub-sections (e.g., "Section 302(1)")
3. Handles section with clauses (e.g., "Section 376(2)(n)")
4. Normalizes section references
5. Deduplication
"""
import re
from typing import List, Dict


class SectionExtractor:
    """Extracts statutory section references from judgment text."""

    # Common statutory acts and their abbreviations
    ACT_PATTERNS = {
        "IPC": [
            r'I\.?P\.?C\.?',
            r'Indian Penal Code',
            r'Penal Code'
        ],
        "CrPC": [
            r'Cr\.?P\.?C\.?',
            r'Code of Criminal Procedure',
            r'Criminal Procedure Code'
        ],
        "Evidence Act": [
            r'Indian Evidence Act',
            r'Evidence Act'
        ],
        "BNS": [
            r'B\.?N\.?S\.?',
            r'Bhartiya Nyaya Sanhita'
        ],
        "BNSS": [
            r'B\.?N\.?S\.?S\.?',
            r'Bhartiya Nagarik Suraksha Sanhita'
        ],
        "Dowry Prohibition Act": [
            r'Dowry Prohibition Act',
            r'D\.?P\.? Act'
        ],
        "NDPS Act": [
            r'N\.?D\.?P\.?S\.? Act',
            r'Narcotic Drugs and Psychotropic Substances Act'
        ],
        "SC/ST Act": [
            r'SC/?ST Act',
            r'Scheduled Castes and Scheduled Tribes \(Prevention of Atrocities\) Act'
        ],
        "POCSO Act": [
            r'P\.?O\.?C\.?S\.?O\.? Act',
            r'Protection of Children from Sexual Offences Act'
        ]
    }

    # Section number patterns (handles various formats)
    SECTION_NUMBER_PATTERNS = [
        r'\d+[A-Z]?(?:-[A-Z])?',  # 498-A, 304-B, 376D
        r'\d+(?:\(\d+\))?(?:\([a-z]\))?',  # 302(1), 376(2)(n)
        r'\d+/\d+',  # 3/4 (as in Dowry Act)
        r'\d+'  # Simple numbers
    ]

    @classmethod
    def extract(cls, text: str) -> List[Dict]:
        """
        Extract all statutory section references from text.

        Args:
            text: Judgment text to extract sections from

        Returns:
            List of section dictionaries with metadata
        """
        sections = []
        seen = set()  # For deduplication

        # Extract sections for each act
        for act_name, act_patterns in cls.ACT_PATTERNS.items():
            for act_pattern in act_patterns:
                # Pattern: "Section(s) <numbers> <Act>"
                # Examples: "Sections 498-A, 304-B I.P.C."
                #           "Section 313 Cr.P.C."

                # Multiple sections pattern - capture everything between "Section(s)" and the act name
                pattern = rf'Sections?\s+([^.]+?)\s+{act_pattern}'

                for match in re.finditer(pattern, text, re.IGNORECASE):
                    section_text = match.group(1).strip()
                    act_ref = match.group(0)

                    # Parse individual sections from the list
                    individual_sections = cls._parse_section_list(section_text)

                    for section_num in individual_sections:
                        section_key = f"{act_name}_{section_num}"

                        if section_key in seen:
                            continue

                        section = {
                            "type": "statutory_section",
                            "act": act_name,
                            "section": section_num,
                            "raw": act_ref,
                            "start_pos": match.start(),
                            "end_pos": match.end()
                        }

                        sections.append(section)
                        seen.add(section_key)

                # Also catch standalone "under Section X" patterns
                pattern2 = rf'under\s+Sections?\s+([^.]+?)\s+{act_pattern}'

                for match in re.finditer(pattern2, text, re.IGNORECASE):
                    section_text = match.group(1).strip()
                    individual_sections = cls._parse_section_list(section_text)

                    for section_num in individual_sections:
                        section_key = f"{act_name}_{section_num}"

                        if section_key in seen:
                            continue

                        section = {
                            "type": "statutory_section",
                            "act": act_name,
                            "section": section_num,
                            "raw": match.group(0),
                            "start_pos": match.start(),
                            "end_pos": match.end()
                        }

                        sections.append(section)
                        seen.add(section_key)

        return sections

    @staticmethod
    def _parse_section_list(section_text: str) -> List[str]:
        """
        Parse a comma/and-separated list of sections.
        
        Args:
            section_text: Text like "498-A, 304-B, 323" or "302(1) and 376(2)(n)"
            
        Returns:
            List of individual section numbers
        """
        # Split by comma, 'and', '&'
        separators = r'\s*,\s*|\s+and\s+|\s+&\s+'
        parts = re.split(separators, section_text, flags=re.IGNORECASE)
        
        sections = []
        for part in parts:
            # Clean up the section number
            section = part.strip()
            
            # Remove common trailing words that shouldn't be part of the section number
            section = re.sub(r'\s+(of|the|under|in|to|for|with|by|from|as|at)\b.*$', '', section, flags=re.IGNORECASE)
            
            # Remove any non-section characters at the end
            section = re.sub(r'[^0-9A-Za-z\-/()]+$', '', section)
            
            # Only keep if it looks like a valid section number
            # Valid formats: 498-A, 304B, 313, 302(1), 376(2)(n), 3/4
            if re.match(r'^\d+[A-Za-z]?(?:-[A-Z])?(?:\(\d+\))?(?:\([a-z]\))?(?:/\d+)?$', section):
                sections.append(section)
        
        return sections

    @classmethod
    def group_by_act(cls, sections: List[Dict]) -> Dict[str, List[str]]:
        """
        Group sections by their parent act.

        Args:
            sections: List of section dictionaries

        Returns:
            Dictionary mapping act names to lists of section numbers
        """
        grouped = {}

        for section in sections:
            act = section.get("act")
            section_num = section.get("section")

            if act not in grouped:
                grouped[act] = []

            if section_num not in grouped[act]:
                grouped[act].append(section_num)

        return grouped


class SectionNormalizer:
    """Normalizes section references to standard formats."""

    @staticmethod
    def normalize(section: Dict) -> str:
        """
        Normalize a section to a standard ID format.

        Args:
            section: Section dictionary from SectionExtractor

        Returns:
            Normalized section ID (e.g., "IPC_498A", "CrPC_313")
        """
        act = section.get("act", "UNKNOWN").upper()
        section_num = section.get("section", "0")

        # Remove special characters for ID
        section_clean = re.sub(r'[^\w]', '', section_num)

        return f"{act}_{section_clean}"

    @staticmethod
    def to_standard_format(section: Dict) -> str:
        """
        Convert section to standard legal citation format.

        Args:
            section: Section dictionary

        Returns:
            Standard format (e.g., "Section 498-A IPC", "Section 313 Cr.P.C.")
        """
        act = section.get("act", "")
        section_num = section.get("section", "")

        # Format act name
        if act == "IPC":
            act_formatted = "I.P.C."
        elif act == "CrPC":
            act_formatted = "Cr.P.C."
        elif act == "BNS":
            act_formatted = "B.N.S."
        elif act == "BNSS":
            act_formatted = "B.N.S.S."
        else:
            act_formatted = act

        return f"Section {section_num} {act_formatted}"

    @staticmethod
    def get_section_category(section: Dict) -> str:
        """
        Categorize a section based on its act and number.

        Args:
            section: Section dictionary

        Returns:
            Category string (e.g., "criminal", "procedural", "evidence")
        """
        act = section.get("act", "")

        if act in ["IPC", "BNS"]:
            return "criminal"
        elif act in ["CrPC", "BNSS"]:
            return "procedural"
        elif act == "Evidence Act":
            return "evidence"
        else:
            return "special_act"
