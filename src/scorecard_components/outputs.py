from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.scorecard_components.models import DatasetScorecard, ScorecardMetric
from src.utils import ensure_directory


def save_outputs(metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard], *, output_dir: Path, csv_path: Path, json_path: Path) -> tuple[Path, Path]:
    ensure_directory(output_dir)
    pd.DataFrame(asdict(metric) for metric in metrics).to_csv(csv_path, index=False)
    json_path.write_text(json.dumps({"generated_at_utc": datetime.now(timezone.utc).isoformat(), "metrics": [asdict(metric) for metric in metrics], "dataset_scorecards": [asdict(scorecard) for scorecard in scorecards]}, ensure_ascii=False, indent=2), encoding="utf-8")
    return csv_path, json_path


def render_report(metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]) -> str:
    lines = ["# Governance Scorecards", "", "Scorecards de governança por dataset gerados a partir de qualidade, contratos, privacidade e monitoramento.", "", "## Score por Dataset", "", "| Dataset | Governance Score | Status |", "| --- | ---: | --- |"]
    for scorecard in scorecards:
        lines.append(f"| `{scorecard.dataset_name}` | {scorecard.governance_score} | `{scorecard.status}` |")
    lines.extend(["", "## Métricas por Dimensão", "", "| Dataset | Dimensão | Score | Falhas | Total Checks | Fonte |", "| --- | --- | ---: | ---: | ---: | --- |"])
    for metric in metrics:
        lines.append(f"| `{metric.dataset_name}` | `{metric.dimension}` | {metric.score} | {metric.failed_checks} | {metric.total_checks} | `{Path(metric.source).as_posix()}` |")
    return "\n".join(lines) + "\n"


def save_report(report: str, *, docs_dir: Path, report_path: Path) -> Path:
    ensure_directory(docs_dir)
    report_path.write_text(report, encoding="utf-8")
    return report_path

