from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ANALYTICS_DIR, DOCS_DIR, QUALITY_DIR, ROOT_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
FACT_TABLE_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
CONTRACT_PATH = ROOT_DIR / "contracts" / "governance" / "business_rules" / "fact_orders_enriched.v1.json"
RESULTS_PATH = QUALITY_DIR / "business_rule_results.csv"
REPORT_PATH = DOCS_DIR / "business_rule_report.md"


@dataclass(frozen=True)
class BusinessRuleResult:
    rule_id: str
    status: str
    severity: str
    failed_rows: int
    failure_pct: float
    details: str


def load_fact_table() -> pd.DataFrame:
    if not FACT_TABLE_PATH.exists():
        raise FileNotFoundError(f"Tabela analítica não encontrada: {FACT_TABLE_PATH}")
    df = pd.read_parquet(FACT_TABLE_PATH)
    if df.empty:
        raise ValueError("fact_orders_enriched está vazia.")
    return df


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_contract_shape(contract: dict[str, Any]) -> None:
    required = {"contract_id", "version", "dataset_name", "owner", "rules"}
    missing = sorted(field for field in required if field not in contract)
    if missing:
        raise ValueError(f"Contrato de regras de negócio inválido. Campos ausentes: {missing}")
    if not isinstance(contract["rules"], list) or not contract["rules"]:
        raise ValueError("Contrato de regras de negócio inválido. `rules` deve ser uma lista não vazia.")


def _build_result(rule: dict[str, Any], failed_mask: pd.Series, total_rows: int, details: str) -> BusinessRuleResult:
    failed_rows = int(failed_mask.sum())
    failure_pct = round((failed_rows / total_rows) * 100, 4) if total_rows > 0 else 0.0
    return BusinessRuleResult(
        rule_id=str(rule["rule_id"]),
        status="PASS" if failed_rows == 0 else "FAIL",
        severity=str(rule["severity"]),
        failed_rows=failed_rows,
        failure_pct=failure_pct,
        details=details,
    )


def _rule_range(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
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


def _rule_not_null_if(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    column = str(rule["column"])
    params = rule.get("params", {})
    if_column = str(params["if_column"])
    if_equals = params["if_equals"]
    condition = df[if_column] == if_equals
    return (condition & df[column].isna()).fillna(False)


def _rule_accepted_values(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    column = str(rule["column"])
    allowed = set(rule.get("params", {}).get("allowed", []))
    return (~df[column].isin(allowed) & df[column].notna()).fillna(False)


def _rule_compare_columns(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
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


def _rule_expression(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    expression = str(rule.get("params", {}).get("expression", "")).strip()
    if not expression:
        raise ValueError(f"Regra `{rule['rule_id']}` sem expressão.")
    evaluated = df.eval(expression)
    return (~evaluated.fillna(False)).astype(bool)


def run_business_rules(df: pd.DataFrame, contract: dict[str, Any]) -> list[BusinessRuleResult]:
    _validate_contract_shape(contract)
    results: list[BusinessRuleResult] = []
    runners = {
        "range": _rule_range,
        "not_null_if": _rule_not_null_if,
        "accepted_values": _rule_accepted_values,
        "compare_columns": _rule_compare_columns,
        "expression": _rule_expression,
    }
    for rule in contract["rules"]:
        rule_type = str(rule["type"])
        runner = runners.get(rule_type)
        if runner is None:
            raise ValueError(f"Tipo de regra não suportado: {rule_type}")
        failed_mask = runner(df, rule)
        results.append(
            _build_result(
                rule=rule,
                failed_mask=failed_mask,
                total_rows=len(df),
                details=str(rule.get("description", "")),
            )
        )
    return results


def save_results(results: list[BusinessRuleResult]) -> Path:
    ensure_directory(QUALITY_DIR)
    pd.DataFrame(asdict(result) for result in results).to_csv(RESULTS_PATH, index=False)
    return RESULTS_PATH


def render_report(results: list[BusinessRuleResult], contract: dict[str, Any]) -> str:
    lines = [
        "# Relatório de Regras de Negócio",
        "",
        f"- Contrato: `{contract.get('contract_id', '-')}` v{contract.get('version', '-')}",
        f"- Dataset: `{contract.get('dataset_name', '-')}`",
        f"- Owner: `{contract.get('owner', '-')}`",
        f"- Regras avaliadas: **{len(results)}**",
        "",
        "| Regra | Status | Severidade | Linhas com falha | Falha (%) |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| `{result.rule_id}` | **{result.status}** | {result.severity} | {result.failed_rows} | {result.failure_pct} |"
        )
    return "\n".join(lines) + "\n"


def save_report(results: list[BusinessRuleResult], contract: dict[str, Any]) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(results, contract), encoding="utf-8")
    return REPORT_PATH


def main() -> None:
    configure_logging()
    df = load_fact_table()
    contract = load_contract()
    results = run_business_rules(df, contract)
    save_results(results)
    save_report(results, contract)
    if any(result.status == "FAIL" and result.severity == "high" for result in results):
        raise SystemExit("Falha em regra de negócio de severidade alta.")
    LOGGER.info("Validação de regras de negócio concluída.")


if __name__ == "__main__":
    main()
