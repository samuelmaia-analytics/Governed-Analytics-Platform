from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, QUALITY_DIR, ROOT_DIR
from src.ingest import configure_logging
from src.schema_contract_components import checks as _checks
from src.schema_contract_components import discovery as _discovery
from src.schema_contract_components import outputs as _outputs
from src.schema_contract_components.models import ContractCheck

LOGGER = logging.getLogger(__name__)
CONTRACTS_DIR = ROOT_DIR / "contracts"
RESULTS_PATH = QUALITY_DIR / "schema_contract_results.csv"
REPORT_PATH = DOCS_DIR / "schema_contract_report.md"


def load_contract(path: Path) -> dict[str, Any]:
    return _discovery.load_contract(path)


def iter_contract_paths() -> list[Path]:
    return _discovery.iter_contract_paths(CONTRACTS_DIR)


def load_dataset(contract: dict[str, Any]) -> pd.DataFrame:
    return _discovery.load_dataset(contract, root_dir=ROOT_DIR)


def matches_expected_type(series: pd.Series, expected_type: str) -> bool:
    return _checks.matches_expected_type(series, expected_type)


def validate_contract(contract: dict[str, Any]) -> list[ContractCheck]:
    return _checks.validate_contract(contract, load_dataset_fn=load_dataset)


def run_contract_checks() -> list[ContractCheck]:
    return _checks.run_contract_checks(
        contract_paths_fn=iter_contract_paths,
        load_contract_fn=load_contract,
        validate_contract_fn=validate_contract,
    )


def save_results(checks: list[ContractCheck]) -> Path:
    return _outputs.save_results(
        checks,
        quality_dir=QUALITY_DIR,
        results_path=RESULTS_PATH,
        logger=LOGGER,
    )


def render_report(checks: list[ContractCheck]) -> str:
    return _outputs.render_report(checks)


def save_report(checks: list[ContractCheck]) -> Path:
    return _outputs.save_report(
        checks,
        docs_dir=DOCS_DIR,
        report_path=REPORT_PATH,
        logger=LOGGER,
    )


def main(
    *, capture_results_fn: Callable[[list[ContractCheck]], None] | None = None
) -> None:
    configure_logging()
    checks = run_contract_checks()
    if capture_results_fn is not None:
        capture_results_fn(checks)
    save_results(checks)
    save_report(checks)


if __name__ == "__main__":
    main()
