from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScorecardMetric:
    dataset_name: str
    dimension: str
    score: float
    status: str
    source: str
    total_checks: int
    failed_checks: int


@dataclass(frozen=True)
class DatasetScorecard:
    dataset_name: str
    governance_score: float
    status: str
