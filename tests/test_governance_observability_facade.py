from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.governance_observability as facade
from src.config import PUBLISHED_MONITORING_DIR
from src.observability_components.models import ObservabilityCheck


def test_historical_api_and_defaults_remain_available() -> None:
    assert facade.ObservabilityCheck is ObservabilityCheck
    assert facade.DEFAULT_GOVERNANCE_HISTORY_PATH == (
        PUBLISHED_MONITORING_DIR / "governance_history.csv"
    )
    assert facade.DEFAULT_OBSERVABILITY_PATH == (
        PUBLISHED_MONITORING_DIR / "governance_observability.json"
    )
    for name in (
        "_result",
        "_row_count_anomaly_check",
        "_null_rate_drift_check",
        "_privacy_risk_trend_check",
        "_quality_score_trend_check",
        "evaluate_governance_observability",
        "save_observability_results",
        "load_governance_history",
    ):
        assert callable(getattr(facade, name))


def test_load_wrapper_delegates_dynamically(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "history.csv"
    expected = pd.DataFrame({"value": [1]})
    received: list[Path] = []

    def fake(actual_path: Path) -> pd.DataFrame:
        received.append(actual_path)
        return expected

    monkeypatch.setattr(facade._readers, "load_governance_history", fake)

    assert facade.load_governance_history(path) is expected
    assert received == [path]


def test_save_wrapper_preserves_component_and_facade_monkeypatches(
    monkeypatch, tmp_path: Path
) -> None:
    output_path = tmp_path / "observability.json"
    checks = [ObservabilityCheck("ok", "PASS", "low", 0.0, 0.0, "ok")]
    ensure_sentinel = object()
    captured: dict[str, object] = {}

    def fake(component_checks, *, output_path, ensure_directory_fn):
        captured.update(
            checks=component_checks,
            output_path=output_path,
            ensure_directory_fn=ensure_directory_fn,
        )
        return output_path

    monkeypatch.setattr(facade, "ensure_directory", ensure_sentinel)
    monkeypatch.setattr(facade._outputs, "save_observability_results", fake)

    assert facade.save_observability_results(checks, output_path=output_path) == output_path
    assert captured == {
        "checks": checks,
        "output_path": output_path,
        "ensure_directory_fn": ensure_sentinel,
    }


def test_evaluate_wrapper_injects_historical_facade_helpers(monkeypatch) -> None:
    history = pd.DataFrame({"value": [1]})
    sentinels = {
        "result_fn": object(),
        "row_count_anomaly_check_fn": object(),
        "null_rate_drift_check_fn": object(),
        "privacy_risk_trend_check_fn": object(),
        "quality_score_trend_check_fn": object(),
    }
    for argument, sentinel in sentinels.items():
        facade_name = {
            "result_fn": "_result",
            "row_count_anomaly_check_fn": "_row_count_anomaly_check",
            "null_rate_drift_check_fn": "_null_rate_drift_check",
            "privacy_risk_trend_check_fn": "_privacy_risk_trend_check",
            "quality_score_trend_check_fn": "_quality_score_trend_check",
        }[argument]
        monkeypatch.setattr(facade, facade_name, sentinel)

    expected: list[ObservabilityCheck] = []

    def fake(**kwargs):
        assert kwargs["expected_columns"] == {"a"}
        assert kwargs["observed_columns"] == ["a"]
        assert kwargs["freshness_status"] == "fresh"
        assert kwargs["history_df"] is history
        for argument, sentinel in sentinels.items():
            assert kwargs[argument] is sentinel
        return expected

    monkeypatch.setattr(facade._pipeline, "evaluate_governance_observability", fake)

    result = facade.evaluate_governance_observability(
        expected_columns={"a"},
        observed_columns=["a"],
        freshness_status="fresh",
        history_df=history,
    )

    assert result is expected


def test_private_check_wrapper_observes_component_monkeypatch(monkeypatch) -> None:
    history = pd.DataFrame()
    expected = ObservabilityCheck("patched", "PASS", "low", 0.0, 0.0, "patched")
    monkeypatch.setattr(
        facade._checks, "row_count_anomaly_check", lambda received: expected
    )

    assert facade._row_count_anomaly_check(history) is expected
