from __future__ import annotations

from collections.abc import Callable

from src.scorecard_components.models import DatasetScorecard, ScorecardMetric


def run_scorecards(*, build_metrics_fn: Callable[[], list[ScorecardMetric]], build_dataset_scorecards_fn: Callable[[list[ScorecardMetric]], list[DatasetScorecard]], save_outputs_fn: Callable[[list[ScorecardMetric], list[DatasetScorecard]], object], save_report_fn: Callable[[list[ScorecardMetric], list[DatasetScorecard]], object]) -> tuple[list[ScorecardMetric], list[DatasetScorecard]]:
    metrics = build_metrics_fn()
    scorecards = build_dataset_scorecards_fn(metrics)
    save_outputs_fn(metrics, scorecards)
    save_report_fn(metrics, scorecards)
    return metrics, scorecards
