from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml  # type: ignore[import-untyped]

from src.governance_types import DataQualityCheck


@dataclass(frozen=True)
class DataQualityRule:
    name: str
    rule_type: str
    columns: list[str]
    severity: str
    params: dict[str, Any]
    recommendation: str


def load_quality_rules(path: str | Path) -> list[DataQualityRule]:
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rules_data = loaded.get("rules", [])
    rules: list[DataQualityRule] = []
    for item in rules_data:
        rules.append(
            DataQualityRule(
                name=str(item["name"]),
                rule_type=str(item["type"]),
                columns=[str(column) for column in item.get("columns", [])],
                severity=str(item.get("severity", "medium")),
                params=dict(item.get("params", {})),
                recommendation=str(item.get("recommendation", "Review data quality issue.")),
            )
        )
    return rules


def _build_check(
    *,
    rule: DataQualityRule,
    status: str,
    affected_columns: str,
    affected_rows: int,
    rule_source: str,
) -> DataQualityCheck:
    return {
        "check_name": rule.name,
        "status": status,
        "severity": rule.severity if status == "FAIL" else "low",
        "affected_columns": affected_columns,
        "affected_rows": affected_rows,
        "recommendation": rule.recommendation,
        "rule_source": rule_source,
    }


def execute_quality_rules(df: pd.DataFrame, rules: list[DataQualityRule], *, rule_source: str) -> list[DataQualityCheck]:
    checks: list[DataQualityCheck] = []
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    for rule in rules:
        rule_type = rule.rule_type
        columns = [column for column in rule.columns if column in df.columns]
        if not columns:
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL",
                    affected_columns=", ".join(rule.columns),
                    affected_rows=0,
                    rule_source=rule_source,
                )
            )
            continue

        if rule_type == "not_null":
            mask = df[columns].isna().any(axis=1)
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(mask.any()) else "PASS",
                    affected_columns=", ".join(columns),
                    affected_rows=int(mask.sum()),
                    rule_source=rule_source,
                )
            )
        elif rule_type == "unique":
            duplicated = df.duplicated(subset=columns, keep=False)
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(duplicated.any()) else "PASS",
                    affected_columns=", ".join(columns),
                    affected_rows=int(duplicated.sum()),
                    rule_source=rule_source,
                )
            )
        elif rule_type == "accepted_range":
            min_value = float(rule.params.get("min", float("-inf")))
            max_value = float(rule.params.get("max", float("inf")))
            target = columns[0]
            out_of_range = ~df[target].fillna(min_value).between(min_value, max_value)
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(out_of_range.any()) else "PASS",
                    affected_columns=target,
                    affected_rows=int(out_of_range.sum()),
                    rule_source=rule_source,
                )
            )
        elif rule_type == "no_future_dates":
            target = columns[0]
            series = pd.to_datetime(df[target], errors="coerce").dt.tz_localize(None)
            mask = series > now
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(mask.any()) else "PASS",
                    affected_columns=target,
                    affected_rows=int(mask.sum()),
                    rule_source=rule_source,
                )
            )
        elif rule_type == "no_negative_values":
            target = columns[0]
            mask = df[target].fillna(0) < 0
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(mask.any()) else "PASS",
                    affected_columns=target,
                    affected_rows=int(mask.sum()),
                    rule_source=rule_source,
                )
            )
        elif rule_type == "max_null_pct":
            max_null_pct = float(rule.params.get("max_null_pct", 0))
            column_pct = df[columns].isna().mean() * 100
            failing_columns = [str(column) for column, pct in column_pct.items() if float(pct) > max_null_pct]
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if failing_columns else "PASS",
                    affected_columns=", ".join(failing_columns),
                    affected_rows=int(len(df)) if failing_columns else 0,
                    rule_source=rule_source,
                )
            )
        elif rule_type == "allowed_values":
            target = columns[0]
            allowed = set(rule.params.get("allowed", []))
            invalid = ~df[target].isin(allowed)
            checks.append(
                _build_check(
                    rule=rule,
                    status="FAIL" if bool(invalid.any()) else "PASS",
                    affected_columns=target,
                    affected_rows=int(invalid.sum()),
                    rule_source=rule_source,
                )
            )
    return checks
