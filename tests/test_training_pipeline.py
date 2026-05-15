"""Kiểm thử pipeline training GGNN với graph nhỏ."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import torch

from variable_misuse_gnn.models.ggnn import GGNNVariableMisuseModel
from variable_misuse_gnn.training.config import TrainingConfig
from variable_misuse_gnn.training.dataset import GraphShardDataset, collate_graphs
from variable_misuse_gnn.training.losses import compute_variable_misuse_loss
from variable_misuse_gnn.training.trainer import run_training


def make_training_graph(graph_id: str, has_bug: bool) -> dict:
    """Tạo ProgramGraph JSON tối giản cho training test."""
    return {
        "graph_id": graph_id,
        "split": "train",
        "graph_variant": "ast_only",
        "num_nodes": 4,
        "node_tokens": ["def f(", "x", "return", "y"],
        "node_types": ["token"] * 4,
        "candidate_mask": [False, True, False, True],
        "edge_index": [[0, 1], [1, 0], [2, 3], [3, 2]],
        "edge_types": [0, 1, 0, 1],
        "edge_type_names": ["syntax", "syntax_reverse", "syntax", "syntax_reverse"],
        "edge_group_ids": [0, 0, 0, 0],
        "raw_edge_types": [7, 7, 7, 7],
        "has_bug": has_bug,
        "localization_target": 3 if has_bug else None,
        "repair_candidates": [1, 3],
        "repair_targets": [1] if has_bug else [],
        "provenance": {"license": "mit", "filepath": "repo/file.py"},
    }


def write_graph_shards(root: Path) -> None:
    """Ghi graph shard train/dev nhỏ."""
    for split in ("train", "dev"):
        split_dir = root / "ast_only" / split
        split_dir.mkdir(parents=True, exist_ok=True)
        with (split_dir / "shard_00000.jsonl").open("w", encoding="utf-8") as file:
            file.write(json.dumps(make_training_graph(f"{split}-bug", True)) + "\n")
            file.write(json.dumps(make_training_graph(f"{split}-ok", False)) + "\n")


def write_embedding_artifacts(root: Path) -> None:
    """Ghi shared embedding artifacts nhỏ."""
    root.mkdir(parents=True, exist_ok=True)
    token_to_id = {
        "<PAD>": 0,
        "<UNK>": 1,
        "<MASK_NO_BUG>": 2,
        "def f(": 3,
        "x": 4,
        "return": 5,
        "y": 6,
    }
    (root / "token_to_id.json").write_text(json.dumps(token_to_id), encoding="utf-8")
    (root / "embedding_config.json").write_text(
        json.dumps({"unk_idx": 1, "embedding_dim": 8}),
        encoding="utf-8",
    )
    torch.manual_seed(7)
    embedding_weight = torch.randn(len(token_to_id), 8) * 0.02
    embedding_weight[0].zero_()
    torch.save({"embedding_weight": embedding_weight}, root / "embedding_init.pt")


class TrainingPipelineTest(unittest.TestCase):
    """Kiểm thử DataLoader, forward, loss và trainer."""

    def test_model_forward_and_loss_on_small_batch(self) -> None:
        """Model forward trả logits hợp lệ và loss hữu hạn."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            graph_root = root / "graphs"
            write_graph_shards(graph_root)
            token_to_id = {
                "<PAD>": 0,
                "<UNK>": 1,
                "<MASK_NO_BUG>": 2,
                "def f(": 3,
                "x": 4,
                "return": 5,
                "y": 6,
            }
            dataset = GraphShardDataset(graph_root, "ast_only", "train", token_to_id, unk_idx=1)
            batch = collate_graphs([next(iter(dataset)), next(iter(dataset))])
            embedding_weight = torch.randn(len(token_to_id), 8) * 0.02
            model = GGNNVariableMisuseModel(
                embedding_weight=embedding_weight,
                hidden_dim=16,
                num_edge_types=12,
                message_passing_steps=2,
                dropout=0.0,
            )

            outputs = model(batch)
            loss, loss_parts = compute_variable_misuse_loss(outputs, batch)

            self.assertTrue(torch.isfinite(loss))
            self.assertIn("localization_loss", loss_parts)
            self.assertIn("repair_loss", loss_parts)

    def test_run_training_writes_checkpoint_and_metrics(self) -> None:
        """Trainer chạy được một epoch và ghi checkpoint/metrics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            graph_root = root / "graphs"
            embedding_root = root / "embedding"
            output_root = root / "output"
            write_graph_shards(graph_root)
            write_embedding_artifacts(embedding_root)

            config = TrainingConfig(
                graph_root=graph_root,
                embedding_root=embedding_root,
                output_root=output_root,
                graph_variant="ast_only",
                batch_size=2,
                epochs=1,
                hidden_dim=16,
                message_passing_steps=1,
                dropout=0.0,
                max_train_graphs=2,
                max_dev_graphs=2,
                log_every=0,
            )
            report = run_training(config)

            self.assertEqual(len(report["history"]), 1)
            self.assertTrue((output_root / "best_model.pt").exists())
            self.assertTrue((output_root / "metrics_history.json").exists())


if __name__ == "__main__":
    unittest.main()

