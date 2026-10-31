from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd

from src.business_rule_components.models import BusinessRuleResult

RuleRunner = Callable[[pd.DataFrame, dict[str, Any]], pd.Series]
BuildResultFn = Callable[[dict[str, Any], pd.Series, int, str], BusinessRuleResult]
ValidateContractFn = Callable[[dict[str, Any]], None]


def validate_contract_shape(contract: dict[str, Any]) -> None:
    required = {"contract_id", "version", "dataset_name", "owner", "rules"}
    missing = sorted(field for field in required if field not in contract)
    if missing:
        raise ValueError(
            f"Contrato de regras de negócio inválido. Campos ausentes: {missing}"
        )
    if not isinstance(contract["rules"], list) or not contract["rules"]:
        raise ValueError(
            "Contrato de regras de negócio inválido. `rules` deve ser uma lista não vazia."
        )


def build_result(
    rule: dict[str, Any], failed_mask: pd.Series, total_rows: int, details: str
) -> BusinessRuleResult:
    failed_rows = int(failed_mask.sum())
    failure_pct = round((failed_rows / total_rows) * 100, 4) if total_rows > 0 else 0.0
    params = rule.get("params", {})
    max_failure_pct = params.get("max_failure_pct")
    within_tolerance = max_failure_pct is not None and failure_pct <= float(
        max_failure_pct
    )
    status = "PASS" if failed_rows == 0 or within_tolerance else "FAIL"
    if within_tolerance and failed_rows > 0:
        details = f"{details} Falha residual dentro da tolerancia contratual de {max_failure_pct}%."
    return BusinessRuleResult(
        rule_id=str(rule["rule_id"]),
        status=status,
        severity=str(rule["severity"]),
        failed_rows=failed_rows,
        failure_pct=failure_pct,
        details=details,
    )


def run_business_rules(
    df: pd.DataFrame,
    contract: dict[str, Any],
    *,
    runners: Mapping[str, RuleRunner],
    validate_contract_fn: ValidateContractFn = validate_contract_shape,
    build_result_fn: BuildResultFn = build_result,
) -> list[BusinessRuleResult]:
    validate_contract_fn(contract)
    results: list[BusinessRuleResult] = []
    for rule in contract["rules"]:
        rule_type = str(rule["type"])
        runner = runners.get(rule_type)
        if runner is None:
            raise ValueError(f"Tipo de regra não suportado: {rule_type}")
        failed_mask = runner(df, rule)
        results.append(
            build_result_fn(
                rule,
                failed_mask,
                len(df),
                str(rule.get("description", "")),
            )
        )
    return results
