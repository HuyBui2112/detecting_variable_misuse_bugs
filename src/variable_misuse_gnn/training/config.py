"""Cấu hình training GGNN cho Variable Misuse."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    """Cấu hình điều khiển một lần train theo graph variant."""

    graph_root: Path
    embedding_root: Path
    output_root: Path
    graph_variant: str
    train_split: str = "train"
    dev_split: str = "dev"
    batch_size: int = 8
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    epochs: int = 5
    hidden_dim: int = 128
    message_passing_steps: int = 4
    dropout: float = 0.1
    max_train_graphs: int | None = None
    max_dev_graphs: int | None = None
    log_every: int = 100
    seed: int = 42
    freeze_embedding: bool = False
    num_edge_types: int = 12
    checkpoint_name: str = "best_model.pt"
    last_checkpoint_name: str = "last_model.pt"
    resume_from_checkpoint: Path | None = None
    early_stopping_patience: int = 3
    early_stopping_min_delta: float = 1e-4
    monitor_metric: str = "combined"
    lr_scheduler_patience: int = 2
    lr_scheduler_factor: float = 0.5
