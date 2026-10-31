from __future__ import annotations

from pathlib import Path

import pytest

from src.governance_history_components.pipeline import append_governance_history


def _snapshot() -> dict[str, object]:
    return {
        "dataset_name": "dashboard", "publication_status": "Approved",
        "data_quality_score": 100, "privacy_risk_score": 22,
        "failed_rules_count": 0, "execution_timestamp": "timestamp",
    }


def test_pipeline_preserves_snapshot_history_decision_order_and_arguments(
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    snapshot = _snapshot()
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    captured: dict[str, object] = {}

    def write_history(value: dict[str, object], *, history_path: Path) -> Path:
        calls.append("history")
        assert value is snapshot
        return history_path

    def write_decision(**kwargs: object) -> Path:
        calls.append("decision")
        captured.update(kwargs)
        return decision_path

    returned = append_governance_history(
        build_snapshot_fn=lambda: calls.append("snapshot") or snapshot,
        write_history_fn=write_history,
        write_decision_fn=write_decision,
        history_path=history_path,
        publication_decision_path=decision_path,
    )
    assert returned == history_path
    assert calls == ["snapshot", "history", "decision"]
    assert captured == {
        "dataset_name": "dashboard", "publication_status": "Approved",
        "data_quality_score": 100, "privacy_risk_score": 22,
        "failed_checks_count": 0, "timestamp_utc": "timestamp",
        "output_path": decision_path,
    }


def test_decision_failure_propagates_after_history_without_rollback(
    tmp_path: Path,
) -> None:
    history_path = tmp_path / "history.csv"

    def write_history(value: dict[str, object], *, history_path: Path) -> Path:
        history_path.write_text("written", encoding="utf-8")
        return history_path

    with pytest.raises(OSError, match="decision failed"):
        append_governance_history(
            build_snapshot_fn=_snapshot,
            write_history_fn=write_history,
            write_decision_fn=lambda **kwargs: (_ for _ in ()).throw(OSError("decision failed")),
            history_path=history_path,
            publication_decision_path=tmp_path / "decision.json",
        )
    assert history_path.read_text(encoding="utf-8") == "written"


@pytest.mark.parametrize("step", ["snapshot", "history"])
def test_earlier_failures_stop_pipeline(step: str, tmp_path: Path) -> None:
    calls: list[str] = []
    def fail(*args: object, **kwargs: object):
        calls.append(step)
        raise RuntimeError(step)
    with pytest.raises(RuntimeError, match=step):
        append_governance_history(
            build_snapshot_fn=fail if step == "snapshot" else _snapshot,
            write_history_fn=fail if step == "history" else lambda value, **kwargs: tmp_path / "h.csv",
            write_decision_fn=lambda **kwargs: calls.append("decision") or tmp_path / "d.json",
            history_path=tmp_path / "h.csv", publication_decision_path=tmp_path / "d.json",
        )
    assert "decision" not in calls

