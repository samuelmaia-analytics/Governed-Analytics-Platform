from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from src.business_rule_components.models import BusinessRuleResult
from src.utils import ensure_directory


def save_results(
    results: list[BusinessRuleResult], *, quality_dir: Path, results_path: Path
) -> Path:
    ensure_directory(quality_dir)
    pd.DataFrame(asdict(result) for result in results).to_csv(results_path, index=False)
    return results_path


def render_report(
    results: list[BusinessRuleResult], contract: dict[str, Any]
) -> str:
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


def save_report(
    results: list[BusinessRuleResult],
    contract: dict[str, Any],
    *,
    docs_dir: Path,
    report_path: Path,
) -> Path:
    ensure_directory(docs_dir)
    report_path.write_text(render_report(results, contract), encoding="utf-8")
    return report_path
