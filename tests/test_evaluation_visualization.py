"""Kiểm thử trực quan hóa kết quả evaluation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from variable_misuse_gnn.visualization.evaluation_visualizer import (
    write_accuracy_chart,
    write_program_graph_svg,
)


class EvaluationVisualizationTest(unittest.TestCase):
    """Kiểm thử xuất SVG cho chart và Program Graph."""

    def test_write_accuracy_chart(self) -> None:
        """Biểu đồ accuracy được ghi ra file SVG."""
        rows = [
            {
                "graph_variant": "ast_only",
                "split": "eval",
                "checkpoint_epoch": 7,
                "loss": 1.2,
                "localization_accuracy": 0.5,
                "repair_accuracy": 0.6,
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "accuracy.svg"
            write_accuracy_chart(rows, output_path)

            content = output_path.read_text(encoding="utf-8")
            self.assertIn("<svg", content)
            self.assertIn("Localization Accuracy", content)

    def test_write_program_graph_svg_marks_prediction(self) -> None:
        """Program Graph SVG có node dự đoán lỗi và ground-truth."""
        graph = {
            "graph_id": "g1",
            "graph_variant": "ast_only",
            "num_nodes": 4,
            "node_tokens": ["def f(", "x", "return", "y"],
            "edge_index": [[0, 1], [1, 2], [2, 3]],
            "edge_type_names": ["syntax", "syntax", "syntax"],
            "repair_candidates": [1, 3],
            "repair_targets": [1],
            "localization_target": 3,
            "provenance": {"filepath": "sample.py"},
        }
        prediction = {
            "predicted_localization": 2,
            "predicted_repair": 1,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "graph.svg"
            write_program_graph_svg(graph, prediction, output_path, max_nodes=10)

            content = output_path.read_text(encoding="utf-8")
            self.assertIn("<svg", content)
            self.assertIn("pred=2", content)
            self.assertIn("target=3", content)
            self.assertIn("#dc2626", content)


if __name__ == "__main__":
    unittest.main()
