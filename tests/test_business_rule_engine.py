from __future__ import annotations

import pandas as pd
import pytest

from src.business_rule_components import engine
from src.business_rule_components.models import BusinessRuleResult


def _contract(rules: list[dict]) -> dict:
    return {
        "contract_id": "demo",
        "version": 1,
        "dataset_name": "demo",
        "owner": "owner",
        "rules": rules,
    }


def test_engine_preserves_order_runner_selection_and_result_structure() -> None:
    events: list[str] = []
    contract = _contract(
        [
            {"rule_id": "first", "type": "a", "severity": "high"},
            {"rule_id": "second", "type": "b", "severity": "medium"},
        ]
    )

    def runner_a(df, rule):
        events.append(rule["rule_id"])
        return pd.Series([False, True], index=df.index)

    def runner_b(df, rule):
        events.append(rule["rule_id"])
        return pd.Series([False, False], index=df.index)

    results = engine.run_business_rules(
        pd.DataFrame({"value": [1, 2]}),
        contract,
        runners={"a": runner_a, "b": runner_b},
    )

    assert events == ["first", "second"]
    assert [result.rule_id for result in results] == ["first", "second"]
    assert [result.status for result in results] == ["FAIL", "PASS"]
    assert all(isinstance(result, BusinessRuleResult) for result in results)


def test_engine_preserves_residual_tolerance_and_rounding() -> None:
    rule = {
        "rule_id": "tolerated",
        "type": "range",
        "severity": "high",
        "description": "rule",
        "params": {"max_failure_pct": 0.01},
    }
    result = engine.build_result(
        rule, pd.Series([True] * 8 + [False] * 112_642), 112_650, "rule"
    )

    assert result == BusinessRuleResult(
        "tolerated",
        "PASS",
        "high",
        8,
        0.0071,
        "rule Falha residual dentro da tolerancia contratual de 0.01%.",
    )


def test_engine_rejects_invalid_contract_and_unknown_type() -> None:
    with pytest.raises(ValueError, match="Campos ausentes"):
        engine.run_business_rules(pd.DataFrame(), {"rules": []}, runners={})
    with pytest.raises(ValueError, match="lista não vazia"):
        engine.run_business_rules(pd.DataFrame(), _contract([]), runners={})
    with pytest.raises(ValueError, match="Tipo de regra não suportado"):
        engine.run_business_rules(
            pd.DataFrame({"value": [1]}),
            _contract([{"rule_id": "x", "type": "unknown", "severity": "high"}]),
            runners={},
        )
