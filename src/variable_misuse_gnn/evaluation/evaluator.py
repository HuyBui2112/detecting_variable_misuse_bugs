"""Chạy evaluation GGNN trên split eval của Variable Misuse."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader

from variable_misuse_gnn.evaluation.config import EvaluationConfig
from variable_misuse_gnn.evaluation.metrics import MetricAccumulator, update_prediction_metrics
from variable_misuse_gnn.models.ggnn import GGNNVariableMisuseModel
from variable_misuse_gnn.training.dataset import GraphBatch, GraphShardDataset, collate_graphs
from variable_misuse_gnn.training.embedding_artifacts import (
    load_embedding_config,
    load_embedding_payload,
    load_token_to_id,
)
from variable_misuse_gnn.training.losses import compute_variable_misuse_loss
from variable_misuse_gnn.utils.device import get_runtime_device
from variable_misuse_gnn.utils.seed import set_random_seed


def run_evaluation(config: EvaluationConfig) -> dict[str, Any]:
    """Đánh giá một checkpoint trên split eval và ghi metric ra JSON."""
    set_random_seed(config.seed)
    device = get_runtime_device()
    config.output_root.mkdir(parents=True, exist_ok=True)

    token_to_id = load_token_to_id(config.embedding_root)
    embedding_config = load_embedding_config(config.embedding_root)
    embedding_payload = load_embedding_payload(config.embedding_root)
    embedding_weight = embedding_payload["embedding_weight"].float()
    unk_idx = int(embedding_config.get("unk_idx", token_to_id.get("<UNK>", 1)))

    checkpoint = load_checkpoint(config.checkpoint_path, device)
    checkpoint_config = checkpoint.get("config", {})
    model = build_model_from_checkpoint(
        embedding_weight=embedding_weight,
        checkpoint_config=checkpoint_config,
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])

    loader = build_evaluation_loader(
        config=config,
        token_to_id=token_to_id,
        unk_idx=unk_idx,
    )
    metrics = evaluate_loader(
        model=model,
        loader=loader,
        device=device,
        log_every=config.log_every,
    )
    report = {
        "graph_variant": config.graph_variant,
        "split": config.split,
        "checkpoint_path": config.checkpoint_path.as_posix(),
        "checkpoint_epoch": int(checkpoint.get("epoch", -1)),
        "checkpoint_dev_metrics": checkpoint.get("dev_metrics", {}),
        "device": str(device),
        "metrics": metrics,
        "config": serialize_config(config),
        "checkpoint_training_config": checkpoint_config,
    }
    output_path = config.output_root / "eval_metrics.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def load_checkpoint(checkpoint_path: Path, device: torch.device) -> dict[str, Any]:
    """Đọc checkpoint bằng map_location để chạy được cả CPU và GPU."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Không thấy checkpoint: {checkpoint_path}")
    try:
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    except TypeError:
        checkpoint = torch.load(checkpoint_path, map_location=device)
    if "model_state_dict" not in checkpoint:
        raise ValueError(f"Checkpoint không có model_state_dict: {checkpoint_path}")
    return checkpoint


def build_model_from_checkpoint(
    embedding_weight: torch.Tensor,
    checkpoint_config: dict[str, Any],
) -> GGNNVariableMisuseModel:
    """Khởi tạo model bằng đúng tham số kiến trúc đã lưu trong checkpoint."""
    return GGNNVariableMisuseModel(
        embedding_weight=embedding_weight,
        hidden_dim=int(checkpoint_config.get("hidden_dim", 128)),
        num_edge_types=int(checkpoint_config.get("num_edge_types", 12)),
        message_passing_steps=int(checkpoint_config.get("message_passing_steps", 4)),
        dropout=float(checkpoint_config.get("dropout", 0.1)),
        freeze_embedding=bool(checkpoint_config.get("freeze_embedding", False)),
    )


def build_evaluation_loader(
    config: EvaluationConfig,
    token_to_id: dict[str, int],
    unk_idx: int,
) -> DataLoader:
    """Tạo DataLoader streaming cho split evaluation."""
    graph_dir = config.graph_root / config.graph_variant / config.split
    if not graph_dir.exists():
        raise FileNotFoundError(f"Không thấy graph split: {graph_dir}")
    if not list(graph_dir.glob("shard_*.jsonl")):
        raise FileNotFoundError(f"Không thấy shard_*.jsonl trong: {graph_dir}")

    dataset = GraphShardDataset(
        graph_root=config.graph_root,
        graph_variant=config.graph_variant,
        split=config.split,
        token_to_id=token_to_id,
        unk_idx=unk_idx,
        max_graphs=config.max_graphs,
    )
    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        collate_fn=collate_graphs,
        num_workers=0,
    )


def evaluate_loader(
    model: GGNNVariableMisuseModel,
    loader: DataLoader,
    device: torch.device,
    log_every: int,
) -> dict[str, float | int]:
    """Chạy forward-only evaluation và tính Localization/Repair Accuracy."""
    model.eval()
    metrics = MetricAccumulator()
    with torch.no_grad():
        for step, batch in enumerate(loader, start=1):
            assert isinstance(batch, GraphBatch)
            batch = batch.to(device)
            outputs = model(batch)
            loss, _ = compute_variable_misuse_loss(outputs, batch)
            metrics.update_loss(float(loss.detach().cpu().item()))
            update_prediction_metrics(metrics, outputs, batch)
            if log_every > 0 and step % log_every == 0:
                print(f"eval step={step} metrics={metrics.to_json_dict()}")
    return metrics.to_json_dict()


def serialize_config(config: EvaluationConfig) -> dict[str, Any]:
    """Chuyển EvaluationConfig sang dict JSON-friendly."""
    data = config.__dict__.copy()
    for key, value in list(data.items()):
        if isinstance(value, Path):
            data[key] = value.as_posix()
    return data
