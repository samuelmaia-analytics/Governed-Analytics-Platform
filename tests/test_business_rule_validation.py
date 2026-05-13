from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import src.business_rule_validation as bv
from src.business_rule_validation import run_business_rules


def build_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "price": [10.0, -1.0],
            "freight_value": [2.0, 3.0],
            "order_status": ["delivered", "unknown"],
            "order_delivered_customer_date": [pd.Timestamp("2020-01-02"), pd.NaT],
            "order_purchase_timestamp": [
                pd.Timestamp("2020-01-01"),
                pd.Timestamp("2020-01-03"),
            ],
        }
    )


def _valid_contract(rules: list) -> dict:
    return {
        "contract_id": "x",
        "version": 1,
        "dataset_name": "fact_orders_enriched",
        "owner": "owner",
        "rules": rules,
    }


def test_run_business_rules_evaluates_multiple_types() -> None:
    contract = _valid_contract([
        {
            "rule_id": "r1",
            "severity": "high",
            "type": "range",
            "column": "price",
            "params": {"min": 0},
        },
        {
            "rule_id": "r2",
            "severity": "high",
            "type": "not_null_if",
            "column": "order_delivered_customer_date",
            "params": {"if_column": "order_status", "if_equals": "delivered"},
        },
        {
            "rule_id": "r3",
            "severity": "medium",
            "type": "accepted_values",
            "column": "order_status",
            "params": {"allowed": ["delivered", "unknown"]},
        },
        {
            "rule_id": "r4",
            "severity": "high",
            "type": "compare_columns",
            "columns": [
                "order_delivered_customer_date",
                "order_purchase_timestamp",
            ],
            "params": {"operator": ">="},
        },
    ])

    results = {
        result.rule_id: result for result in run_business_rules(build_df(), contract)
    }

    assert results["r1"].status == "FAIL"
    assert results["r2"].status == "PASS"
    assert results["r3"].status == "PASS"
    assert results["r4"].status == "PASS"


def test_run_business_rules_raises_for_invalid_contract() -> None:
    with pytest.raises(ValueError, match="Campos ausentes"):
        run_business_rules(build_df(), {"rules": []})


def test_run_business_rules_raises_for_empty_rules_list() -> None:
    with pytest.raises(ValueError, match="lista não vazia"):
        run_business_rules(build_df(), {
            "contract_id": "x", "version": 1,
            "dataset_name": "ds", "owner": "o", "rules": [],
        })


def test_rule_expression_passes_when_condition_holds() -> None:
    df = pd.DataFrame({"price": [10.0, 5.0]})
    contract = _valid_contract([{
        "rule_id": "expr1",
        "severity": "high",
        "type": "expression",
        "params": {"expression": "price > 0"},
    }])
    results = run_business_rules(df, contract)
    assert results[0].status == "PASS"
    assert results[0].failed_rows == 0


def test_rule_expression_fails_when_condition_violated() -> None:
    df = pd.DataFrame({"price": [10.0, -1.0]})
    contract = _valid_contract([{
        "rule_id": "expr2",
        "severity": "high",
        "type": "expression",
        "params": {"expression": "price > 0"},
    }])
    results = run_business_rules(df, contract)
    assert results[0].status == "FAIL"
    assert results[0].failed_rows == 1


def test_rule_expression_raises_for_empty_expression() -> None:
    df = pd.DataFrame({"price": [1.0]})
    contract = _valid_contract([{
        "rule_id": "empty_expr",
        "severity": "high",
        "type": "expression",
        "params": {"expression": ""},
    }])
    with pytest.raises(ValueError, match="sem expressão"):
        run_business_rules(df, contract)


def test_compare_columns_all_operators() -> None:
    df = pd.DataFrame({"a": [3.0], "b": [2.0]})
    for operator, expected_status in [
        (">=", "PASS"), (">", "PASS"), ("<=", "FAIL"), ("<", "FAIL"), ("==", "FAIL")
    ]:
        contract = _valid_contract([{
            "rule_id": f"op_{operator}",
            "severity": "high",
            "type": "compare_columns",
            "columns": ["a", "b"],
            "params": {"operator": operator},
        }])
        results = run_business_rules(df, contract)
        assert results[0].status == expected_status, f"Failed for operator={operator}"


def test_compare_columns_raises_for_unknown_operator() -> None:
    df = pd.DataFrame({"a": [1.0], "b": [1.0]})
    contract = _valid_contract([{
        "rule_id": "bad_op",
        "severity": "high",
        "type": "compare_columns",
        "columns": ["a", "b"],
        "params": {"operator": "!="},
    }])
    with pytest.raises(ValueError, match="Operador não suportado"):
        run_business_rules(df, contract)


def test_run_business_rules_raises_for_unknown_rule_type() -> None:
    df = pd.DataFrame({"price": [1.0]})
    contract = _valid_contract([{
        "rule_id": "bad_type",
        "severity": "high",
        "type": "unknown_type",
        "column": "price",
    }])
    with pytest.raises(ValueError, match="Tipo de regra não suportado"):
        run_business_rules(df, contract)


def test_save_results_and_render_report(tmp_path: Path, monkeypatch) -> None:
    df = pd.DataFrame({"price": [10.0, -1.0]})
    contract = _valid_contract([{
        "rule_id": "r1",
        "severity": "high",
        "type": "range",
        "column": "price",
        "params": {"min": 0},
        "description": "price must be >= 0",
    }])
    results = run_business_rules(df, contract)

    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(bv, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(bv, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(bv, "RESULTS_PATH", quality_dir / "business_rule_results.csv")
    monkeypatch.setattr(bv, "REPORT_PATH", docs_dir / "business_rule_report.md")

    results_path = bv.save_results(results)
    report_path = bv.save_report(results, contract)
    report_text = bv.render_report(results, contract)

    assert results_path.exists()
    assert report_path.exists()
    assert "Relatório de Regras de Negócio" in report_text
    assert "r1" in report_text
