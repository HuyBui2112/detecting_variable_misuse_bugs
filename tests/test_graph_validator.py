"""Kiểm thử validator cho compact sample và Program Graph."""

from __future__ import annotations

import unittest

from test_graph_builder import make_compact_example
from variable_misuse_gnn.graph.builder import build_program_graph
from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.validator import validate_preprocessed_example, validate_program_graph


class GraphValidatorTest(unittest.TestCase):
    """Kiểm thử các lỗi schema cơ bản."""

    def test_validate_preprocessed_example_accepts_valid_sample(self) -> None:
        """Validator chấp nhận compact sample hợp lệ."""
        is_valid, reason = validate_preprocessed_example(make_compact_example())
        self.assertTrue(is_valid)
        self.assertEqual(reason, "ok")

    def test_validate_preprocessed_example_rejects_bad_edge_endpoint(self) -> None:
        """Validator loại edge trỏ ra ngoài node range."""
        example = make_compact_example()
        example["edges"] = [[0, 99, 0, 7]]

        is_valid, reason = validate_preprocessed_example(example)

        self.assertFalse(is_valid)
        self.assertEqual(reason, "invalid_edge_endpoint_index")

    def test_validate_program_graph_accepts_built_graph(self) -> None:
        """Graph build từ sample hợp lệ vượt qua validator."""
        graph = build_program_graph(
            make_compact_example(),
            GraphConstructionConfig(graph_variant="ast_next_token_data_flow"),
        )
        is_valid, reason = validate_program_graph(graph)

        self.assertTrue(is_valid)
        self.assertEqual(reason, "ok")


if __name__ == "__main__":
    unittest.main()

