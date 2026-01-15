class IPCBNSTransitionDB:
    """
    Authoritative IPC → BNS mapping
    Source: Government Gazette + Bharatiya Nyaya Sanhita, 2023
    """

    MAPPING = {
        "302": {"bns": "103", "type": "direct", "risk": "low"},
        "304": {"bns": "104", "type": "modified", "risk": "medium"},
        "304A": {"bns": "106", "type": "direct", "risk": "low"},
        "376": {"bns": "64", "type": "enhanced", "risk": "high"},
        "420": {"bns": "318", "type": "enhanced", "risk": "high"},
        "498A": {"bns": "86", "type": "modified", "risk": "medium"},
        "506": {"bns": "351", "type": "direct", "risk": "low"},
    }

    @classmethod
    def get(cls, ipc_section: str):
        return cls.MAPPING.get(ipc_section)
