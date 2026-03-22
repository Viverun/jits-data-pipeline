import importlib.util
import json
import tempfile
from pathlib import Path


def _load_normalize_dataset_module():
    module_path = Path("scripts/normalize_dataset.py")
    spec = importlib.util.spec_from_file_location("normalize_dataset", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_should_export_record_excludes_unknown_case_by_default():
    module = _load_normalize_dataset_module()
    record = {
        "judgment_id": "IN-UNKNOWN-UNK-2024-CR-ABCDE1",
        "metadata": {"court": "UNKNOWN", "court_level": "UNKNOWN"},
        "classification": {"domain": "criminal"},
    }

    include, reason = module.should_export_record(record)

    assert include is False
    assert reason == "unknown_id"


def test_should_export_record_excludes_unknown_year_id_by_default():
    module = _load_normalize_dataset_module()
    record = {
        "judgment_id": "IN-HC-ALL-0000-SV-ABCDE1",
        "metadata": {"court": "Allahabad High Court", "court_level": "HC"},
        "classification": {"domain": "service"},
    }

    include, reason = module.should_export_record(record)

    assert include is False
    assert reason == "unknown_year_id"


def test_should_export_record_can_exclude_unknown_domain():
    module = _load_normalize_dataset_module()
    record = {
        "judgment_id": "IN-HC-DEL-2024-CV-ABCDE1",
        "metadata": {"court": "Delhi High Court", "court_level": "HC"},
        "classification": {"domain": "unknown"},
    }

    include, reason = module.should_export_record(record, exclude_unknown_domain=True)

    assert include is False
    assert reason == "unknown_domain"


def test_export_jsonl_skips_unknown_cases_by_default():
    module = _load_normalize_dataset_module()

    good_record = {
        "judgment_id": "IN-HC-DEL-2024-CV-ABCDE1",
        "text": "sample text",
        "metadata": {
            "court": "Delhi High Court",
            "court_level": "HC",
            "decision_date": "2024-01-15",
            "case_number": "W.P.(C) 10/2024",
            "jurisdiction": "India",
        },
        "classification": {"domain": "civil"},
    }
    unknown_record = {
        "judgment_id": "IN-UNKNOWN-UNK-2024-CV-ABCDE2",
        "text": "sample text",
        "metadata": {
            "court": "UNKNOWN",
            "court_level": "UNKNOWN",
            "decision_date": "2024-01-16",
            "case_number": "UNKNOWN",
            "jurisdiction": "India",
        },
        "classification": {"domain": "civil"},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "in"
        output_file = Path(tmpdir) / "train.jsonl"
        input_dir.mkdir()
        (input_dir / "good.json").write_text(json.dumps(good_record), encoding="utf-8")
        (input_dir / "unknown.json").write_text(json.dumps(unknown_record), encoding="utf-8")

        count, skipped = module.export_jsonl(input_dir, output_file)

        lines = output_file.read_text(encoding="utf-8").strip().splitlines()

    assert count == 1
    assert skipped["unknown_id"] == 1
    assert len(lines) == 1
    assert json.loads(lines[0])["judgment_id"] == "IN-HC-DEL-2024-CV-ABCDE1"


def test_validate_release_quality_fails_for_unknown_year_ids():
    module = _load_normalize_dataset_module()
    bad_record = {
        "judgment_id": "IN-HC-ALL-0000-SV-ABCDE1",
        "text": "sample text",
        "metadata": {
            "court": "Allahabad High Court",
            "court_level": "HC",
            "decision_date": "UNKNOWN",
            "case_number": "W.P.(C) 10/2024",
            "jurisdiction": "India",
        },
        "classification": {"domain": "service"},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "train.jsonl"
        output_file.write_text(json.dumps(module.normalize_record(bad_record)) + "\n", encoding="utf-8")

        try:
            module.validate_release_quality(output_file)
            assert False, "Expected ValueError for unknown-year IDs"
        except ValueError as exc:
            assert "Release gate failed" in str(exc)
