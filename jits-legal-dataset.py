"""JITS Legal Dataset loading script with explicit Features.

Why this exists:
  train.jsonl contains legal extraction structs that evolved over time.
  Three transition producers emitted different key sets, bench was str-or-list,
  citations/landmarks had optional keys, and several `by_*` / `issues.details`
  objects use dynamic keys. HF's automatic JSON -> Parquet inference samples
  the first chunk, infers e.g. bns as null type, then fails on later rows with:

    Couldn't cast array of type struct<ipc,bns,source,...,requires_judicial_confirmation,
    context_snippet> to {ipc,bns:null,...}

  This script declares the canonical uniform schema explicitly and converts
  dynamic-key maps to lists, so parquet conversion is deterministic.

  The underlying train.jsonl shape is unchanged for backward compatibility;
  conversion happens at load time in _generate_examples().
"""

import json

import datasets


_TRANSITION_FEATURE = {
    "ipc": datasets.Value("string"),
    "bns": datasets.Value("string"),
    "source": datasets.Value("string"),
    "validated": datasets.Value("bool"),
    "risk": datasets.Value("string"),
    "confidence": datasets.Value("string"),
    "note": datasets.Value("string"),
    "context_snippet": datasets.Value("string"),
    "requires_judicial_confirmation": datasets.Value("bool"),
    "temporal_warning": datasets.Value("string"),
}

_CITATION_FEATURE = {
    "type": datasets.Value("string"),
    "reporter": datasets.Value("string"),
    "year": datasets.Value("string"),
    "page": datasets.Value("string"),
    "volume": datasets.Value("string"),
    "court": datasets.Value("string"),
    "petitioner": datasets.Value("string"),
    "respondent": datasets.Value("string"),
    "case_name": datasets.Value("string"),
    "raw": datasets.Value("string"),
    "start_pos": datasets.Value("int64"),
    "end_pos": datasets.Value("int64"),
    "is_landmark": datasets.Value("bool"),
    "precedent_id": datasets.Value("string"),
}

_LANDMARK_FEATURE = {
    "precedent_id": datasets.Value("string"),
    "full_citation": datasets.Value("string"),
    "short_name": datasets.Value("string"),
    "aliases": datasets.Sequence(datasets.Value("string")),
    "year": datasets.Value("int64"),
    "court": datasets.Value("string"),
    "bench_strength": datasets.Value("int64"),
    "legal_principle": datasets.Value("string"),
    "issues": datasets.Sequence(datasets.Value("string")),
    "keywords": datasets.Sequence(datasets.Value("string")),
    "provisions": datasets.Sequence(datasets.Value("string")),
    "binding_authority": datasets.Value("string"),
    "overrules": datasets.Sequence(datasets.Value("string")),
    "status": datasets.Value("string"),
    "matched_by": datasets.Value("string"),
}

_ISSUE_FEATURE = {
    "issue_type": datasets.Value("string"),
    "statute": datasets.Value("string"),
    "keywords": datasets.Sequence(datasets.Value("string")),
    "sections": datasets.Sequence(datasets.Value("string")),
    "confidence": datasets.Value("string"),
    "keyword_count": datasets.Value("int64"),
    "mention_count": datasets.Value("int64"),
}


def _as_list_of_str(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    return [str(value)]


def _normalize_bench(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text or text.upper() == "UNKNOWN":
        return []
    if " | " in text:
        return [p.strip() for p in text.split(" | ") if p.strip()]
    return [text]


def _normalize_transition(item):
    if not isinstance(item, dict):
        return {k: None for k in _TRANSITION_FEATURE}
    return {
        "ipc": item.get("ipc"),
        "bns": item.get("bns"),
        "source": item.get("source"),
        "validated": bool(item.get("validated", False)),
        "risk": item.get("risk"),
        "confidence": item.get("confidence"),
        "note": item.get("note"),
        "context_snippet": item.get("context_snippet"),
        "requires_judicial_confirmation": bool(item.get("requires_judicial_confirmation", False)),
        "temporal_warning": item.get("temporal_warning"),
    }


def _to_int_or_none(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_citation(item):
    if not isinstance(item, dict):
        return {
            "type": None, "reporter": None, "year": None, "page": None,
            "volume": None, "court": None, "petitioner": None,
            "respondent": None, "case_name": None, "raw": None,
            "start_pos": None, "end_pos": None, "is_landmark": False,
            "precedent_id": None,
        }
    return {
        "type": item.get("type"),
        "reporter": item.get("reporter"),
        "year": item.get("year"),
        "page": item.get("page"),
        "volume": item.get("volume"),
        "court": item.get("court"),
        "petitioner": item.get("petitioner"),
        "respondent": item.get("respondent"),
        "case_name": item.get("case_name"),
        "raw": item.get("raw"),
        "start_pos": _to_int_or_none(item.get("start_pos")),
        "end_pos": _to_int_or_none(item.get("end_pos")),
        "is_landmark": bool(item.get("is_landmark", False)),
        "precedent_id": item.get("precedent_id"),
    }


def _normalize_landmark(item):
    if not isinstance(item, dict):
        return {
            "precedent_id": None, "full_citation": None, "short_name": None,
            "aliases": [], "year": None, "court": None, "bench_strength": None,
            "legal_principle": None, "issues": [], "keywords": [], "provisions": [],
            "binding_authority": None, "overrules": [], "status": None, "matched_by": None,
        }
    aliases = item.get("aliases", [])
    if not isinstance(aliases, list):
        aliases = []
    overrules = item.get("overrules", [])
    if not isinstance(overrules, list):
        overrules = [overrules] if overrules else []
    issues = item.get("issues", [])
    if not isinstance(issues, list):
        issues = []
    keywords = item.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []
    provisions = item.get("provisions", [])
    if not isinstance(provisions, list):
        provisions = []
    return {
        "precedent_id": item.get("precedent_id"),
        "full_citation": item.get("full_citation"),
        "short_name": item.get("short_name"),
        "aliases": [str(x) for x in aliases if x is not None],
        "year": _to_int_or_none(item.get("year")),
        "court": item.get("court"),
        "bench_strength": _to_int_or_none(item.get("bench_strength")),
        "legal_principle": item.get("legal_principle"),
        "issues": [str(x) for x in issues if x is not None],
        "keywords": [str(x) for x in keywords if x is not None],
        "provisions": [str(x) for x in provisions if x is not None],
        "binding_authority": item.get("binding_authority"),
        "overrules": [str(x) for x in overrules if x is not None],
        "status": item.get("status"),
        "matched_by": item.get("matched_by"),
    }


def _map_to_list(mapping, key_name="key", value_name="count"):
    if not isinstance(mapping, dict):
        return []
    return [{key_name: str(k), value_name: int(v) if isinstance(v, int) else 0}
            for k, v in mapping.items()]


class JitsLegalDataset(datasets.GeneratorBasedBuilder):
    VERSION = datasets.Version("1.14.0")

    def _info(self):
        return datasets.DatasetInfo(
            description="JITS Legal Dataset: deterministic Indian legal extraction with citation graph, section tagging, and IPC->BNS mapping.",
            homepage="https://github.com/Viverun/jits-data-pipeline",
            license="Apache-2.0",
            features=datasets.Features(
                {
                    "judgment_id": datasets.Value("string"),
                    "text": datasets.Value("string"),
                    "metadata": {
                        "court": datasets.Value("string"),
                        "court_level": datasets.Value("string"),
                        "decision_date": datasets.Value("string"),
                        "case_number": datasets.Value("string"),
                        "jurisdiction": datasets.Value("string"),
                        "petitioner": datasets.Value("string"),
                        "respondent": datasets.Value("string"),
                        "bench": datasets.Sequence(datasets.Value("string")),
                    },
                    "classification": {
                        "domain": datasets.Value("string"),
                        "confidence": datasets.Value("string"),
                        "signals": {
                            "civil": datasets.Sequence(datasets.Value("string")),
                            "criminal": datasets.Sequence(datasets.Value("string")),
                            "service": datasets.Sequence(datasets.Value("string")),
                            "writ_supervisory": datasets.Sequence(datasets.Value("string")),
                        },
                        "reasoning": datasets.Sequence(datasets.Value("string")),
                    },
                    "extractions": {
                        "citations": {
                            "total": datasets.Value("int64"),
                            "by_type": datasets.Sequence(
                                {"key": datasets.Value("string"), "count": datasets.Value("int64")}
                            ),
                            "details": datasets.Sequence(_CITATION_FEATURE),
                        },
                        "sections": {
                            "total": datasets.Value("int64"),
                            "by_act": datasets.Sequence(
                                {
                                    "act": datasets.Value("string"),
                                    "sections": datasets.Sequence(datasets.Value("string")),
                                }
                            ),
                            "details": datasets.Sequence(
                                {
                                    "section": datasets.Value("string"),
                                    "act": datasets.Value("string"),
                                }
                            ),
                        },
                        "transitions": {
                            "total": datasets.Value("int64"),
                            "by_source": datasets.Sequence(
                                {"source": datasets.Value("string"), "count": datasets.Value("int64")}
                            ),
                            "details": datasets.Sequence(_TRANSITION_FEATURE),
                        },
                        "landmarks": {
                            "total": datasets.Value("int64"),
                            "by_id": datasets.Sequence(
                                {"id": datasets.Value("string"), "count": datasets.Value("int64")}
                            ),
                            "details": datasets.Sequence(_LANDMARK_FEATURE),
                        },
                        "issues": {
                            "total": datasets.Value("int64"),
                            "details": datasets.Sequence(_ISSUE_FEATURE),
                        },
                    },
                    "statutory_transitions": datasets.Sequence(_TRANSITION_FEATURE),
                    "provenance": {
                        "pipeline_version": datasets.Value("string"),
                        "processed_date": datasets.Value("string"),
                        "processing_steps": datasets.Sequence(datasets.Value("string")),
                    },
                }
            ),
        )

    def _split_generators(self, dl_manager):
        data_file = dl_manager.download_and_extract("train.jsonl")
        return [datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": data_file})]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                md = row.get("metadata", {}) or {}
                cl = row.get("classification", {}) or {}
                ex = row.get("extractions", {}) or {}
                prov = row.get("provenance", {}) or {}

                top_trans = row.get("statutory_transitions", []) or []
                if isinstance(top_trans, dict):
                    top_trans = top_trans.get("transitions", []) or []
                norm_top_trans = [_normalize_transition(t) for t in top_trans if isinstance(t, dict)]

                cit_block = ex.get("citations", {}) or {}
                cit_details = [_normalize_citation(d) for d in (cit_block.get("details", []) or []) if isinstance(d, dict)]

                sec_block = ex.get("sections", {}) or {}
                sec_by_act = sec_block.get("by_act", {}) or {}
                sec_by_act_list = [
                    {"act": str(act), "sections": _as_list_of_str(sections)}
                    for act, sections in sec_by_act.items()
                ]
                sec_details = []
                for d in (sec_block.get("details", []) or []):
                    if isinstance(d, dict):
                        sec_details.append({"section": d.get("section"), "act": d.get("act")})

                tr_block = ex.get("transitions", {}) or {}
                # Prefer canonical top-level transitions when nested copy is stale.
                tr_details_src = tr_block.get("details", []) or []
                tr_details = [_normalize_transition(d) for d in tr_details_src if isinstance(d, dict)]
                if len(tr_details) != len(norm_top_trans):
                    tr_details = norm_top_trans

                lm_block = ex.get("landmarks", {}) or {}
                lm_details = [_normalize_landmark(d) for d in (lm_block.get("details", []) or []) if isinstance(d, dict)]

                iss_block = ex.get("issues", {}) or {}
                iss_raw = iss_block.get("details", {}) or {}
                iss_details = []
                if isinstance(iss_raw, dict):
                    for issue_type, v in iss_raw.items():
                        if not isinstance(v, dict):
                            continue
                        iss_details.append({
                            "issue_type": str(issue_type),
                            "statute": v.get("statute"),
                            "keywords": _as_list_of_str(v.get("keywords")),
                            "sections": _as_list_of_str(v.get("sections")),
                            "confidence": v.get("confidence"),
                            "keyword_count": _to_int_or_none(v.get("keyword_count")),
                            "mention_count": _to_int_or_none(v.get("mention_count")),
                        })
                elif isinstance(iss_raw, list):
                    for v in iss_raw:
                        if isinstance(v, dict) and "issue_type" in v:
                            iss_details.append({
                                "issue_type": v.get("issue_type"),
                                "statute": v.get("statute"),
                                "keywords": _as_list_of_str(v.get("keywords")),
                                "sections": _as_list_of_str(v.get("sections")),
                                "confidence": v.get("confidence"),
                                "keyword_count": _to_int_or_none(v.get("keyword_count")),
                                "mention_count": _to_int_or_none(v.get("mention_count")),
                            })

                signals = cl.get("signals", {}) or {}

                yield idx, {
                    "judgment_id": row.get("judgment_id", ""),
                    "text": row.get("text", ""),
                    "metadata": {
                        "court": md.get("court", ""),
                        "court_level": md.get("court_level", ""),
                        "decision_date": md.get("decision_date"),
                        "case_number": md.get("case_number", ""),
                        "jurisdiction": md.get("jurisdiction", ""),
                        "petitioner": md.get("petitioner", ""),
                        "respondent": md.get("respondent", ""),
                        "bench": _normalize_bench(md.get("bench", [])),
                    },
                    "classification": {
                        "domain": cl.get("domain", ""),
                        "confidence": cl.get("confidence", "low"),
                        "signals": {
                            "civil": _as_list_of_str(signals.get("civil")),
                            "criminal": _as_list_of_str(signals.get("criminal")),
                            "service": _as_list_of_str(signals.get("service")),
                            "writ_supervisory": _as_list_of_str(signals.get("writ_supervisory")),
                        },
                        "reasoning": _as_list_of_str(cl.get("reasoning")),
                    },
                    "extractions": {
                        "citations": {
                            "total": len(cit_details),
                            "by_type": _map_to_list(cit_block.get("by_type", {})),
                            "details": cit_details,
                        },
                        "sections": {
                            "total": len(sec_details),
                            "by_act": sec_by_act_list,
                            "details": sec_details,
                        },
                        "transitions": {
                            "total": len(tr_details),
                            "by_source": [
                                {"source": str(k), "count": int(v)}
                                for k, v in (tr_block.get("by_source", {}) or {}).items()
                            ] or [
                                {"source": str(k), "count": int(v)}
                                for k, v in self._count_sources(tr_details).items()
                            ],
                            "details": tr_details,
                        },
                        "landmarks": {
                            "total": len(lm_details),
                            "by_id": [
                                {"id": str(k), "count": int(v)}
                                for k, v in (lm_block.get("by_id", {}) or {}).items()
                            ],
                            "details": lm_details,
                        },
                        "issues": {
                            "total": len(iss_details),
                            "details": iss_details,
                        },
                    },
                    "statutory_transitions": norm_top_trans,
                    "provenance": {
                        "pipeline_version": str(prov.get("pipeline_version", prov.get("version", "2.0"))),
                        "processed_date": str(prov.get("processed_date", "")),
                        "processing_steps": _as_list_of_str(prov.get("processing_steps")),
                    },
                }

    @staticmethod
    def _count_sources(details):
        counts = {}
        for d in details:
            src = d.get("source") or "unknown"
            counts[src] = counts.get(src, 0) + 1
        return counts
