import json
import random
import re
from pathlib import Path


DEFAULT_COURT_TOPICS = {
    "Supreme Court of India": [
        ("sc_criminal_appeal", "criminal appeal bail"),
        ("sc_service", "service matter promotion pension"),
        ("sc_writ", "writ petition article 32"),
        ("sc_civil", "civil appeal arbitration contract"),
    ],
    "Allahabad High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_dowry", "498A 304B dowry"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration property injunction"),
    ],
    "Delhi High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration commercial suit"),
    ],
    "Bombay High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_ndps", "ndps bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration property injunction"),
    ],
    "Madras High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "specific performance arbitration"),
    ],
    "Calcutta High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "property dispute injunction"),
    ],
    "Karnataka High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_pocso", "pocso bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration motor accident claim"),
    ],
    "Gujarat High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "property dispute injunction"),
    ],
    "Rajasthan High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_dowry", "498A 304B dowry"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration land acquisition"),
    ],
    "Patna High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "property dispute injunction"),
    ],
    "Punjab and Haryana High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_pocso", "pocso bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "specific performance arbitration"),
    ],
    "Kerala High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "arbitration property injunction"),
    ],
    "Madhya Pradesh High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_dowry", "498A 304B dowry"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "motor accident claim"),
    ],
    "Jharkhand High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "property dispute injunction"),
    ],
    "Chhattisgarh High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "land acquisition compensation"),
    ],
    "Orissa High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "property dispute injunction"),
    ],
    "Telangana High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_ndps", "ndps bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "commercial suit arbitration"),
    ],
    "Andhra Pradesh High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_pocso", "pocso bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
        ("hc_civil", "specific performance arbitration"),
    ],
    "Uttarakhand High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
    ],
    "Himachal Pradesh High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_quashing", "quashing 482 crpc"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
    ],
    "Gauhati High Court": [
        ("hc_bail", "anticipatory bail section 438"),
        ("hc_pocso", "pocso bail"),
        ("hc_service", "pension promotion seniority"),
        ("hc_writ", "writ petition article 226"),
    ],
    "Central Administrative Tribunal": [
        ("cat_service", "pension promotion seniority"),
        ("cat_service", "disciplinary proceedings"),
        ("cat_service", "recruitment appointment"),
        ("cat_service", "reservation roster"),
    ],
}

DEFAULT_GENERAL_FALLBACK_QUERIES = [
    {"query": "criminal appeal judgment bail", "category": "general_criminal"},
    {"query": "civil appeal arbitration contract", "category": "general_civil"},
    {"query": "service matter pension promotion", "category": "general_service"},
    {"query": "writ petition article 226 administrative law", "category": "general_writ"},
    {"query": "quashing 482 crpc judgment", "category": "general_quashing"},
    {"query": "anticipatory bail section 438 judgment", "category": "general_bail"},
]

DEFAULT_YEARS = [2025, 2024, 2023, 2022, 2021, 2020]
DEEP_YEARS = DEFAULT_YEARS + [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]

COMMON_HIGH_COURT_DEEP_TOPICS = [
    ("hc_revision", "criminal revision"),
    ("hc_cheque_bounce", "section 138 ni act"),
    ("hc_motor_accident", "motor accident compensation"),
    ("hc_land_acquisition", "land acquisition compensation"),
    ("hc_habeas", "habeas corpus detention"),
]

SUPREME_COURT_DEEP_TOPICS = [
    ("sc_special_leave", "special leave petition article 136"),
    ("sc_constitution", "constitutional bench article 14 article 21"),
    ("sc_land_acquisition", "land acquisition compensation"),
    ("sc_tax", "gst income tax"),
]

CAT_DEEP_TOPICS = [
    ("cat_service", "macp acp pay fixation"),
    ("cat_service", "transfer posting deputation"),
    ("cat_service", "compassionate appointment"),
]

DEEP_EXTRA_COURTS = {
    "Armed Forces Tribunal": [
        ("aft_service", "disability pension"),
        ("aft_service", "court martial"),
        ("aft_service", "release medical board"),
        ("aft_service", "promotion seniority"),
    ],
    "National Green Tribunal": [
        ("ngt_environment", "environment compensation pollution"),
        ("ngt_clearance", "environment clearance"),
        ("ngt_waste", "solid waste management"),
        ("ngt_forest", "forest conservation"),
    ],
}

DEEP_GENERAL_FALLBACK_QUERIES = [
    {"query": "criminal revision judgment", "category": "general_revision"},
    {"query": "section 138 ni act judgment", "category": "general_ni_act"},
    {"query": "motor accident compensation judgment", "category": "general_motor_accident"},
    {"query": "land acquisition compensation judgment", "category": "general_land_acquisition"},
    {"query": "habeas corpus detention judgment", "category": "general_habeas"},
    {"query": "special leave petition article 136 judgment", "category": "general_slp"},
    {"query": "constitutional bench article 21 judgment", "category": "general_constitution"},
    {"query": "gst income tax judgment", "category": "general_tax"},
]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "query"


def _build_court_topics(profile: str):
    court_topics = {court: list(topics) for court, topics in DEFAULT_COURT_TOPICS.items()}
    if profile != "deep":
        return court_topics

    for court in list(court_topics):
        if court == "Supreme Court of India":
            court_topics[court].extend(SUPREME_COURT_DEEP_TOPICS)
        elif court == "Central Administrative Tribunal":
            court_topics[court].extend(CAT_DEEP_TOPICS)
        elif "High Court" in court:
            court_topics[court].extend(COMMON_HIGH_COURT_DEEP_TOPICS)

    for court, topics in DEEP_EXTRA_COURTS.items():
        court_topics.setdefault(court, []).extend(topics)

    return court_topics


def _build_general_queries(profile: str):
    queries = list(DEFAULT_GENERAL_FALLBACK_QUERIES)
    if profile == "deep":
        queries.extend(DEEP_GENERAL_FALLBACK_QUERIES)
    return queries


def build_expansion_queries(shuffle=False, seed=42, profile="default"):
    if profile not in {"default", "deep"}:
        raise ValueError(f"Unsupported query profile: {profile}")

    years = DEFAULT_YEARS if profile == "default" else DEEP_YEARS
    court_topics = _build_court_topics(profile)
    general_queries = _build_general_queries(profile)
    queries = []
    seen = set()

    def add_query(query, category):
        if query in seen:
            return
        seen.add(query)
        queries.append({"query": query, "category": category})

    for court, topics in court_topics.items():
        for topic_key, phrase in topics:
            base_category = f"{slugify(court)}_{topic_key}"
            add_query(f"{court} {phrase}", base_category)
            for year in years:
                add_query(f"{court} {phrase} {year}", f"{base_category}_{year}")

    for item in general_queries:
        add_query(item["query"], item["category"])
        for year in years:
            add_query(f"{item['query']} {year}", f"{item['category']}_{year}")

    if shuffle:
        random.Random(seed).shuffle(queries)

    return queries


def load_queries_from_file(path):
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if file_path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            return data
        raise ValueError("JSON query file must contain a list of query objects.")

    queries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("{"):
            queries.append(json.loads(line))
        else:
            queries.append({"query": line, "category": slugify(line)})
    return queries
