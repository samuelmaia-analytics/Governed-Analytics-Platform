from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

import src.published_monitoring as facade
from src.monitoring_components.models import AlertDispatchResult, MonitoringCheckResult


def test_facade_reexports_canonical_models_and_historical_api() -> None:
    assert facade.MonitoringCheckResult is MonitoringCheckResult
    assert facade.AlertDispatchResult is AlertDispatchResult
    names = {
        "build_result",
        "load_published_table",
        "check_file_freshness",
        "check_expected_schema",
        "check_primary_key_duplicates",
        "check_row_volume",
        "check_critical_nulls",
        "check_semantic_coverage",
        "run_monitoring",
        "build_alert_payload",
        "send_external_alert",
        "save_results",
        "render_report",
        "save_report",
        "parse_args",
        "main",
    }
    assert all(callable(getattr(facade, name)) for name in names)


def test_check_and_output_wrappers_delegate_dynamically(tmp_path: Path, monkeypatch) -> None:
    frame = pd.DataFrame({"a": [1]})
    expected = MonitoringCheckResult("schema", "PASS", 0, 0, "high", "ok")
    observed: dict[str, object] = {}

    monkeypatch.setattr(
        facade._checks,
        "check_expected_schema",
        lambda value, **kwargs: observed.update(frame=value, **kwargs) or expected,
    )
    monkeypatch.setattr(
        facade._outputs,
        "save_results",
        lambda results, **kwargs: observed.update(results=results, **kwargs)
        or (tmp_path / "a.csv", tmp_path / "a.json"),
    )
    monkeypatch.setattr(facade, "PUBLISHED_MONITORING_DIR", tmp_path)
    monkeypatch.setattr(facade, "RESULTS_PATH", tmp_path / "a.csv")
    monkeypatch.setattr(facade, "SUMMARY_PATH", tmp_path / "a.json")

    assert facade.check_expected_schema(frame) is expected
    assert facade.save_results([expected]) == (tmp_path / "a.csv", tmp_path / "a.json")
    assert observed["frame"] is frame
    assert observed["expected_columns"] is facade.EXPECTED_COLUMNS
    assert observed["monitoring_dir"] == tmp_path


def test_run_wrapper_passes_historic_facade_functions(monkeypatch) -> None:
    captured: dict[str, object] = {}
    expected = [MonitoringCheckResult("check", "PASS", 0, 0, "high", "ok")]

    def fake_pipeline(**kwargs: object) -> list[MonitoringCheckResult]:
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(facade._pipeline, "run_monitoring", fake_pipeline)

    assert facade.run_monitoring(max_freshness_hours=17) is expected
    assert captured == {
        "max_freshness_hours": 17,
        "published_path": facade.PUBLISHED_PARQUET_PATH,
        "load_published_table_fn": facade.load_published_table,
        "check_file_freshness_fn": facade.check_file_freshness,
        "check_expected_schema_fn": facade.check_expected_schema,
        "check_primary_key_duplicates_fn": facade.check_primary_key_duplicates,
        "check_row_volume_fn": facade.check_row_volume,
        "check_critical_nulls_fn": facade.check_critical_nulls,
        "check_semantic_coverage_fn": facade.check_semantic_coverage,
    }


def test_historical_monkeypatches_on_facade_are_observed(monkeypatch) -> None:
    calls: list[str] = []
    frame = pd.DataFrame({"a": [1]})

    monkeypatch.setattr(facade, "load_published_table", lambda: calls.append("load") or frame)
    monkeypatch.setattr(
        facade,
        "check_file_freshness",
        lambda *args, **kwargs: calls.append("freshness") or MonitoringCheckResult("f", "PASS", 0, 0, "high", ""),
    )
    for name in (
        "check_expected_schema",
        "check_primary_key_duplicates",
        "check_row_volume",
    ):
        monkeypatch.setattr(
            facade,
            name,
            lambda value, name=name: calls.append(name)
            or MonitoringCheckResult(name, "PASS", 0, 0, "high", ""),
        )
    monkeypatch.setattr(
        facade, "check_critical_nulls", lambda value: calls.append("nulls") or []
    )
    monkeypatch.setattr(
        facade, "check_semantic_coverage", lambda value: calls.append("semantic") or []
    )

    facade.run_monitoring()
    assert calls == [
        "load",
        "freshness",
        "check_expected_schema",
        "check_primary_key_duplicates",
        "check_row_volume",
        "nulls",
        "semantic",
    ]


def test_main_without_webhook_never_calls_http(monkeypatch) -> None:
    failed = [MonitoringCheckResult("failed", "FAIL", 1, 0, "high", "broken")]
    calls: list[str] = []
    args = Namespace(
        max_freshness_hours=36,
        fail_on_alert=False,
        alert_webhook_url="",
        alert_webhook_token="",
        alert_environment="prod",
    )
    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(facade, "parse_args", lambda: args)
    monkeypatch.setattr(facade, "run_monitoring", lambda **kwargs: failed)
    monkeypatch.setattr(facade, "save_results", lambda results: calls.append("results"))
    monkeypatch.setattr(facade, "save_report", lambda results: calls.append("report"))
    monkeypatch.setattr(
        facade, "send_external_alert", lambda *args, **kwargs: calls.append("http")
    )

    facade.main()
    assert calls == ["results", "report"]


def test_main_preserves_fail_on_alert_exit_code(monkeypatch) -> None:
    failed = [MonitoringCheckResult("failed", "FAIL", 1, 0, "high", "broken")]
    args = Namespace(
        max_freshness_hours=36,
        fail_on_alert=True,
        alert_webhook_url="",
        alert_webhook_token="",
        alert_environment="prod",
    )
    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(facade, "parse_args", lambda: args)
    monkeypatch.setattr(facade, "run_monitoring", lambda **kwargs: failed)
    monkeypatch.setattr(facade, "save_results", lambda results: None)
    monkeypatch.setattr(facade, "save_report", lambda results: None)

    with pytest.raises(SystemExit) as error:
        facade.main()
    assert error.value.code == 1
