from __future__ import annotations

import inspect
import json
import uuid
from pathlib import Path

import pandas as pd
import pytest

import app.pages.governance_control_center as control_center
import src.governance_history as history
import src.run_platform_pipeline as platform_pipeline

HISTORY_COLUMNS = [
    "run_id",
    "dataset_name",
    "execution_timestamp",
    "row_count",
    "null_rate",
    "duplicate_rate",
    "freshness_status",
    "data_quality_score",
    "privacy_risk_score",
    "publication_status",
    "failed_rules_count",
    "warning_rules_count",
    "critical_rules_count",
    "run_timestamp",
    "total_rows",
    "total_columns",
    "privacy_score",
    "privacy_risk_level",
    "failed_checks_count",
]

DECISION_FIELDS = [
    "dataset",
    "status",
    "quality_score",
    "privacy_risk_score",
    "failed_checks",
    "timestamp_utc",
    "decision_reason",
]


def _privacy_result(score: int = 40) -> dict[str, object]:
    return {"score": score, "risk_level": "medium"}


def _quality_result() -> dict[str, object]:
    return {
        "failed_checks_count": 2,
        "duplicate_rows": 2,
        "null_pct_by_column": {"a": 10.0, "b": 0.0},
        "checks": [
            {"status": "FAIL", "severity": "high"},
            {"status": "FAIL", "severity": "medium"},
            {"status": "WARN", "severity": "critical"},
        ],
    }


def _append(tmp_path: Path, **overrides: object) -> tuple[Path, Path, Path]:
    history_path = tmp_path / "governance_history.csv"
    decision_path = tmp_path / "publication_decision.json"
    arguments: dict[str, object] = {
        "total_rows": 10,
        "total_columns": 3,
        "privacy_result": _privacy_result(),
        "quality_result": _quality_result(),
        "publication_status": "Needs Review",
        "freshness_status": "warning",
        "history_path": history_path,
        "publication_decision_path": decision_path,
    }
    arguments.update(overrides)
    returned = history.append_governance_history(**arguments)  # type: ignore[arg-type]
    return returned, history_path, decision_path


def test_public_api_and_default_paths_are_stable() -> None:
    assert history.DEFAULT_HISTORY_PATH == Path(
        "data/published/monitoring/governance_history.csv"
    ).resolve()
    assert history.DEFAULT_PUBLICATION_DECISION_PATH == Path(
        "data/published/monitoring/publication_decision.json"
    ).resolve()
    assert all(
        callable(getattr(history, name))
        for name in (
            "_compute_warning_and_critical_failures",
            "append_governance_history",
            "append_governance_history_from_dataframes",
            "save_publication_decision_artifact",
        )
    )


def test_append_creates_uuid_timestamp_exact_schema_and_returns_history_path(
    tmp_path: Path,
) -> None:
    returned, history_path, decision_path = _append(tmp_path)
    stored = pd.read_csv(history_path)

    assert returned == history_path
    assert history_path.exists() and decision_path.exists()
    assert stored.columns.tolist() == HISTORY_COLUMNS
    uuid.UUID(stored.at[0, "run_id"])
    assert pd.Timestamp(stored.at[0, "execution_timestamp"]).tzinfo is not None
    assert stored.at[0, "run_timestamp"] == stored.at[0, "execution_timestamp"]


def test_append_second_row_preserves_first_row(tmp_path: Path) -> None:
    _, history_path, decision_path = _append(tmp_path, run_id="first-run")
    first = pd.read_csv(history_path).iloc[0].to_dict()

    history.append_governance_history(
        total_rows=20,
        total_columns=4,
        privacy_result=_privacy_result(22),  # type: ignore[arg-type]
        quality_result={"failed_checks_count": 0},  # type: ignore[arg-type]
        publication_status="Approved",
        run_id="second-run",
        history_path=history_path,
        publication_decision_path=decision_path,
    )
    stored = pd.read_csv(history_path)

    assert stored.shape[0] == 2
    assert stored.iloc[0].to_dict() == first
    assert stored["run_id"].tolist() == ["first-run", "second-run"]


def test_single_append_writes_history_before_decision(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    original_writer = history.save_publication_decision_artifact
    observed: dict[str, object] = {}

    def observing_writer(**kwargs: object) -> Path:
        observed["history_exists_when_decision_starts"] = history_path.exists()
        return original_writer(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(history, "save_publication_decision_artifact", observing_writer)
    _append(
        tmp_path,
        history_path=history_path,
        publication_decision_path=decision_path,
    )

    assert observed == {"history_exists_when_decision_starts": True}
    assert history_path.exists() and decision_path.exists()


def test_history_metrics_and_failure_counts_are_frozen(tmp_path: Path) -> None:
    _, history_path, _ = _append(tmp_path)
    row = pd.read_csv(history_path).iloc[0]

    assert row["row_count"] == 10
    assert row["data_quality_score"] == 80
    assert row["privacy_risk_score"] == 40
    assert row["failed_rules_count"] == 2
    assert row["warning_rules_count"] == 1
    assert row["critical_rules_count"] == 1
    assert row["null_rate"] == 5.0
    assert row["duplicate_rate"] == 20.0
    assert row["privacy_score"] == 40


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        (
            "Approved",
            "All quality and privacy checks are within configured thresholds.",
        ),
        (
            "Needs Review",
            "One or more controls require manual review before publication.",
        ),
        (
            "Blocked",
            "Blocking governance conditions were detected and publication must be stopped.",
        ),
    ],
)
def test_publication_decision_schema_format_and_reasons(
    tmp_path: Path, status: str, reason: str
) -> None:
    path = tmp_path / f"{status}.json"
    returned = history.save_publication_decision_artifact(
        dataset_name="dados_com_acentuação",
        publication_status=status,
        data_quality_score=91,
        privacy_risk_score=22,
        failed_checks_count=3,
        timestamp_utc="2026-01-01T00:00:00+00:00",
        output_path=path,
    )
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)

    assert returned == path
    assert list(payload) == DECISION_FIELDS
    assert payload == {
        "dataset": "dados_com_acentuação",
        "status": status,
        "quality_score": 91,
        "privacy_risk_score": 22,
        "failed_checks": 3,
        "timestamp_utc": "2026-01-01T00:00:00+00:00",
        "decision_reason": reason,
    }
    assert "run_id" not in payload
    assert "  \"dataset\"" in text
    assert "acentuação" in text


def test_from_dataframes_calculates_privacy_and_delegates_all_paths(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    frame = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    classification = pd.DataFrame({"column": ["a"]})
    privacy = _privacy_result(22)
    captured: dict[str, object] = {}

    def fake_risk(value: pd.DataFrame, total_rows: int) -> dict[str, object]:
        assert value is classification
        assert total_rows == 2
        return privacy

    def fake_append(**kwargs: object) -> Path:
        captured.update(kwargs)
        return history_path

    monkeypatch.setattr(history, "calculate_privacy_risk_score", fake_risk)
    monkeypatch.setattr(history, "append_governance_history", fake_append)
    returned = history.append_governance_history_from_dataframes(
        df=frame,
        classification_df=classification,
        quality_result={"failed_checks_count": 0},  # type: ignore[arg-type]
        publication_status="Approved",
        run_id="run-test",
        freshness_status="fresh",
        history_path=history_path,
        publication_decision_path=decision_path,
    )

    assert returned == history_path
    assert captured["total_rows"] == 2
    assert captured["total_columns"] == 2
    assert captured["privacy_result"] is privacy
    assert captured["run_id"] == "run-test"
    assert captured["history_path"] == history_path
    assert captured["publication_decision_path"] == decision_path


def test_from_dataframes_propagates_risk_and_append_errors(
    tmp_path: Path, monkeypatch
) -> None:
    arguments = {
        "df": pd.DataFrame({"a": [1]}),
        "classification_df": pd.DataFrame({"column": ["a"]}),
        "quality_result": {"failed_checks_count": 0},
        "publication_status": "Approved",
        "history_path": tmp_path / "history.csv",
        "publication_decision_path": tmp_path / "decision.json",
    }
    monkeypatch.setattr(
        history,
        "calculate_privacy_risk_score",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("risk failed")),
    )
    with pytest.raises(RuntimeError, match="risk failed"):
        history.append_governance_history_from_dataframes(**arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(history, "calculate_privacy_risk_score", lambda *args, **kwargs: _privacy_result())
    monkeypatch.setattr(
        history,
        "append_governance_history",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("append failed")),
    )
    with pytest.raises(RuntimeError, match="append failed"):
        history.append_governance_history_from_dataframes(**arguments)  # type: ignore[arg-type]


def test_default_decision_path_remains_bound_when_only_history_path_is_passed() -> None:
    signature = inspect.signature(history.append_governance_history_from_dataframes)
    assert signature.parameters["history_path"].default is history.DEFAULT_HISTORY_PATH
    assert (
        signature.parameters["publication_decision_path"].default
        is history.DEFAULT_PUBLICATION_DECISION_PATH
    )


def test_control_center_custom_history_omits_decision_path(
    tmp_path: Path, monkeypatch
) -> None:
    captured: dict[str, object] = {}
    history_path = tmp_path / "history.csv"
    frame = pd.DataFrame({"a": [1]})

    def fake_append(**kwargs: object) -> Path:
        captured.update(kwargs)
        return history_path

    monkeypatch.setattr(control_center, "append_governance_history", fake_append)
    returned = control_center.save_governance_snapshot(
        df=frame,
        risk_result=_privacy_result(),  # type: ignore[arg-type]
        quality_results={"failed_checks_count": 0},  # type: ignore[arg-type]
        publication_status="Approved",
        history_path=history_path,
    )

    assert returned == history_path
    assert captured["history_path"] == history_path
    assert "publication_decision_path" not in captured


def test_pipeline_uses_direct_decision_writer_not_history_append() -> None:
    source = inspect.getsource(platform_pipeline._run_monitor_step)
    assert "save_publication_decision_artifact(" in source
    assert "append_governance_history" not in source
    assert platform_pipeline.save_publication_decision_artifact is (
        history.save_publication_decision_artifact
    )


def test_invalid_existing_history_and_history_write_errors_propagate(
    tmp_path: Path, monkeypatch
) -> None:
    invalid_history = tmp_path / "invalid.csv"
    invalid_history.write_text("", encoding="utf-8")
    with pytest.raises(pd.errors.EmptyDataError):
        _append(
            tmp_path,
            history_path=invalid_history,
            publication_decision_path=tmp_path / "decision.json",
        )

    monkeypatch.setattr(
        pd.DataFrame,
        "to_csv",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("history write failed")),
    )
    with pytest.raises(OSError, match="history write failed"):
        _append(tmp_path / "write-error")


def test_decision_failure_leaves_written_history_without_rollback(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    monkeypatch.setattr(
        history,
        "save_publication_decision_artifact",
        lambda **kwargs: (_ for _ in ()).throw(OSError("decision write failed")),
    )

    with pytest.raises(OSError, match="decision write failed"):
        _append(
            tmp_path,
            history_path=history_path,
            publication_decision_path=decision_path,
        )

    assert history_path.exists()
    assert not decision_path.exists()
    assert "run_id" in pd.read_csv(history_path).columns


def test_json_writer_failure_propagates(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "decision.json"

    def fail_write(*args: object, **kwargs: object) -> int:
        raise OSError("json write failed")

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(OSError, match="json write failed"):
        history.save_publication_decision_artifact(
            dataset_name="dataset",
            publication_status="Approved",
            data_quality_score=100,
            privacy_risk_score=0,
            failed_checks_count=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            output_path=output_path,
        )


def test_history_and_decision_lack_transversal_identity(tmp_path: Path) -> None:
    _, history_path, decision_path = _append(tmp_path, run_id="history-only-run-id")
    stored = pd.read_csv(history_path)
    decision = json.loads(decision_path.read_text(encoding="utf-8"))

    assert stored.at[0, "run_id"] == "history-only-run-id"
    assert "run_id" not in decision
    assert set(stored.columns).isdisjoint(decision.keys()) is False
