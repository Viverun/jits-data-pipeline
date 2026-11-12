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

        # Abetment & Conspiracy
        "107": {"bns": "45", "type": "direct", "risk": "low", "offense": "Abetment"},
        "109": {"bns": "48", "type": "direct", "risk": "low", "offense": "Punishment of abetment"},
        "114": {"bns": "52", "type": "direct", "risk": "low", "offense": "Abettor present when offence is committed"},
        "120B": {"bns": "61", "type": "modified", "risk": "medium", "offense": "Criminal conspiracy"},

        # Cruelty & Dowry
        "498A": {"bns": "86", "type": "modified", "risk": "medium", "offense": "Cruelty by husband"},

        # Homicide Definitions
        "299": {"bns": "100", "type": "direct", "risk": "low", "offense": "Culpable homicide definition"},
        "300": {"bns": "101", "type": "direct", "risk": "low", "offense": "Murder definition"},

        # Hurt & Grievous Hurt
        "323": {"bns": "115", "type": "direct", "risk": "low", "offense": "Voluntarily causing hurt"},
        "325": {"bns": "117", "type": "direct", "risk": "low", "offense": "Voluntarily causing grievous hurt"},
        "326": {"bns": "118", "type": "direct", "risk": "low", "offense": "Grievous hurt by dangerous weapons"},

        # Kidnapping
        "363": {"bns": "137", "type": "direct", "risk": "low", "offense": "Punishment for kidnapping"},
        "364": {"bns": "140", "type": "direct", "risk": "low", "offense": "Kidnapping for murder"},

        # Theft, Extortion & Robbery
        "378": {"bns": "303(1)", "type": "direct", "risk": "low", "offense": "Theft definition"},
        "379": {"bns": "303(2)", "type": "direct", "risk": "low", "offense": "Punishment for theft"},
        "392": {"bns": "309", "type": "direct", "risk": "low", "offense": "Robbery"},
        "395": {"bns": "310", "type": "direct", "risk": "low", "offense": "Dacoity"},

        # Cheating & Fraud
        "415": {"bns": "318(1)", "type": "direct", "risk": "low", "offense": "Cheating definition"},
        "420": {"bns": "318", "type": "enhanced", "risk": "high", "offense": "Cheating"},
        "406": {"bns": "316", "type": "direct", "risk": "low", "offense": "Criminal breach of trust"},
        "409": {"bns": "316", "type": "direct", "risk": "low", "offense": "Criminal breach of trust by public servant"},
        "411": {"bns": "317", "type": "direct", "risk": "low", "offense": "Dishonestly receiving stolen property"},

        # Forgery
        "467": {"bns": "338", "type": "direct", "risk": "low", "offense": "Forgery of valuable security"},
        "468": {"bns": "336", "type": "direct", "risk": "low", "offense": "Forgery for cheating"},
        "471": {"bns": "340", "type": "direct", "risk": "low", "offense": "Using forged document"},

        # Definitions & Lesser Offences
        "30": {"bns": "2(37)", "type": "definition", "risk": "low", "offense": "Valuable security definition"},
        "84": {"bns": "22", "type": "direct", "risk": "low", "offense": "Act of person of unsound mind"},
        "90": {"bns": "28", "type": "direct", "risk": "low", "offense": "Consent known to be given under fear or misconception"},
        "106": {"bns": "44", "type": "direct", "risk": "low", "offense": "Right of private defence against deadly assault"},
        "143": {"bns": "189(1)", "type": "direct", "risk": "low", "offense": "Unlawful assembly punishment"},
        "147": {"bns": "191(2)", "type": "direct", "risk": "low", "offense": "Rioting punishment"},
        "148": {"bns": "191(3)", "type": "direct", "risk": "low", "offense": "Rioting armed with deadly weapon"},
        "161": {"bns": "repealed", "type": "repealed", "risk": "high", "offense": "Public servant taking gratification (Now PC Act)"},
        "182": {"bns": "217", "type": "direct", "risk": "low", "offense": "False information to public servant"},
        "188": {"bns": "223", "type": "direct", "risk": "low", "offense": "Disobedience to order of public servant"},
        "211": {"bns": "248", "type": "direct", "risk": "low", "offense": "False charge of offence with intent to injure"},
        "313": {"bns": "89", "type": "direct", "risk": "low", "offense": "Causing miscarriage without woman's consent"},
        "342": {"bns": "127", "type": "direct", "risk": "low", "offense": "Wrongful confinement punishment"},
        "360": {"bns": "137", "type": "direct", "risk": "low", "offense": "Kidnapping definition"},
        "379": {"bns": "303(2)", "type": "direct", "risk": "low", "offense": "Theft punishment"},
        "387": {"bns": "308(5)", "type": "direct", "risk": "low", "offense": "Extortion by putting fear of death"},
        "398": {"bns": "311", "type": "direct", "risk": "low", "offense": "Attempt to commit robbery armed with deadly weapon"},
        "405": {"bns": "316(1)", "type": "definition", "risk": "low", "offense": "Criminal breach of trust definition"},
        "495": {"bns": "82", "type": "modified", "risk": "medium", "offense": "Same offence with concealment of former marriage"},
        "497": {"bns": "repealed", "type": "repealed", "risk": "high", "offense": "Adultery - REPEALED"},
        "498": {"bns": "84", "type": "modified", "risk": "medium", "offense": "Enticing or taking away a married woman"},
        "124A": {"bns": "152", "type": "replaced", "risk": "high", "offense": "Sedition / Acts endangering sovereignty"},

        # Procedural & Evidence Interference
        "174A": {"bns": "211", "type": "direct", "risk": "low", "offense": "Non-appearance in response to a proclamation"},
        "201": {"bns": "238", "type": "direct", "risk": "low", "offense": "Causing disappearance of evidence"},
        "229A": {"bns": "264", "type": "direct", "risk": "low", "offense": "Failure by person released on bail to appear in Court"},

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
        "154": {"statute": "CrPC/BNSS", "description": "Information in cognizable cases (FIR)", "bnss": "173"},
        "156": {"statute": "CrPC/BNSS", "description": "Police officer's power to investigate", "bnss": "175"},
        "161": {"statute": "CrPC/BNSS", "description": "Examination by police", "bnss": "180"},
        "164": {"statute": "CrPC/BNSS", "description": "Statement before magistrate", "bnss": "183"},
        "167": {"statute": "CrPC/BNSS", "description": "Procedure when investigation cannot be completed in 24 hours (Remand)", "bnss": "187"},
        "173": {"statute": "CrPC/BNSS", "description": "Police report (Charge sheet)", "bnss": "193"},
        "190": {"statute": "CrPC/BNSS", "description": "Cognizance of offences by Magistrates", "bnss": "210"},
        "200": {"statute": "CrPC/BNSS", "description": "Examination of complainant", "bnss": "223"},
        "313": {"statute": "CrPC/BNSS", "description": "Statement of accused", "bnss": "347"},
        "437": {"statute": "CrPC/BNSS", "description": "Bail in non-bailable offences", "bnss": "483"},
        "438": {"statute": "CrPC/BNSS", "description": "Anticipatory bail", "bnss": "484"},
        "439": {"statute": "CrPC/BNSS", "description": "Special powers of High Court/Sessions Court regarding bail", "bnss": "485"},
        "482": {"statute": "CrPC/BNSS", "description": "Inherent powers of High Court (Quashing)", "bnss": "528"},
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
        # Normalize: remove hyphens and spaces
        section_num = section_num.strip().upper().replace("-", "").replace(" ", "")

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
