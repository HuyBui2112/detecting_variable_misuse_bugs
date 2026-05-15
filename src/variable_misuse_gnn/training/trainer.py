"""Trainer cho GGNN Variable Misuse."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader

from variable_misuse_gnn.evaluation.metrics import MetricAccumulator
from variable_misuse_gnn.models.ggnn import GGNNVariableMisuseModel
from variable_misuse_gnn.training.config import TrainingConfig
from variable_misuse_gnn.training.dataset import GraphBatch, GraphShardDataset, collate_graphs
from variable_misuse_gnn.training.embedding_artifacts import (
    load_embedding_config,
    load_embedding_payload,
    load_token_to_id,
)
from variable_misuse_gnn.training.losses import compute_variable_misuse_loss
from variable_misuse_gnn.utils.device import get_runtime_device
from variable_misuse_gnn.utils.seed import set_random_seed


def run_training(config: TrainingConfig) -> dict[str, Any]:
    """Train GGNN cho một graph variant và lưu checkpoint/metrics."""
    set_random_seed(config.seed)
    device = get_runtime_device()
    config.output_root.mkdir(parents=True, exist_ok=True)

    token_to_id = load_token_to_id(config.embedding_root)
    embedding_config = load_embedding_config(config.embedding_root)
    embedding_payload = load_embedding_payload(config.embedding_root)
    embedding_weight = embedding_payload["embedding_weight"].float()
    unk_idx = int(embedding_config.get("unk_idx", token_to_id.get("<UNK>", 1)))

    train_loader = build_loader(
        config=config,
        split=config.train_split,
        token_to_id=token_to_id,
        unk_idx=unk_idx,
        max_graphs=config.max_train_graphs,
    )
    dev_loader = build_loader(
        config=config,
        split=config.dev_split,
        token_to_id=token_to_id,
        unk_idx=unk_idx,
        max_graphs=config.max_dev_graphs,
    )

    model = GGNNVariableMisuseModel(
        embedding_weight=embedding_weight,
        hidden_dim=config.hidden_dim,
        num_edge_types=config.num_edge_types,
        message_passing_steps=config.message_passing_steps,
        dropout=config.dropout,
        freeze_embedding=config.freeze_embedding,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min" if config.monitor_metric == "loss" else "max",
        factor=config.lr_scheduler_factor,
        patience=config.lr_scheduler_patience,
    )

    start_epoch = 1
    best_monitor_score = float("inf") if config.monitor_metric == "loss" else -float("inf")
    epochs_without_improvement = 0
    history = []
    if config.resume_from_checkpoint is not None:
        start_epoch, best_monitor_score, history = load_training_checkpoint(
            config.resume_from_checkpoint,
            model,
            optimizer,
            device,
            config.monitor_metric,
        )

    stopped_early = False
    for epoch in range(start_epoch, config.epochs + 1):
        train_metrics = run_epoch(
            model=model,
            loader=train_loader,
            device=device,
            optimizer=optimizer,
            log_every=config.log_every,
            epoch=epoch,
            train=True,
        )
        dev_metrics = run_epoch(
            model=model,
            loader=dev_loader,
            device=device,
            optimizer=None,
            log_every=config.log_every,
            epoch=epoch,
            train=False,
        )
        epoch_report = {
            "epoch": epoch,
            "train": train_metrics,
            "dev": dev_metrics,
            "learning_rate": optimizer.param_groups[0]["lr"],
        }
        history.append(epoch_report)
        print(json.dumps(epoch_report, ensure_ascii=False, indent=2))

        monitor_score = compute_monitor_score(dev_metrics, config.monitor_metric)
        scheduler.step(monitor_score)
        improved = has_improved(
            monitor_score=monitor_score,
            best_score=best_monitor_score,
            monitor_metric=config.monitor_metric,
            min_delta=config.early_stopping_min_delta,
        )
        if improved:
            best_monitor_score = monitor_score
            epochs_without_improvement = 0
            save_checkpoint(
                config=config,
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                dev_metrics=dev_metrics,
                history=history,
                checkpoint_name=config.checkpoint_name,
                best_monitor_score=best_monitor_score,
            )
        else:
            epochs_without_improvement += 1

        save_checkpoint(
            config=config,
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            dev_metrics=dev_metrics,
            history=history,
            checkpoint_name=config.last_checkpoint_name,
            best_monitor_score=best_monitor_score,
        )

        write_metrics(config, history)
        if (
            config.early_stopping_patience > 0
            and epochs_without_improvement >= config.early_stopping_patience
        ):
            stopped_early = True
            print(
                "Early stopping: "
                f"metric={config.monitor_metric} "
                f"best={best_monitor_score} "
                f"patience={config.early_stopping_patience}"
            )
            break

    report = {
        "config": serialize_config(config),
        "embedding_config": embedding_config,
        "device": str(device),
        "best_monitor_score": best_monitor_score,
        "stopped_early": stopped_early,
        "history": history,
    }
    (config.output_root / "training_summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def build_loader(
    config: TrainingConfig,
    split: str,
    token_to_id: dict[str, int],
    unk_idx: int,
    max_graphs: int | None,
) -> DataLoader:
    """Tạo DataLoader streaming từ graph shards."""
    dataset = GraphShardDataset(
        graph_root=config.graph_root,
        graph_variant=config.graph_variant,
        split=split,
        token_to_id=token_to_id,
        unk_idx=unk_idx,
        max_graphs=max_graphs,
    )
    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        collate_fn=collate_graphs,
        num_workers=0,
    )


def run_epoch(
    model: GGNNVariableMisuseModel,
    loader: DataLoader,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None,
    log_every: int,
    epoch: int,
    train: bool,
) -> dict[str, float | int]:
    """Chạy một epoch train hoặc evaluation."""
    model.train(train)
    metrics = MetricAccumulator()
    for step, batch in enumerate(loader, start=1):
        assert isinstance(batch, GraphBatch)
        batch = batch.to(device)
        if optimizer is not None:
            optimizer.zero_grad(set_to_none=True)
        with torch.set_grad_enabled(train):
            outputs = model(batch)
            loss, _ = compute_variable_misuse_loss(outputs, batch)
            if optimizer is not None:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
        metrics.update_loss(float(loss.detach().cpu().item()))
        update_prediction_metrics(metrics, outputs, batch)
        if log_every > 0 and step % log_every == 0:
            phase = "train" if train else "dev"
            print(f"{phase} epoch={epoch} step={step} metrics={metrics.to_json_dict()}")
    return metrics.to_json_dict()


def update_prediction_metrics(
    metrics: MetricAccumulator,
    outputs: dict[str, torch.Tensor | list[torch.Tensor]],
    batch: GraphBatch,
) -> None:
    """Cập nhật Localization Accuracy và Repair Accuracy."""
    node_logits = outputs["localization_logits"]
    no_bug_logits = outputs["no_bug_logits"]
    repair_logits = outputs["repair_logits"]
    assert isinstance(node_logits, torch.Tensor)
    assert isinstance(no_bug_logits, torch.Tensor)
    assert isinstance(repair_logits, list)

    for graph_index, (start, end) in enumerate(zip(batch.graph_ptr[:-1], batch.graph_ptr[1:], strict=True)):
        logits = torch.cat([node_logits[start:end], no_bug_logits[graph_index].view(1)], dim=0)
        predicted_local = int(torch.argmax(logits).detach().cpu().item())
        no_bug_index = int((end - start).detach().cpu().item())
        if batch.has_bug[graph_index]:
            target_local = int((batch.localization_targets[graph_index] - start).detach().cpu().item())
        else:
            target_local = no_bug_index
        metrics.localization_total += 1
        metrics.localization_correct += int(predicted_local == target_local)

        if batch.has_bug[graph_index] and repair_logits[graph_index].numel() > 0:
            candidates = batch.candidate_indices[graph_index]
            predicted_candidate = candidates[int(torch.argmax(repair_logits[graph_index]).detach().cpu().item())]
            targets = set(int(value) for value in batch.repair_targets[graph_index].detach().cpu().tolist())
            metrics.repair_total += 1
            metrics.repair_correct += int(int(predicted_candidate.detach().cpu().item()) in targets)


def save_checkpoint(
    config: TrainingConfig,
    model: GGNNVariableMisuseModel,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    dev_metrics: dict[str, float | int],
    history: list[dict[str, Any]],
    checkpoint_name: str,
    best_monitor_score: float,
) -> None:
    """Lưu checkpoint model, optimizer và lịch sử metric."""
    checkpoint_path = config.output_root / checkpoint_name
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "dev_metrics": dev_metrics,
            "history": history,
            "best_monitor_score": best_monitor_score,
            "config": serialize_config(config),
        },
        checkpoint_path,
    )


def load_training_checkpoint(
    checkpoint_path: Path,
    model: GGNNVariableMisuseModel,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    monitor_metric: str,
) -> tuple[int, float, list[dict[str, Any]]]:
    """Load checkpoint để resume training sau khi Colab bị ngắt."""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    start_epoch = int(checkpoint["epoch"]) + 1
    history = list(checkpoint.get("history", []))
    if "best_monitor_score" in checkpoint:
        best_monitor_score = float(checkpoint["best_monitor_score"])
    else:
        dev_metrics = checkpoint.get("dev_metrics", {})
        best_monitor_score = compute_monitor_score(dev_metrics, monitor_metric)
    print(f"Resume checkpoint {checkpoint_path} from epoch {start_epoch}")
    return start_epoch, best_monitor_score, history


def write_metrics(config: TrainingConfig, history: list[dict[str, Any]]) -> None:
    """Ghi metrics sau mỗi epoch để Colab reset vẫn còn kết quả."""
    path = config.output_root / "metrics_history.json"
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def serialize_config(config: TrainingConfig) -> dict[str, Any]:
    """Chuyển TrainingConfig sang dict JSON-friendly."""
    data = config.__dict__.copy()
    for key, value in list(data.items()):
        if isinstance(value, Path):
            data[key] = value.as_posix()
    return data


def compute_monitor_score(dev_metrics: dict[str, float | int], monitor_metric: str) -> float:
    """Tính score dùng cho checkpoint, scheduler và early stopping."""
    if monitor_metric == "combined":
        return float(dev_metrics["localization_accuracy"]) + float(dev_metrics["repair_accuracy"])
    if monitor_metric == "repair_accuracy":
        return float(dev_metrics["repair_accuracy"])
    if monitor_metric == "localization_accuracy":
        return float(dev_metrics["localization_accuracy"])
    if monitor_metric == "loss":
        return float(dev_metrics["loss"])
    raise ValueError(f"Monitor metric không hỗ trợ: {monitor_metric}")


def has_improved(
    monitor_score: float,
    best_score: float,
    monitor_metric: str,
    min_delta: float,
) -> bool:
    """Kiểm tra metric hiện tại có cải thiện đủ so với best score không."""
    if monitor_metric == "loss":
        return monitor_score < best_score - min_delta
    return monitor_score > best_score + min_delta
