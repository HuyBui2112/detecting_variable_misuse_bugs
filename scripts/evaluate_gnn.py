"""Evaluate GGNN Variable Misuse checkpoints trên split eval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from variable_misuse_gnn.evaluation import EvaluationConfig, run_evaluation
from variable_misuse_gnn.graph.variants import GRAPH_VARIANTS
from variable_misuse_gnn.visualization import write_accuracy_chart

DEFAULT_EVALUATION_VARIANTS = (
    "ast_only",
    "ast_next_token",
    "ast_next_token_data_flow",
)


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh cho evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graph-root",
        type=Path,
        default=Path("dataset/graphs"),
        help="Thư mục chứa graph shards theo variant.",
    )
    parser.add_argument(
        "--embedding-root",
        type=Path,
        default=Path("dataset/embedding/shared_token_embedding_300000"),
        help="Thư mục chứa shared embedding artifacts.",
    )
    parser.add_argument(
        "--checkpoint-root",
        type=Path,
        default=Path("output/checkpoints"),
        help="Thư mục chứa checkpoint theo graph variant.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/evaluation"),
        help="Thư mục lưu kết quả evaluation.",
    )
    parser.add_argument(
        "--graph-variant",
        choices=["all", *sorted(GRAPH_VARIANTS)],
        default="all",
        help="Graph variant cần evaluate, hoặc all cho ba variant chính.",
    )
    parser.add_argument("--split", default="eval", help="Split cần đánh giá.")
    parser.add_argument("--checkpoint-name", default="best_model.pt")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-graphs", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    """Chạy evaluation và ghi bảng so sánh kết quả."""
    args = parse_args()
    variants = resolve_variants(args.graph_variant)
    reports = []
    for variant in variants:
        checkpoint_path = args.checkpoint_root / variant / args.checkpoint_name
        variant_output_root = args.output_root / variant
        config = EvaluationConfig(
            graph_root=args.graph_root,
            embedding_root=args.embedding_root,
            checkpoint_path=checkpoint_path,
            output_root=variant_output_root,
            graph_variant=variant,
            split=args.split,
            batch_size=args.batch_size,
            max_graphs=args.max_graphs,
            log_every=args.log_every,
            seed=args.seed,
        )
        report = run_evaluation(config)
        reports.append(report)
        print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
        print(f"evaluation output: {variant_output_root}")

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_summary_files(args.output_root, reports)


def resolve_variants(graph_variant: str) -> tuple[str, ...]:
    """Trả về danh sách variant cần evaluate."""
    if graph_variant == "all":
        return DEFAULT_EVALUATION_VARIANTS
    return (graph_variant,)


def write_summary_files(output_root: Path, reports: list[dict[str, Any]]) -> None:
    """Ghi JSON và Markdown summary để đưa vào báo cáo."""
    rows = []
    for report in reports:
        metrics = report["metrics"]
        rows.append(
            {
                "graph_variant": report["graph_variant"],
                "split": report["split"],
                "checkpoint_epoch": report["checkpoint_epoch"],
                "loss": metrics["loss"],
                "localization_accuracy": metrics["localization_accuracy"],
                "repair_accuracy": metrics["repair_accuracy"],
                "localization_correct": metrics["localization_correct"],
                "localization_total": metrics["localization_total"],
                "repair_correct": metrics["repair_correct"],
                "repair_total": metrics["repair_total"],
            }
        )

    (output_root / "evaluation_summary.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_root / "evaluation_summary.md").write_text(
        build_markdown_table(rows),
        encoding="utf-8",
    )
    write_accuracy_chart(rows, output_root / "figures" / "accuracy_comparison.svg")


def build_markdown_table(rows: list[dict[str, Any]]) -> str:
    """Tạo bảng Markdown so sánh Localization Accuracy và Repair Accuracy."""
    lines = [
        "| Model / Graph Variant | Split | Checkpoint Epoch | Loss | Localization Accuracy | Repair Accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['graph_variant']} | "
            f"{row['split']} | "
            f"{row['checkpoint_epoch']} | "
            f"{float(row['loss']):.4f} | "
            f"{float(row['localization_accuracy']):.4f} | "
            f"{float(row['repair_accuracy']):.4f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
