"""Train GGNN Variable Misuse cho một graph variant."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from variable_misuse_gnn.training.config import TrainingConfig
from variable_misuse_gnn.training.trainer import run_training
from variable_misuse_gnn.graph.variants import GRAPH_VARIANTS


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh cho training trên Colab."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graph-root",
        type=Path,
        required=True,
        help="Thư mục chứa graph shards theo variant.",
    )
    parser.add_argument(
        "--embedding-root",
        type=Path,
        required=True,
        help="Thư mục chứa shared embedding artifacts.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Thư mục lưu checkpoint và metrics.",
    )
    parser.add_argument(
        "--graph-variant",
        choices=sorted(GRAPH_VARIANTS),
        required=True,
        help="Graph variant cần train.",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--message-passing-steps", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--max-train-graphs", type=int, default=None)
    parser.add_argument("--max-dev-graphs", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--freeze-embedding", action="store_true")
    parser.add_argument("--resume-from-checkpoint", type=Path, default=None)
    parser.add_argument("--early-stopping-patience", type=int, default=3)
    parser.add_argument("--early-stopping-min-delta", type=float, default=1e-4)
    parser.add_argument(
        "--monitor-metric",
        choices=["combined", "repair_accuracy", "localization_accuracy", "loss"],
        default="combined",
    )
    parser.add_argument("--lr-scheduler-patience", type=int, default=2)
    parser.add_argument("--lr-scheduler-factor", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    """Khởi chạy training và in summary cuối."""
    args = parse_args()
    output_root = args.output_root / args.graph_variant
    config = TrainingConfig(
        graph_root=args.graph_root,
        embedding_root=args.embedding_root,
        output_root=output_root,
        graph_variant=args.graph_variant,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        epochs=args.epochs,
        hidden_dim=args.hidden_dim,
        message_passing_steps=args.message_passing_steps,
        dropout=args.dropout,
        max_train_graphs=args.max_train_graphs,
        max_dev_graphs=args.max_dev_graphs,
        log_every=args.log_every,
        seed=args.seed,
        freeze_embedding=args.freeze_embedding,
        resume_from_checkpoint=args.resume_from_checkpoint,
        early_stopping_patience=args.early_stopping_patience,
        early_stopping_min_delta=args.early_stopping_min_delta,
        monitor_metric=args.monitor_metric,
        lr_scheduler_patience=args.lr_scheduler_patience,
        lr_scheduler_factor=args.lr_scheduler_factor,
    )
    report = run_training(config)
    print(json.dumps(report["history"][-1], ensure_ascii=False, indent=2))
    print(f"training output: {output_root}")


if __name__ == "__main__":
    main()
