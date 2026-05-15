"""Tạo hình trực quan cho kết quả evaluation Variable Misuse."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from variable_misuse_gnn.evaluation.evaluator import build_model_from_checkpoint, load_checkpoint
from variable_misuse_gnn.graph.variants import GRAPH_VARIANTS
from variable_misuse_gnn.training.dataset import collate_graphs
from variable_misuse_gnn.training.embedding_artifacts import (
    load_embedding_config,
    load_embedding_payload,
    load_token_to_id,
)
from variable_misuse_gnn.utils.device import get_runtime_device
from variable_misuse_gnn.visualization import write_accuracy_chart, write_program_graph_svg

DEFAULT_EVALUATION_VARIANTS = (
    "ast_only",
    "ast_next_token",
    "ast_next_token_data_flow",
)


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh cho visualization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph-root", type=Path, default=Path("dataset/graphs"))
    parser.add_argument(
        "--embedding-root",
        type=Path,
        default=Path("dataset/embedding/shared_token_embedding_300000"),
    )
    parser.add_argument("--checkpoint-root", type=Path, default=Path("output/checkpoints"))
    parser.add_argument("--evaluation-root", type=Path, default=Path("output/evaluation"))
    parser.add_argument("--output-root", type=Path, default=Path("output/evaluation/figures"))
    parser.add_argument(
        "--graph-variant",
        choices=["all", *sorted(GRAPH_VARIANTS)],
        default="all",
    )
    parser.add_argument("--split", default="eval")
    parser.add_argument("--checkpoint-name", default="best_model.pt")
    parser.add_argument("--max-nodes", type=int, default=45)
    parser.add_argument("--example-index", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    """Tạo chart accuracy và graph prediction SVG."""
    args = parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    maybe_write_accuracy_chart(args.evaluation_root, args.output_root)

    variants = resolve_variants(args.graph_variant)
    token_to_id = load_token_to_id(args.embedding_root)
    embedding_config = load_embedding_config(args.embedding_root)
    embedding_payload = load_embedding_payload(args.embedding_root)
    embedding_weight = embedding_payload["embedding_weight"].float()
    unk_idx = int(embedding_config.get("unk_idx", token_to_id.get("<UNK>", 1)))
    device = get_runtime_device()

    for variant in variants:
        graph = load_bug_graph(
            graph_root=args.graph_root,
            graph_variant=variant,
            split=args.split,
            example_index=args.example_index,
        )
        prediction = predict_graph(
            graph=graph,
            token_to_id=token_to_id,
            unk_idx=unk_idx,
            embedding_weight=embedding_weight,
            checkpoint_path=args.checkpoint_root / variant / args.checkpoint_name,
            device=device,
        )
        graph_output_path = args.output_root / f"{variant}_prediction_graph.svg"
        write_program_graph_svg(
            graph=graph,
            prediction=prediction,
            output_path=graph_output_path,
            max_nodes=args.max_nodes,
        )
        metadata_path = args.output_root / f"{variant}_prediction_graph.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "graph_variant": variant,
                    "graph_id": graph.get("graph_id"),
                    "provenance": graph.get("provenance", {}),
                    "prediction": prediction,
                    "output_svg": graph_output_path.as_posix(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"graph visualization: {graph_output_path}")


def maybe_write_accuracy_chart(evaluation_root: Path, output_root: Path) -> None:
    """Tạo lại biểu đồ accuracy nếu đã có evaluation summary."""
    summary_path = evaluation_root / "evaluation_summary.json"
    if not summary_path.exists():
        print(f"Skip accuracy chart, chưa thấy: {summary_path}")
        return
    rows = json.loads(summary_path.read_text(encoding="utf-8"))
    chart_path = output_root / "accuracy_comparison.svg"
    write_accuracy_chart(rows, chart_path)
    print(f"accuracy chart: {chart_path}")


def resolve_variants(graph_variant: str) -> tuple[str, ...]:
    """Trả về danh sách variant cần trực quan hóa."""
    if graph_variant == "all":
        return DEFAULT_EVALUATION_VARIANTS
    return (graph_variant,)


def load_bug_graph(
    graph_root: Path,
    graph_variant: str,
    split: str,
    example_index: int,
) -> dict[str, Any]:
    """Đọc một graph có bug từ split eval để trực quan hóa."""
    graph_dir = graph_root / graph_variant / split
    if not graph_dir.exists():
        raise FileNotFoundError(f"Không thấy graph split: {graph_dir}")

    bug_seen = 0
    for shard_path in sorted(graph_dir.glob("shard_*.jsonl")):
        with shard_path.open("r", encoding="utf-8") as file:
            for line in file:
                graph = json.loads(line)
                if not graph.get("has_bug"):
                    continue
                if bug_seen == example_index:
                    return graph
                bug_seen += 1
    raise ValueError(f"Không tìm thấy bug graph index={example_index} trong {graph_dir}")


def predict_graph(
    graph: dict[str, Any],
    token_to_id: dict[str, int],
    unk_idx: int,
    embedding_weight: torch.Tensor,
    checkpoint_path: Path,
    device: torch.device,
) -> dict[str, Any]:
    """Chạy model trên một graph và trả về node prediction."""
    graph_for_batch = graph.copy()
    graph_for_batch["node_token_ids"] = [
        token_to_id.get(str(token), unk_idx) for token in graph_for_batch["node_tokens"]
    ]
    batch = collate_graphs([graph_for_batch]).to(device)
    checkpoint = load_checkpoint(checkpoint_path, device)
    model = build_model_from_checkpoint(
        embedding_weight=embedding_weight,
        checkpoint_config=checkpoint.get("config", {}),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with torch.no_grad():
        outputs = model(batch)
    node_logits = outputs["localization_logits"]
    no_bug_logits = outputs["no_bug_logits"]
    repair_logits = outputs["repair_logits"]
    assert isinstance(node_logits, torch.Tensor)
    assert isinstance(no_bug_logits, torch.Tensor)
    assert isinstance(repair_logits, list)

    localization_logits = torch.cat([node_logits, no_bug_logits[0].view(1)], dim=0)
    predicted_local = int(torch.argmax(localization_logits).detach().cpu().item())
    no_bug_index = int(graph["num_nodes"])
    predicted_localization = None if predicted_local == no_bug_index else predicted_local

    predicted_repair = None
    if repair_logits and repair_logits[0].numel() > 0:
        repair_position = int(torch.argmax(repair_logits[0]).detach().cpu().item())
        predicted_repair = int(graph["repair_candidates"][repair_position])

    return {
        "predicted_localization": predicted_localization,
        "ground_truth_localization": graph.get("localization_target"),
        "predicted_repair": predicted_repair,
        "ground_truth_repairs": graph.get("repair_targets", []),
        "checkpoint_epoch": int(checkpoint.get("epoch", -1)),
    }


if __name__ == "__main__":
    main()
