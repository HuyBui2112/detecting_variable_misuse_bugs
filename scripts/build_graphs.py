"""Xây dựng Program Graph từ dữ liệu GREAT compact đã tiền xử lý."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.pipeline import run_graph_construction
from variable_misuse_gnn.graph.variants import GRAPH_VARIANTS


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh cho graph construction."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("dataset/processed/great_colab"),
        help="Thư mục chứa train/dev/eval JSONL compact.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("dataset/graphs/great_colab"),
        help="Thư mục ghi graph shard và report.",
    )
    parser.add_argument(
        "--graph-variant",
        choices=sorted(GRAPH_VARIANTS),
        default="ast_next_token_data_flow",
        help="Graph variant cần xây dựng.",
    )
    parser.add_argument(
        "--splits",
        default="train,dev,eval",
        help="Danh sách split phân tách bằng dấu phẩy.",
    )
    parser.add_argument("--max-samples-per-split", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=50000)
    parser.add_argument("--no-inverse-edges", action="store_true")
    parser.add_argument("--add-self-loops", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    """Khởi chạy graph construction và in tóm tắt aggregate."""
    args = parse_args()
    splits = tuple(split.strip() for split in args.splits.split(",") if split.strip())
    config = GraphConstructionConfig(
        input_root=args.input_root,
        output_root=args.output_root,
        graph_variant=args.graph_variant,
        splits=splits,
        add_inverse_edges=not args.no_inverse_edges,
        add_self_loops=args.add_self_loops,
        max_samples_per_split=args.max_samples_per_split,
        shard_size=args.shard_size,
        dry_run=args.dry_run,
    )
    report = run_graph_construction(config)
    print(json.dumps(report["aggregate"], ensure_ascii=False, indent=2))
    print(
        "graph construction report: "
        f"{config.output_root / config.graph_variant / 'graph_construction_summary.json'}"
    )


if __name__ == "__main__":
    main()

