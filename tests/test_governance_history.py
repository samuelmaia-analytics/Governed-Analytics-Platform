from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.governance_history import append_governance_history


def test_append_governance_history(tmp_path: Path) -> None:
    output = tmp_path / "governance_history.csv"
    privacy_result = {
        "score": 40,
        "risk_level": "medium",
        "summary": "",
        "score_components": {},
        "component_explanations": {},
        "publication_recommendation": "needs_review",
        "recommendations": [],
    }
    quality_result = {
        "total_rows": 10,
        "total_columns": 3,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 2,
    }
    append_governance_history(
        total_rows=10,
        total_columns=3,
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status="Needs Review",
        history_path=output,
    )
    append_governance_history(
        total_rows=10,
        total_columns=3,
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status="Needs Review",
        history_path=output,
    )
    stored = pd.read_csv(output)
    assert len(stored) == 2
    assert "run_timestamp" in stored.columns

