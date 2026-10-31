from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.schema_contract_components.models import ContractCheck
from src.utils import ensure_directory


def save_results(
    checks: list[ContractCheck],
    *,
    quality_dir: Path,
    results_path: Path,
    logger: logging.Logger,
) -> Path:
    ensure_directory(quality_dir)
    pd.DataFrame(asdict(check) for check in checks).to_csv(results_path, index=False)
    logger.info("Resultados dos contratos salvos em %s", results_path)
    return results_path


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


def save_report(
    checks: list[ContractCheck],
    *,
    docs_dir: Path,
    report_path: Path,
    logger: logging.Logger,
) -> Path:
    ensure_directory(docs_dir)
    report_path.write_text(render_report(checks), encoding="utf-8")
    logger.info("Relatorio de contratos salvo em %s", report_path)
    return report_path
