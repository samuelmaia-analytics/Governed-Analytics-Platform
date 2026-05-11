from __future__ import annotations

import pandas as pd

from src.risk_scoring import calculate_privacy_risk_score


def test_returns_score_between_0_and_100() -> None:
    classification_df = pd.DataFrame(
        {
            "column_name": ["customer_email", "revenue"],
            "lgpd_classification": ["personal_data", "non_personal"],
        }
    )
    result = calculate_privacy_risk_score(classification_df, total_rows=1000)
    assert 0 <= result["score"] <= 100
    assert result["total_score"] == result["score"]
    assert result["components"] == result["score_components"]
    assert result["per_component_points"] == result["score_components"]
    assert result["explanation"]
    assert "score_components" in result
    assert "publication_recommendation" in result


def test_classifies_high_risk_with_many_personal_identifiers() -> None:
    classification_df = pd.DataFrame(
        {
            "column_name": [
                "customer_email",
                "cpf",
                "customer_name",
                "health_status",
                "phone",
            ],
            "lgpd_classification": [
                "personal_data",
                "personal_data",
                "personal_data",
                "sensitive_personal_data",
                "personal_data",
            ],
        }
    )
    result = calculate_privacy_risk_score(classification_df, total_rows=250_000)
    assert result["risk_level"] == "high"


def test_classifies_low_risk_without_personal_data() -> None:
    classification_df = pd.DataFrame(
        {
            "column_name": ["revenue", "status", "state"],
            "lgpd_classification": ["non_personal", "non_personal", "non_personal"],
        }
    )
    result = calculate_privacy_risk_score(classification_df, total_rows=500)
    assert result["risk_level"] == "low"


def test_classifies_medium_risk() -> None:
    classification_df = pd.DataFrame(
        {
            "column_name": ["email", "state", "customer_id"],
            "lgpd_classification": [
                "personal_data",
                "indirect_identifier",
                "indirect_identifier",
            ],
        }
    )
    result = calculate_privacy_risk_score(classification_df, total_rows=50_000)
    assert result["risk_level"] == "medium"
