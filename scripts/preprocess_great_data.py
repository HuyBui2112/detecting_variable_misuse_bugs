"""Chạy tiền xử lý GREAT Variable-Misuse dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from variable_misuse_gnn.data.preprocessing import PreprocessingConfig, run_preprocessing


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh cho preprocessing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("dataset/interim/great_sample_subset"),
        help="Thư mục chứa raw split hoặc subset JSONL.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("dataset/processed/great_subset"),
        help="Thư mục ghi JSONL đã tiền xử lý.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("dataset/processed/great_subset/preprocessing_summary.json"),
        help="File JSON ghi báo cáo tiền xử lý.",
    )
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--max-edges", type=int, default=4096)
    parser.add_argument("--min-repair-candidates", type=int, default=2)
    parser.add_argument("--max-samples-per-class", type=int, default=None)
    parser.add_argument("--no-balance", action="store_true")
    parser.add_argument("--drop-duplicates", action="store_true")
    parser.add_argument("--drop-control-flow", action="store_true")
    parser.add_argument("--no-linear-next-token", action="store_true")
    parser.add_argument("--output-format", choices=["compact", "full"], default="compact")
    parser.add_argument("--no-provenance", action="store_true")
    return parser.parse_args()


def main() -> None:
    """Khởi chạy preprocessing và in tóm tắt ngắn."""
    args = parse_args()
    config = PreprocessingConfig(
        input_root=args.input_root,
        output_root=args.output_root,
        report_path=args.report_path,
        max_tokens=args.max_tokens,
        max_edges=args.max_edges,
        min_repair_candidates=args.min_repair_candidates,
        balance_classes=not args.no_balance,
        max_samples_per_class=args.max_samples_per_class,
        drop_duplicate_tokens_within_split=args.drop_duplicates,
        keep_control_flow_edges=not args.drop_control_flow,
        include_linear_next_token_edges=not args.no_linear_next_token,
        output_format=args.output_format,
        include_provenance=not args.no_provenance,
    )
    report = run_preprocessing(config)
    print(json.dumps(report["aggregate"], ensure_ascii=False, indent=2))
    print(f"preprocessing report: {config.report_path}")


if __name__ == "__main__":
    main()
