from __future__ import annotations

import pandas as pd
import pytest

from src.business_rule_components import runners


def test_five_rule_runners_preserve_current_failure_masks() -> None:
    df = pd.DataFrame(
        {
            "value": [1.0, -1.0],
            "status": ["delivered", "invalid"],
            "delivered_at": [pd.Timestamp("2020-01-02"), pd.NaT],
            "purchased_at": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")],
        }
    )

    assert runners.rule_range(
        df, {"column": "value", "params": {"min": 0}}
    ).tolist() == [False, True]
    assert runners.rule_not_null_if(
        df,
        {
            "column": "delivered_at",
            "params": {"if_column": "status", "if_equals": "delivered"},
        },
    ).tolist() == [False, False]
    assert runners.rule_accepted_values(
        df, {"column": "status", "params": {"allowed": ["delivered"]}}
    ).tolist() == [False, True]
    assert runners.rule_compare_columns(
        df,
        {"columns": ["delivered_at", "purchased_at"], "params": {"operator": ">="}},
    ).tolist() == [False, False]
    assert runners.rule_expression(
        df, {"rule_id": "expr", "params": {"expression": "value >= 0"}}
    ).tolist() == [False, True]


def test_runner_exceptions_remain_unchanged() -> None:
    with pytest.raises(ValueError, match="Operador não suportado"):
        runners.rule_compare_columns(
            pd.DataFrame({"a": [1], "b": [1]}),
            {"columns": ["a", "b"], "params": {"operator": "!="}},
        )
    with pytest.raises(ValueError, match="sem expressão"):
        runners.rule_expression(
            pd.DataFrame({"a": [1]}),
            {"rule_id": "empty", "params": {"expression": ""}},
        )
