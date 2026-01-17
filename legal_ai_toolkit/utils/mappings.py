class IPCBNSTransitionDB:
    """
    Comprehensive IPC → BNS + CrPC/Evidence Act mapping
    """

    IPC_MAPPING = {
        # Murder & Culpable Homicide
        "302": {"bns": "103", "type": "direct", "risk": "low", "offense": "Murder"},
        "304": {"bns": "104", "type": "modified", "risk": "medium", "offense": "Culpable homicide not amounting to murder"},
        "304A": {"bns": "106", "type": "direct", "risk": "low", "offense": "Causing death by negligence"},
        "304B": {"bns": "80", "type": "modified", "risk": "medium", "offense": "Dowry death"},

        # Attempt to Murder & Hurt
        "307": {"bns": "109", "type": "direct", "risk": "low", "offense": "Attempt to murder"},
        "323": {"bns": "115", "type": "direct", "risk": "low", "offense": "Voluntarily causing hurt"},
        "325": {"bns": "117", "type": "direct", "risk": "low", "offense": "Voluntarily causing grievous hurt"},

        # Rape & Sexual Offences
        "376": {"bns": "64", "type": "enhanced", "risk": "high", "offense": "Rape"},
        "376D": {"bns": "70", "type": "enhanced", "risk": "high", "offense": "Gang rape"},

        # Abetment of Suicide
        "306": {"bns": "108", "type": "modified", "risk": "medium", "offense": "Abetment of suicide"},
        "309": {"bns": "309", "type": "repealed", "risk": "high", "offense": "Attempt to suicide - REPEALED"},

        # Cruelty & Dowry
        "498A": {"bns": "86", "type": "modified", "risk": "medium", "offense": "Cruelty by husband"},

        # Cheating & Fraud
        "420": {"bns": "318", "type": "enhanced", "risk": "high", "offense": "Cheating"},
        "409": {"bns": "316", "type": "direct", "risk": "low", "offense": "Criminal breach of trust by public servant"},

        # Criminal Intimidation
        "506": {"bns": "351", "type": "direct", "risk": "low", "offense": "Criminal intimidation"},
        "504": {"bns": "356", "type": "direct", "risk": "low", "offense": "Intentional insult"},

        # Common Provisions
        "34": {"bns": "3", "type": "direct", "risk": "low", "offense": "Common intention"},
        "120B": {"bns": "61", "type": "modified", "risk": "medium", "offense": "Criminal conspiracy"},
        "149": {"bns": "191", "type": "direct", "risk": "low", "offense": "Unlawful assembly"},

        # House Trespass & Theft
        "452": {"bns": "331", "type": "direct", "risk": "low", "offense": "House trespass after preparation for hurt"},
        "392": {"bns": "309", "type": "direct", "risk": "low", "offense": "Robbery"},
        "395": {"bns": "310", "type": "direct", "risk": "low", "offense": "Dacoity"},

        # Forgery
        "468": {"bns": "336", "type": "direct", "risk": "low", "offense": "Forgery for cheating"},
        "471": {"bns": "340", "type": "direct", "risk": "low", "offense": "Using forged document"},
    }

    # CrPC Provisions (NOT IPC - commonly misidentified)
    CRPC_PROVISIONS = {
        "482": {"statute": "CrPC/BNSS", "description": "Inherent powers of High Court", "bnss": "528"},
        "313": {"statute": "CrPC/BNSS", "description": "Statement of accused", "bnss": "347"},
        "164": {"statute": "CrPC/BNSS", "description": "Statement before magistrate", "bnss": "183"},
        "161": {"statute": "CrPC/BNSS", "description": "Examination by police", "bnss": "180"},
        "173": {"statute": "CrPC/BNSS", "description": "Police report", "bnss": "193"},
        "437": {"statute": "CrPC/BNSS", "description": "Bail in non-bailable offences", "bnss": "483"},
        "438": {"statute": "CrPC/BNSS", "description": "Anticipatory bail", "bnss": "484"},
        "439": {"statute": "CrPC/BNSS", "description": "Special powers of High Court/Sessions Court regarding bail", "bnss": "485"},
    }

    # Evidence Act (commonly misidentified as IPC)
    EVIDENCE_ACT = {
        "161": {"statute": "Evidence Act", "description": "Cross-examination"},
        "164": {"statute": "Evidence Act", "description": "Statement under Section 164"},
    }

    # Noise patterns (years, procedural references)
    NOISE_PATTERNS = {
        "1860", "1872", "1973", "2019", "2023",  # Years
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",  # Generic low numbers (likely chapter references)
    }

    @classmethod
    def get(cls, section_num: str):
        """Get IPC mapping with enhanced detection"""
        section_num = section_num.strip().upper()

        # Check if it's noise
        if section_num in cls.NOISE_PATTERNS:
            return {"type": "noise", "reason": "Generic number or year reference"}

        # Check IPC mapping
        if section_num in cls.IPC_MAPPING:
            return cls.IPC_MAPPING[section_num]

        # Check if it's actually CrPC
        if section_num in cls.CRPC_PROVISIONS:
            return {
                "type": "crpc_provision",
                "statute": cls.CRPC_PROVISIONS[section_num]["statute"],
                "description": cls.CRPC_PROVISIONS[section_num]["description"],
                "bnss": cls.CRPC_PROVISIONS[section_num].get("bnss"),
                "note": "This is CrPC, not IPC"
            }

        return None

    @classmethod
    def is_noise(cls, section_num: str):
        """Check if section number is noise"""
        return section_num.strip() in cls.NOISE_PATTERNS
