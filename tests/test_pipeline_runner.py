import json
import tempfile
from pathlib import Path

from legal_ai_toolkit.pipeline.runner import BaseStep


class _RenamingStep(BaseStep):
    def process_item(self, data):
        data["judgment_id"] = f"OUT_{data['value']}"
        return data


class _FailingStep(BaseStep):
    def process_item(self, data):
        raise ValueError(f"boom: {data['value']}")


def test_base_step_prunes_stale_outputs():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        (input_dir / "TEMP_A.json").write_text(
            json.dumps({"judgment_id": "TEMP_A", "value": 1}),
            encoding="utf-8",
        )
        (input_dir / "TEMP_B.json").write_text(
            json.dumps({"judgment_id": "TEMP_B", "value": 2}),
            encoding="utf-8",
        )
        (output_dir / "STALE.json").write_text(json.dumps({"judgment_id": "STALE"}), encoding="utf-8")

        _RenamingStep(input_dir, output_dir).run()

        output_names = sorted(path.name for path in output_dir.glob("*.json"))

    assert output_names == ["OUT_1.json", "OUT_2.json"]


def test_error_logs_are_written_outside_data_root():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        (input_dir / "TEMP_A.json").write_text(
            json.dumps({"judgment_id": "TEMP_A", "value": 1}),
            encoding="utf-8",
        )

        _FailingStep(input_dir, output_dir).run()

        root_json = list(output_dir.glob("errors_*.json"))
        error_logs = list((output_dir / "_errors").glob("errors_*.json"))

    assert root_json == []
    assert len(error_logs) == 1
