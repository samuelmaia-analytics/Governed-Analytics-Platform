from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data_quality import generate_data_quality_table
from src.lgpd_classifier import classify_dataframe_columns
from src.risk_scoring import calculate_privacy_risk_score


def _load_contract(contract_name: str) -> dict[str, object]:
    path = Path("contracts/governance") / contract_name
    return json.loads(path.read_text(encoding="utf-8"))


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_email": ["ana@example.com", "bruno@example.com"],
            "cpf": ["123.456.789-09", "987.654.321-00"],
            "revenue": [100.0, 200.0],
            "status": ["completed", "completed"],
        }
    )


def test_lgpd_classification_output_conforms_to_contract() -> None:
    contract = _load_contract("lgpd_classification_schema.json")
    required_columns = set(contract["required_columns"])
    enum_constraints = contract["enum_constraints"]

    result = classify_dataframe_columns(_sample_df())
    assert required_columns.issubset(set(result.columns))
    assert set(result["lgpd_classification"]).issubset(set(enum_constraints["lgpd_classification"]))
    assert set(result["risk_level"]).issubset(set(enum_constraints["risk_level"]))
    assert set(result["recommended_action"]).issubset(set(enum_constraints["recommended_action"]))


def test_data_quality_output_conforms_to_contract() -> None:
    contract = _load_contract("data_quality_checks_schema.json")
    required_columns = set(contract["required_columns"])
    enum_constraints = contract["enum_constraints"]

    table = generate_data_quality_table(_sample_df())
    assert required_columns.issubset(set(table.columns))
    assert set(table["status"]).issubset(set(enum_constraints["status"]))
    assert set(table["severity"]).issubset(set(enum_constraints["severity"]))
    assert int(table["affected_rows"].min()) >= 0


def test_privacy_risk_output_conforms_to_contract() -> None:
    contract = _load_contract("privacy_risk_score_schema.json")
    required_fields = set(contract["required_fields"])
    allowed_risk_levels = set(contract["field_constraints"]["risk_level"]["allowed"])

    classification_df = classify_dataframe_columns(_sample_df())
    risk = calculate_privacy_risk_score(classification_df, total_rows=2)

    assert required_fields.issubset(set(risk.keys()))
    assert 0 <= risk["score"] <= 100
    assert risk["risk_level"] in allowed_risk_levels
    assert isinstance(risk["recommendations"], list)
    assert len(risk["recommendations"]) >= 1
