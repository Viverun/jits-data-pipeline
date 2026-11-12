import re
from collections import defaultdict

def extract_legal_sections_v2(text):
    """Enhanced section extraction with act disambiguation"""

    sections = {
        'ipc': [],
        'crpc': [],
        'iea': [],  # Indian Evidence Act
        'pc_act': [],  # Prevention of Corruption Act
        'ni_act': [],  # Negotiable Instruments Act
        'other_acts': defaultdict(list)
    }

    # IPC pattern (handles 498A, 376D, etc.)
    # Added [A-Z\-]* to capture variants like 498-A or 498A
    ipc_pattern = r'(?:Section|Sec\.|S\.)\s*(\d+[A-Z]?(?:-[A-Z])?)\s+(?:of\s+)?(?:the\s+)?(?:IPC|Indian Penal Code)'
    ipc_matches = re.findall(ipc_pattern, text, re.IGNORECASE)
    sections['ipc'] = sorted(list(set(m.upper() for m in ipc_matches)))

    # CrPC pattern (handles Section 154, 173, etc.)
    crpc_pattern = r'(?:Section|Sec\.|S\.)\s*(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?(?:CrPC|Cr\.P\.C\.|Code of Criminal Procedure)'
    crpc_matches = re.findall(crpc_pattern, text, re.IGNORECASE)
    sections['crpc'] = sorted(list(set(m.upper() for m in crpc_matches)))

    # Evidence Act pattern
    iea_pattern = r'(?:Section|Sec\.|S\.)\s*(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?(?:Indian Evidence Act|Evidence Act)'
    iea_matches = re.findall(iea_pattern, text, re.IGNORECASE)
    sections['iea'] = sorted(list(set(m.upper() for m in iea_matches)))

    # Prevention of Corruption Act (critical for service matters)
    pc_pattern = r'(?:Section|Sec\.|S\.)\s*(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?(?:Prevention of Corruption Act|P\.C\. Act)'
    pc_matches = re.findall(pc_pattern, text, re.IGNORECASE)
    sections['pc_act'] = sorted(list(set(m.upper() for m in pc_matches)))

    # Negotiable Instruments Act (Section 138 is extremely common)
    ni_pattern = r'(?:Section|Sec\.|S\.)\s*(\d+)\s+(?:of\s+)?(?:the\s+)?(?:Negotiable Instruments Act|N\.I\. Act)'
    ni_matches = re.findall(ni_pattern, text, re.IGNORECASE)
    sections['ni_act'] = sorted(list(set(m.upper() for m in ni_matches)))

    return sections
