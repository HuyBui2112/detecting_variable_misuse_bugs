"""Đánh giá Localization Accuracy và Repair Accuracy."""

from variable_misuse_gnn.evaluation.config import EvaluationConfig
from variable_misuse_gnn.evaluation.evaluator import run_evaluation

__all__ = ["EvaluationConfig", "run_evaluation"]
