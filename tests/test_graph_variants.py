"""Kiểm thử graph variant và relation type."""

from __future__ import annotations

import unittest

from variable_misuse_gnn.graph.variants import (
    EDGE_TYPE_ID_TO_NAME,
    get_graph_variant,
    relation_type_id,
)


class GraphVariantsTest(unittest.TestCase):
    """Kiểm thử mapping graph variant theo yêu cầu đồ án."""

    def test_required_variants_have_expected_edge_groups(self) -> None:
        """Ba variant bắt buộc giữ đúng nhóm edge."""
        self.assertEqual(get_graph_variant("ast_only").edge_groups, frozenset({"syntax"}))
        self.assertEqual(
            get_graph_variant("ast_next_token").edge_groups,
            frozenset({"syntax", "next_token"}),
        )
        self.assertEqual(
            get_graph_variant("ast_next_token_data_flow").edge_groups,
            frozenset({"syntax", "next_token", "data_flow", "lexical"}),
        )

    def test_forward_and_reverse_relation_ids_are_stable(self) -> None:
        """Relation type forward/reverse ổn định cho GGNN."""
        self.assertEqual(relation_type_id("syntax"), 0)
        self.assertEqual(relation_type_id("syntax", is_reverse=True), 1)
        self.assertEqual(relation_type_id("next_token"), 2)
        self.assertEqual(relation_type_id("data_flow", is_reverse=True), 5)
        self.assertEqual(EDGE_TYPE_ID_TO_NAME[1], "syntax_reverse")


if __name__ == "__main__":
    unittest.main()

