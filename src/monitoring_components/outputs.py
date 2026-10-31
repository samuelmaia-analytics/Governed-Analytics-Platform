from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.monitoring_components.models import MonitoringCheckResult
from src.utils import ensure_directory


def save_results(
    results: list[MonitoringCheckResult],
    *,
    monitoring_dir: Path,
    results_path: Path,
    summary_path: Path,
) -> tuple[Path, Path]:
    ensure_directory(monitoring_dir)
    results_df = pd.DataFrame(asdict(result) for result in results)
    results_df.to_csv(results_path, index=False)
    summary_path.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "total_checks": len(results),
                "failed_checks": int((results_df["status"] == "FAIL").sum()),
                "results": [asdict(result) for result in results],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return results_path, summary_path


def render_report(results: list[MonitoringCheckResult]) -> str:
    results_df = pd.DataFrame(asdict(result) for result in results)
    failed_df = results_df[results_df["status"] == "FAIL"]
    lines = [
        "# Monitoramento da Camada Published",
        "",
        "Relatorio recorrente de freshness e qualidade da camada `fact_orders_dashboard`.",
        "",
        "## Resumo",
        "",
        f"- Checks executados: **{len(results)}**",
        f"- Checks aprovados: **{int((results_df['status'] == 'PASS').sum())}**",
        f"- Checks reprovados: **{int((results_df['status'] == 'FAIL').sum())}**",
        "",
        "## Resultado dos Checks",
        "",
        "| Check | Status | Valor | Threshold | Severidade |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in results_df.itertuples(index=False):
        lines.append(
            f"| `{row.check_name}` | **{row.status}** | {row.metric_value} | {row.threshold} | {row.severity} |"
        )
    lines.extend(["", "## Alertas", ""])
    if failed_df.empty:
        lines.append("- Nenhum alerta aberto na execucao atual.")
    else:
        for row in failed_df.itertuples(index=False):
            lines.append(
                f"- `{row.check_name}`: {row.details} Valor observado={row.metric_value}."
            )
    return "\n".join(lines) + "\n"


def save_report(report: str, *, docs_dir: Path, report_path: Path) -> Path:
    ensure_directory(docs_dir)
    report_path.write_text(report, encoding="utf-8")
    return report_path
