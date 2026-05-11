from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, QUALITY_DIR, ROOT_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
CONTRACTS_DIR = ROOT_DIR / "contracts"
RESULTS_PATH = QUALITY_DIR / "schema_contract_results.csv"
REPORT_PATH = DOCS_DIR / "schema_contract_report.md"


@dataclass
class ContractCheck:
    dataset_name: str
    layer: str
    check_name: str
    status: str
    details: str


def load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_contract_paths() -> list[Path]:
    return sorted(CONTRACTS_DIR.glob("*/*.contract.json"))


def load_dataset(contract: dict[str, Any]) -> pd.DataFrame:
    dataset_path = ROOT_DIR / str(contract["path"])
    if dataset_path.suffix == ".parquet":
        return pd.read_parquet(dataset_path)
    if dataset_path.suffix == ".csv":
        return pd.read_csv(dataset_path)
    raise ValueError(f"Formato nao suportado no contrato: {dataset_path}")


def matches_expected_type(series: pd.Series, expected_type: str) -> bool:
    if expected_type == "string":
        return is_string_dtype(series.dtype) or is_object_dtype(series.dtype)
    if expected_type == "integer":
        return is_integer_dtype(series.dtype)
    if expected_type == "float":
        return is_float_dtype(series.dtype) or is_integer_dtype(series.dtype)
    if expected_type == "boolean":
        return is_bool_dtype(series.dtype)
    if expected_type == "datetime":
        return is_datetime64_any_dtype(series.dtype)
    if expected_type == "date_like":
        if is_datetime64_any_dtype(series.dtype):
            return True
        if not is_object_dtype(series.dtype):
            return False
        non_null = series.dropna()
        return non_null.empty or all(
            hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day")
            for value in non_null.head(50)
        )
    raise ValueError(f"Tipo esperado desconhecido: {expected_type}")


def validate_contract(contract: dict[str, Any]) -> list[ContractCheck]:
    dataset_name = str(contract["dataset_name"])
    layer = str(contract["layer"])
    df = load_dataset(contract)
    checks: list[ContractCheck] = []

    expected_columns = set(contract["columns"].keys())
    actual_columns = set(df.columns)
    missing_columns = sorted(expected_columns - actual_columns)
    checks.append(
        ContractCheck(
            dataset_name=dataset_name,
            layer=layer,
            check_name="missing_columns",
            status="PASS" if not missing_columns else "FAIL",
            details=f"Ausentes: {missing_columns if missing_columns else 'nenhuma'}",
        )
    )

    if not bool(contract.get("allow_unexpected_columns", False)):
        unexpected_columns = sorted(actual_columns - expected_columns)
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name="unexpected_columns",
                status="PASS" if not unexpected_columns else "FAIL",
                details=f"Inesperadas: {unexpected_columns if unexpected_columns else 'nenhuma'}",
            )
        )

    for column, expected_type in contract["columns"].items():
        if column not in df.columns:
            continue
        matches = matches_expected_type(df[column], str(expected_type))
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name=f"type__{column}",
                status="PASS" if matches else "FAIL",
                details=f"Esperado={expected_type} | atual={df[column].dtype}",
            )
        )

    min_rows = int(contract.get("min_rows", 0))
    checks.append(
        ContractCheck(
            dataset_name=dataset_name,
            layer=layer,
            check_name="min_rows",
            status="PASS" if len(df) >= min_rows else "FAIL",
            details=f"Linhas observadas={len(df)} | minimo={min_rows}",
        )
    )

    primary_key = list(contract.get("primary_key", []))
    if primary_key:
        duplicate_count = int(df.duplicated(subset=primary_key, keep=False).sum())
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name="primary_key_duplicates",
                status="PASS" if duplicate_count == 0 else "FAIL",
                details=f"Chave={primary_key} | duplicados={duplicate_count}",
            )
        )

    return checks


def run_contract_checks() -> list[ContractCheck]:
    checks: list[ContractCheck] = []
    for contract_path in iter_contract_paths():
        contract = load_contract(contract_path)
        checks.extend(validate_contract(contract))
    return checks


def save_results(checks: list[ContractCheck]) -> Path:
    ensure_directory(QUALITY_DIR)
    pd.DataFrame(asdict(check) for check in checks).to_csv(RESULTS_PATH, index=False)
    LOGGER.info("Resultados dos contratos salvos em %s", RESULTS_PATH)
    return RESULTS_PATH


def render_report(checks: list[ContractCheck]) -> str:
    df = pd.DataFrame(asdict(check) for check in checks)
    summary = (
        df.groupby(["dataset_name", "layer"], as_index=False)
        .agg(
            total_checks=("check_name", "count"),
            failed_checks=("status", lambda s: int((s == "FAIL").sum())),
        )
        .sort_values(["layer", "dataset_name"])
    )

    lines = [
        "# Relatorio de Contratos de Schema",
        "",
        "Este documento registra a validacao dos contratos simples de schema das camadas principais do projeto.",
        "",
        "## Resumo",
        "",
        "| Dataset | Camada | Checks | Falhas |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            f"| `{row.dataset_name}` | `{row.layer}` | {int(row.total_checks)} | {int(row.failed_checks)} |"
        )

    lines.extend(
        [
            "",
            "## Resultado dos Checks",
            "",
            "| Dataset | Check | Status | Detalhes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in df.itertuples(index=False):
        lines.append(
            f"| `{row.dataset_name}` | `{row.check_name}` | **{row.status}** | {row.details} |"
        )

    return "\n".join(lines)


def save_report(checks: list[ContractCheck]) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(checks), encoding="utf-8")
    LOGGER.info("Relatorio de contratos salvo em %s", REPORT_PATH)
    return REPORT_PATH


def main() -> None:
    configure_logging()
    checks = run_contract_checks()
    save_results(checks)
    save_report(checks)


if __name__ == "__main__":
    main()
