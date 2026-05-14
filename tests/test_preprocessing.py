"""Kiểm thử module tiền xử lý GREAT."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from variable_misuse_gnn.data.preprocessing.config import PreprocessingConfig
from variable_misuse_gnn.data.preprocessing.normalizer import normalize_example
from variable_misuse_gnn.data.preprocessing.pipeline import run_preprocessing
from variable_misuse_gnn.data.preprocessing.validation import validate_raw_example


def make_raw_example(has_bug: bool = True) -> dict:
    """Tạo sample GREAT tối giản nhưng hợp lệ."""
    return {
        "source_tokens": ["def f(", "x", ",", "y", ")", ":", "return", "x"],
        "has_bug": has_bug,
        "error_location": 7 if has_bug else 0,
        "repair_candidates": [1, 7] if has_bug else [1, 3],
        "bug_kind": 1 if has_bug else 0,
        "bug_kind_name": "VARIABLE_MISUSE" if has_bug else "NONE",
        "repair_targets": [1] if has_bug else [],
        "edges": [
            [0, 1, 8, "enum_SYNTAX"],
            [1, 7, 2, "enum_LAST_READ"],
            [6, 7, 9, "enum_NEXT_SYNTAX"],
        ],
        "provenances": [
            {
                "datasetProvenance": {
                    "datasetName": "ETHPy150Open",
                    "filepath": "repo/file.py",
                    "license": "mit",
                    "note": "test",
                }
            }
        ],
    }


class PreprocessingTest(unittest.TestCase):
    """Kiểm thử validator, normalizer và pipeline."""

    def test_validate_raw_example_accepts_valid_sample(self) -> None:
        """Validator chấp nhận sample hợp lệ."""
        is_valid, reason = validate_raw_example(make_raw_example())
        self.assertTrue(is_valid)
        self.assertEqual(reason, "ok")

    def test_normalizer_adds_repair_target_to_candidates(self) -> None:
        """Normalizer bổ sung repair target nếu candidate set bị thiếu."""
        raw_example = make_raw_example()
        raw_example["repair_candidates"] = [7]
        config = PreprocessingConfig(
            input_root=Path("unused"),
            output_root=Path("unused"),
            report_path=Path("unused/report.json"),
        )
        normalized = normalize_example(raw_example, "train", Path("sample.jsonl"), 1, config)
        self.assertIn(1, normalized.repair_candidates)
        self.assertIn("syntactic_next_token_data_flow", normalized.graph_variant_edges)

    def test_pipeline_writes_processed_jsonl(self) -> None:
        """Pipeline ghi JSONL đã chuẩn hóa và summary cho ba split."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "input"
            output_root = root / "output"
            input_root.mkdir()
            for split in ("train", "dev", "eval"):
                with (input_root / f"{split}_sample.jsonl").open("w", encoding="utf-8") as file:
                    file.write(json.dumps(make_raw_example(True)) + "\n")
                    file.write(json.dumps(make_raw_example(False)) + "\n")

            config = PreprocessingConfig(
                input_root=input_root,
                output_root=output_root,
                report_path=output_root / "summary.json",
                max_tokens=64,
                max_edges=128,
            )
            report = run_preprocessing(config)

            self.assertEqual(report["aggregate"]["counters"]["written"], 6)
            self.assertTrue((output_root / "train.jsonl").exists())
            self.assertTrue((output_root / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()

