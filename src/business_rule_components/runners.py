from __future__ import annotations

from typing import Any

import pandas as pd


def rule_range(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    column = str(rule["column"])
    params = rule.get("params", {})
    min_value = params.get("min")
    max_value = params.get("max")
    failed = pd.Series(False, index=df.index)
    if min_value is not None:
        failed = failed | (df[column] < min_value)
    if max_value is not None:
        failed = failed | (df[column] > max_value)
    return failed.fillna(False)


def rule_not_null_if(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    column = str(rule["column"])
    params = rule.get("params", {})
    if_column = str(params["if_column"])
    if_equals = params["if_equals"]
    condition = df[if_column] == if_equals
    return (condition & df[column].isna()).fillna(False)


def rule_accepted_values(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    column = str(rule["column"])
    allowed = set(rule.get("params", {}).get("allowed", []))
    return (~df[column].isin(allowed) & df[column].notna()).fillna(False)


def rule_compare_columns(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    left_column, right_column = list(rule["columns"])
    operator = str(rule.get("params", {}).get("operator", "=="))
    left = df[left_column]
    right = df[right_column]
    valid_rows = left.notna() & right.notna()
    if operator == ">=":
        failed = valid_rows & (left < right)
    elif operator == ">":
        failed = valid_rows & (left <= right)
    elif operator == "<=":
        failed = valid_rows & (left > right)
    elif operator == "<":
        failed = valid_rows & (left >= right)
    elif operator == "==":
        failed = valid_rows & (left != right)
    else:
        raise ValueError(f"Operador não suportado em compare_columns: {operator}")
    return failed.fillna(False)


def rule_expression(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    expression = str(rule.get("params", {}).get("expression", "")).strip()
    if not expression:
        raise ValueError(f"Regra `{rule['rule_id']}` sem expressão.")
    evaluated = df.eval(expression)
    return (~evaluated.fillna(False)).astype(bool)
