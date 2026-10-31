from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd

import src.governance_history as facade


def test_public_api_and_bound_defaults_remain_available() -> None:
    assert all(callable(getattr(facade, name)) for name in ("_compute_warning_and_critical_failures", "append_governance_history", "append_governance_history_from_dataframes", "save_publication_decision_artifact"))
    signature = inspect.signature(facade.append_governance_history)
    assert signature.parameters["history_path"].default is facade.DEFAULT_HISTORY_PATH
    assert signature.parameters["publication_decision_path"].default is facade.DEFAULT_PUBLICATION_DECISION_PATH


def test_helper_and_decision_writer_delegate_dynamically(tmp_path: Path, monkeypatch) -> None:
    observed: dict[str, object] = {}
    monkeypatch.setattr(facade._metrics, "compute_warning_and_critical_failures", lambda value: (7, 8))
    monkeypatch.setattr(facade._decision_writer, "save_publication_decision_artifact", lambda **kwargs: observed.update(kwargs) or kwargs["output_path"])
    assert facade._compute_warning_and_critical_failures({}) == (7, 8)  # type: ignore[arg-type]
    path = tmp_path / "decision.json"
    assert facade.save_publication_decision_artifact(dataset_name="d", publication_status="Approved", data_quality_score=100, privacy_risk_score=0, failed_checks_count=0, timestamp_utc="t", output_path=path) == path
    assert observed["output_path"] == path


def test_append_wrapper_injects_facade_decision_writer_for_historical_monkeypatch(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    calls: list[str] = []
    monkeypatch.setattr(facade, "save_publication_decision_artifact", lambda **kwargs: calls.append("decision") or decision_path)
    returned = facade.append_governance_history(
        total_rows=1, total_columns=1,
        privacy_result={"score": 0, "risk_level": "low"},  # type: ignore[arg-type]
        quality_result={"failed_checks_count": 0},  # type: ignore[arg-type]
        publication_status="Approved", history_path=history_path,
        publication_decision_path=decision_path,
    )
    assert returned == history_path
    assert calls == ["decision"]


def test_dataframe_wrapper_preserves_historical_append_monkeypatch(
    tmp_path: Path, monkeypatch
) -> None:
    captured: dict[str, object] = {}
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    monkeypatch.setattr(facade, "calculate_privacy_risk_score", lambda value, total_rows: {"score": 22, "risk_level": "low"})
    monkeypatch.setattr(facade, "append_governance_history", lambda **kwargs: captured.update(kwargs) or history_path)
    returned = facade.append_governance_history_from_dataframes(
        df=pd.DataFrame({"a": [1]}), classification_df=pd.DataFrame({"column": ["a"]}),
        quality_result={"failed_checks_count": 0}, publication_status="Approved",  # type: ignore[arg-type]
        history_path=history_path, publication_decision_path=decision_path,
    )
    assert returned == history_path
    assert captured["history_path"] == history_path
    assert captured["publication_decision_path"] == decision_path
