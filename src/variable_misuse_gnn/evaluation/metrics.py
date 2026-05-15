"""Metric cho Variable Misuse Localization và Repair."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from variable_misuse_gnn.training.dataset import GraphBatch


@dataclass
class MetricAccumulator:
    """Tích lũy metric localization và repair trong một epoch."""

    localization_correct: int = 0
    localization_total: int = 0
    repair_correct: int = 0
    repair_total: int = 0
    loss_total: float = 0.0
    loss_steps: int = 0

    def update_loss(self, loss_value: float) -> None:
        """Cộng loss của một batch."""
        self.loss_total += loss_value
        self.loss_steps += 1

    def to_json_dict(self) -> dict[str, float | int]:
        """Chuyển metric sang dict JSON-friendly."""
        localization_accuracy = (
            self.localization_correct / self.localization_total
            if self.localization_total
            else 0.0
        )
        repair_accuracy = self.repair_correct / self.repair_total if self.repair_total else 0.0
        average_loss = self.loss_total / self.loss_steps if self.loss_steps else 0.0
        return {
            "loss": average_loss,
            "localization_correct": self.localization_correct,
            "localization_total": self.localization_total,
            "localization_accuracy": localization_accuracy,
            "repair_correct": self.repair_correct,
            "repair_total": self.repair_total,
            "repair_accuracy": repair_accuracy,
        }


def update_prediction_metrics(
    metrics: MetricAccumulator,
    outputs: dict[str, torch.Tensor | list[torch.Tensor]],
    batch: GraphBatch,
) -> None:
    """Cập nhật Localization Accuracy và Repair Accuracy từ output model."""
    node_logits = outputs["localization_logits"]
    no_bug_logits = outputs["no_bug_logits"]
    repair_logits = outputs["repair_logits"]
    assert isinstance(node_logits, torch.Tensor)
    assert isinstance(no_bug_logits, torch.Tensor)
    assert isinstance(repair_logits, list)

    for graph_index, (start, end) in enumerate(
        zip(batch.graph_ptr[:-1], batch.graph_ptr[1:], strict=True)
    ):
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
            predicted_candidate = candidates[
                int(torch.argmax(repair_logits[graph_index]).detach().cpu().item())
            ]
            targets = set(int(value) for value in batch.repair_targets[graph_index].detach().cpu().tolist())
            metrics.repair_total += 1
            metrics.repair_correct += int(int(predicted_candidate.detach().cpu().item()) in targets)
