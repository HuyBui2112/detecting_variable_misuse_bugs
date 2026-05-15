"""Kiểm thử build Program Graph từ GREAT compact sample."""

from __future__ import annotations

import unittest

from variable_misuse_gnn.graph.builder import build_program_graph
from variable_misuse_gnn.graph.config import GraphConstructionConfig


def make_compact_example(has_bug: bool = True) -> dict:
    """Tạo sample compact nhỏ có đủ syntax, next token và data-flow edge."""
    return {
        "id": "sample-1",
        "split": "train",
        "tokens": ["def f(", "x", ",", "y", ")", ":", "return", "x"],
        "has_bug": has_bug,
        "loc": 7 if has_bug else None,
        "candidates": [1, 3, 7],
        "targets": [1] if has_bug else [],
        "edges": [
            [0, 1, 0, 7],
            [6, 7, 1, -1],
            [1, 7, 2, 2],
            [1, 7, 3, 9],
            [2, 3, 5, 11],
        ],
        "provenance": {"license": "mit", "filepath": "repo/file.py"},
    }


class GraphBuilderTest(unittest.TestCase):
    """Kiểm thử lọc edge, inverse edge và label."""

    def test_ast_only_keeps_only_syntax_with_inverse_edge(self) -> None:
        """AST-only chỉ giữ syntax và syntax reverse."""
        config = GraphConstructionConfig(graph_variant="ast_only")
        graph = build_program_graph(make_compact_example(), config)

        self.assertEqual(graph.edge_type_names, ["syntax", "syntax_reverse"])
        self.assertEqual(graph.edge_index, [[0, 1], [1, 0]])
        self.assertEqual(graph.localization_target, 7)
        self.assertTrue(graph.candidate_mask[1])
        self.assertTrue(graph.candidate_mask[7])

    def test_data_flow_variant_keeps_expected_edge_groups(self) -> None:
        """Variant chính giữ syntax, NextToken, Data Flow và lexical."""
        config = GraphConstructionConfig(graph_variant="ast_next_token_data_flow")
        graph = build_program_graph(make_compact_example(), config)

        self.assertEqual(len(graph.edge_index), 8)
        self.assertIn("data_flow", graph.edge_type_names)
        self.assertIn("data_flow_reverse", graph.edge_type_names)
        self.assertIn("lexical", graph.edge_type_names)
        self.assertNotIn("control_flow", graph.edge_type_names)

    def test_no_bug_sample_has_empty_repair_targets(self) -> None:
        """No-bug sample giữ localization target rỗng."""
        config = GraphConstructionConfig(graph_variant="ast_next_token")
        graph = build_program_graph(make_compact_example(False), config)

        self.assertFalse(graph.has_bug)
        self.assertIsNone(graph.localization_target)
        self.assertEqual(graph.repair_targets, [])


if __name__ == "__main__":
    unittest.main()

