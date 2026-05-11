from __future__ import annotations

import pandas as pd

from app.pages.governance_control_center import build_publication_decision_rationale


def _risk_result(level: str, score: int) -> dict[str, object]:
    return {
        "score": score,
        "total_score": score,
        "risk_level": level,
        "explanation": "test",
        "summary": "test",
        "components": {},
        "score_components": {},
        "per_component_points": {},
        "component_explanations": {},
        "publication_recommendation": "approved",
        "recommendations": ["Mask direct identifiers."],
    }


def _quality_result(failed_checks: int) -> dict[str, object]:
    return {
        "total_rows": 10,
        "total_columns": 2,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": failed_checks,
    }


def test_publication_decision_blocked_for_high_risk() -> None:
    classification_df = pd.DataFrame(
        {"lgpd_classification": ["sensitive_personal_data", "personal_data"]}
    )
    status, reasons, actions, evidence = build_publication_decision_rationale(
        _risk_result("high", 90),
        _quality_result(0),
        classification_df,
    )
    assert status == "Blocked"
    assert reasons
    assert actions
    assert evidence


def test_publication_decision_needs_review_for_failed_quality_checks() -> None:
    classification_df = pd.DataFrame({"lgpd_classification": ["non_personal"]})
    status, _, actions, _ = build_publication_decision_rationale(
        _risk_result("low", 10),
        _quality_result(2),
        classification_df,
    )
    assert status == "Needs Review"
    assert any("quality checks" in action.lower() for action in actions)
