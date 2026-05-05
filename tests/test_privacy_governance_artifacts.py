from __future__ import annotations

import pandas as pd

from src.privacy_governance_artifacts import (
    build_risk_matrix,
    build_treatment_inventory,
    generate_ripd_markdown,
)


def _risk_result(level: str = "medium", score: int = 55) -> dict[str, object]:
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
        "publication_recommendation": "needs_review",
        "recommendations": ["test"],
    }


def _quality_result(failed_checks: int = 1) -> dict[str, object]:
    return {
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
        "failed_checks_count": failed_checks,
    }


def test_build_treatment_inventory_contains_expected_fields() -> None:
    inventory = build_treatment_inventory()
    assert not inventory.empty
    assert "legal_basis" in inventory.columns
    assert "retention_policy" in inventory.columns
    assert "controller" in inventory.columns
    assert "operator" in inventory.columns
    assert "dpo" in inventory.columns


def test_build_risk_matrix_returns_risks_with_severity() -> None:
    classification_df = pd.DataFrame(
        {
            "column_name": ["cpf", "zip_code", "amount"],
            "lgpd_classification": ["personal_data", "indirect_identifier", "non_personal"],
        }
    )
    risk_matrix = build_risk_matrix(classification_df, _risk_result("high", 85), _quality_result(2))
    assert len(risk_matrix) >= 3
    assert {"risk_id", "severity", "mitigation", "evidence"}.issubset(risk_matrix.columns)


def test_generate_ripd_markdown_includes_key_sections() -> None:
    classification_df = pd.DataFrame(
        {"column_name": ["email"], "lgpd_classification": ["personal_data"]}
    )
    inventory = build_treatment_inventory()
    risk_matrix = build_risk_matrix(classification_df, _risk_result(), _quality_result())
    markdown = generate_ripd_markdown(
        dataset_name="fact_orders_dashboard",
        treatment_inventory=inventory,
        risk_matrix=risk_matrix,
        risk_result=_risk_result(),
        quality_result=_quality_result(),
    )
    assert "Mini RIPD (LGPD-inspired)" in markdown
    assert "Inventário de Tratamento" in markdown
    assert "Matriz de Risco" in markdown
