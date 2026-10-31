from __future__ import annotations

import pytest

from src.scorecard_components.models import DatasetScorecard, ScorecardMetric
from src.scorecard_components.pipeline import run_scorecards


def test_pipeline_preserves_order_identity_and_return() -> None:
    calls: list[str] = []
    metrics = [ScorecardMetric("d", "q", 100, "healthy", "x", 1, 0)]
    cards = [DatasetScorecard("d", 100, "healthy")]
    result = run_scorecards(
        build_metrics_fn=lambda: calls.append("metrics") or metrics,
        build_dataset_scorecards_fn=lambda value: calls.append("cards") or (cards if value is metrics else []),
        save_outputs_fn=lambda m, c: calls.append("outputs") if m is metrics and c is cards else None,
        save_report_fn=lambda m, c: calls.append("report") if m is metrics and c is cards else None,
    )
    assert result == (metrics, cards)
    assert calls == ["metrics", "cards", "outputs", "report"]


@pytest.mark.parametrize("step", ["metrics", "cards", "outputs", "report"])
def test_pipeline_propagates_errors_and_stops(step: str) -> None:
    calls: list[str] = []
    metrics: list[ScorecardMetric] = []
    cards: list[DatasetScorecard] = []
    def action(name: str, value: object):
        def run(*args: object):
            calls.append(name)
            if name == step:
                raise RuntimeError(name)
            return value
        return run
    with pytest.raises(RuntimeError, match=step):
        run_scorecards(build_metrics_fn=action("metrics", metrics), build_dataset_scorecards_fn=action("cards", cards), save_outputs_fn=action("outputs", None), save_report_fn=action("report", None))  # type: ignore[arg-type]
    assert calls[-1] == step
