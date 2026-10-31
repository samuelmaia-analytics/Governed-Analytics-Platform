from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.business_rule_components import engine as _engine
from src.business_rule_components import outputs as _outputs
from src.business_rule_components import runners as _runners
from src.business_rule_components.models import BusinessRuleResult
from src.config import ANALYTICS_DIR, DOCS_DIR, QUALITY_DIR, ROOT_DIR
from src.ingest import configure_logging

LOGGER = logging.getLogger(__name__)
FACT_TABLE_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
CONTRACT_PATH = (
    ROOT_DIR
    / "contracts"
    / "governance"
    / "business_rules"
    / "fact_orders_enriched.v1.json"
)
RESULTS_PATH = QUALITY_DIR / "business_rule_results.csv"
REPORT_PATH = DOCS_DIR / "business_rule_report.md"


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
    _engine.validate_contract_shape(contract)


def _build_result(
    rule: dict[str, Any], failed_mask: pd.Series, total_rows: int, details: str
) -> BusinessRuleResult:
    return _engine.build_result(rule, failed_mask, total_rows, details)


def _rule_range(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    return _runners.rule_range(df, rule)


def _rule_not_null_if(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    return _runners.rule_not_null_if(df, rule)


def _rule_accepted_values(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    return _runners.rule_accepted_values(df, rule)


def _rule_compare_columns(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    return _runners.rule_compare_columns(df, rule)


def _rule_expression(df: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    return _runners.rule_expression(df, rule)


def run_business_rules(
    df: pd.DataFrame, contract: dict[str, Any]
) -> list[BusinessRuleResult]:
    runners = {
        "range": _rule_range,
        "not_null_if": _rule_not_null_if,
        "accepted_values": _rule_accepted_values,
        "compare_columns": _rule_compare_columns,
        "expression": _rule_expression,
    }
    return _engine.run_business_rules(
        df,
        contract,
        runners=runners,
        validate_contract_fn=_validate_contract_shape,
        build_result_fn=_build_result,
    )


def save_results(results: list[BusinessRuleResult]) -> Path:
    return _outputs.save_results(
        results, quality_dir=QUALITY_DIR, results_path=RESULTS_PATH
    )


def render_report(
    results: list[BusinessRuleResult], contract: dict[str, Any]
) -> str:
    return _outputs.render_report(results, contract)


def save_report(
    results: list[BusinessRuleResult], contract: dict[str, Any]
) -> Path:
    return _outputs.save_report(
        results,
        contract,
        docs_dir=DOCS_DIR,
        report_path=REPORT_PATH,
    )


def main(
    *, capture_results_fn: Callable[[list[BusinessRuleResult]], None] | None = None
) -> None:
    configure_logging()
    df = load_fact_table()
    contract = load_contract()
    results = run_business_rules(df, contract)
    if capture_results_fn is not None:
        capture_results_fn(results)
    save_results(results)
    save_report(results, contract)
    if any(result.status == "FAIL" and result.severity == "high" for result in results):
        raise SystemExit("Falha em regra de negócio de severidade alta.")
    LOGGER.info("Validação de regras de negócio concluída.")


if __name__ == "__main__":
    main()
