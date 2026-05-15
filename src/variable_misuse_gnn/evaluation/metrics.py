"""Metric cho Variable Misuse Localization và Repair."""

from __future__ import annotations

from dataclasses import dataclass


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

