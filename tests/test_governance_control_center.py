from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.pages.governance_control_center import save_governance_snapshot


def test_save_governance_snapshot_appends_history(tmp_path: Path) -> None:
    history_path = tmp_path / "governance_history.csv"
    df = pd.DataFrame({"id": [1, 2], "email": ["a@x.com", "b@x.com"]})
    risk_result = {
        "score": 35,
        "total_score": 35,
        "risk_level": "medium",
        "explanation": "test",
        "summary": "test",
        "components": {"personal_data_exposure": 7},
        "score_components": {"personal_data_exposure": 7},
        "per_component_points": {"personal_data_exposure": 7},
        "component_explanations": {"personal_data_exposure": "test"},
        "publication_recommendation": "needs_review",
        "recommendations": ["test"],
    }
    quality_result = {
        "total_rows": 2,
        "total_columns": 2,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 1,
    }

    first_path = save_governance_snapshot(
        df=df,
        risk_result=risk_result,
        quality_results=quality_result,
        publication_status="Needs Review",
        history_path=history_path,
    )
    second_path = save_governance_snapshot(
        df=df,
        risk_result=risk_result,
        quality_results=quality_result,
        publication_status="Needs Review",
        history_path=history_path,
    )

    stored = pd.read_csv(history_path)
    assert first_path == history_path
    assert second_path == history_path
    assert len(stored) == 2
    assert "publication_status" in stored.columns
