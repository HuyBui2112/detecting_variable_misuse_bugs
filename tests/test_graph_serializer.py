"""Kiểm thử serializer và pipeline graph construction nhỏ."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_graph_builder import make_compact_example
from variable_misuse_gnn.graph.builder import build_program_graph
from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.pipeline import run_graph_construction
from variable_misuse_gnn.graph.serializer import GraphShardWriter, iter_serialized_graphs


class GraphSerializerTest(unittest.TestCase):
    """Kiểm thử ghi/đọc graph shard."""

    def test_graph_shard_writer_round_trip(self) -> None:
        """Serializer đọc lại graph không mất label và edge type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = GraphConstructionConfig(graph_variant="ast_only")
            graph = build_program_graph(make_compact_example(), config)

            with GraphShardWriter(root, "ast_only", "train", shard_size=10) as writer:
                writer.write(graph)

            graphs = list(iter_serialized_graphs(root / "ast_only" / "train"))

            self.assertEqual(len(graphs), 1)
            self.assertEqual(graphs[0].graph_id, graph.graph_id)
            self.assertEqual(graphs[0].localization_target, graph.localization_target)
            self.assertEqual(graphs[0].edge_type_names, graph.edge_type_names)

    def test_pipeline_writes_demo_graph_and_report(self) -> None:
        """Pipeline ghi graph shard và report cho split nhỏ."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "input"
            output_root = root / "graphs"
            input_root.mkdir()
            with (input_root / "train.jsonl").open("w", encoding="utf-8") as file:
                file.write(json.dumps(make_compact_example(), ensure_ascii=False) + "\n")

            config = GraphConstructionConfig(
                input_root=input_root,
                output_root=output_root,
                graph_variant="ast_next_token_data_flow",
                splits=("train",),
                shard_size=10,
            )
            report = run_graph_construction(config)

            self.assertEqual(report["aggregate"]["counters"]["written"], 1)
            self.assertTrue(
                (
                    output_root
                    / "ast_next_token_data_flow"
                    / "train"
                    / "shard_00000.jsonl"
                ).exists()
            )
            self.assertTrue(
                (
                    output_root
                    / "ast_next_token_data_flow"
                    / "graph_construction_summary.json"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()

