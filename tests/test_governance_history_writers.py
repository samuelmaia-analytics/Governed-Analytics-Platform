from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.governance_history_components.decision_writer import (
    save_publication_decision_artifact,
)
from src.governance_history_components.history_writer import append_history


def test_history_writer_first_write_append_and_return(tmp_path: Path) -> None:
    path = tmp_path / "history.csv"
    first = {"run_id": "one", "score": 100}
    second = {"run_id": "two", "score": 90}
    assert append_history(first, history_path=path) == path
    append_history(second, history_path=path)
    assert pd.read_csv(path).to_dict("records") == [first, second]


def test_history_writer_preserves_invalid_csv_and_write_errors(
    tmp_path: Path, monkeypatch
) -> None:
    path = tmp_path / "history.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(pd.errors.EmptyDataError):
        append_history({"run_id": "one"}, history_path=path)

    monkeypatch.setattr(
        pd.DataFrame,
        "to_csv",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("csv failed")),
    )
    with pytest.raises(OSError, match="csv failed"):
        append_history({"run_id": "one"}, history_path=tmp_path / "new.csv")


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("Approved", "All quality and privacy checks are within configured thresholds."),
        ("Needs Review", "One or more controls require manual review before publication."),
        ("Blocked", "Blocking governance conditions were detected and publication must be stopped."),
    ],
)
def test_decision_writer_preserves_schema_reasons_and_no_run_id(
    tmp_path: Path, status: str, reason: str
) -> None:
    path = tmp_path / f"{status}.json"
    returned = save_publication_decision_artifact(
        dataset_name="dados_com_acentuação", publication_status=status,
        data_quality_score=90, privacy_risk_score=22, failed_checks_count=1,
        timestamp_utc="2026-01-01T00:00:00+00:00", output_path=path,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert returned == path
    assert list(payload) == ["dataset", "status", "quality_score", "privacy_risk_score", "failed_checks", "timestamp_utc", "decision_reason"]
    assert payload["decision_reason"] == reason
    assert "run_id" not in payload
    assert "acentuação" in path.read_text(encoding="utf-8")
