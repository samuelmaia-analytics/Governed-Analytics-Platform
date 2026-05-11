from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PUBLISHED_MONITORING_DIR, QUALITY_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
SCORECARD_CSV_PATH = PUBLISHED_MONITORING_DIR / "governance_scorecards.csv"
SCORECARD_JSON_PATH = PUBLISHED_MONITORING_DIR / "governance_scorecards.json"
REPORT_PATH = DOCS_DIR / "governance_scorecards.md"

QUALITY_RESULTS_PATH = QUALITY_DIR / "fact_orders_enriched_quality_checks.csv"
PRIVACY_RESULTS_PATH = QUALITY_DIR / "privacy_governance_results.csv"
SCHEMA_CONTRACT_RESULTS_PATH = QUALITY_DIR / "schema_contract_results.csv"
BUSINESS_RULE_RESULTS_PATH = QUALITY_DIR / "business_rule_results.csv"
PUBLISHED_MONITORING_RESULTS_PATH = (
    PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
)


@dataclass(frozen=True)
class ScorecardMetric:
    dataset_name: str
    dimension: str
    score: float
    status: str
    source: str
    total_checks: int
    failed_checks: int


@dataclass(frozen=True)
class DatasetScorecard:
    dataset_name: str
    governance_score: float
    status: str


def _severity_weight(value: object) -> int:
    severity = str(value).strip().lower()
    return {"high": 3, "medium": 2, "low": 1}.get(severity, 2)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _score_from_checks(df: pd.DataFrame) -> tuple[float, int, int]:
    if df.empty:
        return 0.0, 0, 0
    weighted_total = 0
    weighted_pass = 0
    failed_checks = 0
    for row in df.to_dict("records"):
        weight = _severity_weight(row.get("severity", "medium"))
        weighted_total += weight
        if str(row.get("status", "")).upper() == "PASS":
            weighted_pass += weight
        else:
            failed_checks += 1
    if weighted_total == 0:
        return 0.0, len(df), failed_checks
    return round((weighted_pass / weighted_total) * 100, 2), len(df), failed_checks


def _status_from_score(score: float) -> str:
    if score >= 95:
        return "healthy"
    if score >= 80:
        return "attention"
    return "critical"


def build_metrics() -> list[ScorecardMetric]:
    metrics: list[ScorecardMetric] = []

    curated_quality = _read_csv(QUALITY_RESULTS_PATH)
    if not curated_quality.empty:
        score, total, failed = _score_from_checks(curated_quality)
        metrics.append(
            ScorecardMetric(
                "fact_orders_enriched",
                "data_quality",
                score,
                _status_from_score(score),
                str(QUALITY_RESULTS_PATH),
                total,
                failed,
            )
        )

    business_rules = _read_csv(BUSINESS_RULE_RESULTS_PATH)
    if not business_rules.empty:
        score, total, failed = _score_from_checks(business_rules)
        metrics.append(
            ScorecardMetric(
                "fact_orders_enriched",
                "business_rules",
                score,
                _status_from_score(score),
                str(BUSINESS_RULE_RESULTS_PATH),
                total,
                failed,
            )
        )

    schema_contracts = _read_csv(SCHEMA_CONTRACT_RESULTS_PATH)
    if not schema_contracts.empty and {"dataset_name", "status"}.issubset(
        schema_contracts.columns
    ):
        for dataset_name, slice_df in schema_contracts.groupby("dataset_name"):
            score, total, failed = _score_from_checks(slice_df)
            metrics.append(
                ScorecardMetric(
                    str(dataset_name),
                    "schema_contracts",
                    score,
                    _status_from_score(score),
                    str(SCHEMA_CONTRACT_RESULTS_PATH),
                    total,
                    failed,
                )
            )

    privacy_results = _read_csv(PRIVACY_RESULTS_PATH)
    if not privacy_results.empty:
        score, total, failed = _score_from_checks(privacy_results)
        metrics.append(
            ScorecardMetric(
                "fact_orders_dashboard",
                "privacy_governance",
                score,
                _status_from_score(score),
                str(PRIVACY_RESULTS_PATH),
                total,
                failed,
            )
        )

    published_monitoring = _read_csv(PUBLISHED_MONITORING_RESULTS_PATH)
    if not published_monitoring.empty:
        score, total, failed = _score_from_checks(published_monitoring)
        metrics.append(
            ScorecardMetric(
                "fact_orders_dashboard",
                "published_monitoring",
                score,
                _status_from_score(score),
                str(PUBLISHED_MONITORING_RESULTS_PATH),
                total,
                failed,
            )
        )

    return metrics


def build_dataset_scorecards(metrics: list[ScorecardMetric]) -> list[DatasetScorecard]:
    if not metrics:
        return []
    by_dataset: dict[str, list[ScorecardMetric]] = {}
    for metric in metrics:
        by_dataset.setdefault(metric.dataset_name, []).append(metric)
    scorecards: list[DatasetScorecard] = []
    for dataset_name, dataset_metrics in sorted(by_dataset.items()):
        score = round(
            sum(metric.score for metric in dataset_metrics) / len(dataset_metrics), 2
        )
        scorecards.append(
            DatasetScorecard(dataset_name, score, _status_from_score(score))
        )
    return scorecards


def save_outputs(
    metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]
) -> tuple[Path, Path]:
    ensure_directory(PUBLISHED_MONITORING_DIR)
    pd.DataFrame(asdict(metric) for metric in metrics).to_csv(
        SCORECARD_CSV_PATH, index=False
    )
    SCORECARD_JSON_PATH.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "metrics": [asdict(metric) for metric in metrics],
                "dataset_scorecards": [asdict(scorecard) for scorecard in scorecards],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return SCORECARD_CSV_PATH, SCORECARD_JSON_PATH


def render_report(
    metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]
) -> str:
    lines = [
        "# Governance Scorecards",
        "",
        "Scorecards de governança por dataset gerados a partir de qualidade, contratos, privacidade e monitoramento.",
        "",
        "## Score por Dataset",
        "",
        "| Dataset | Governance Score | Status |",
        "| --- | ---: | --- |",
    ]
    for scorecard in scorecards:
        lines.append(
            f"| `{scorecard.dataset_name}` | {scorecard.governance_score} | `{scorecard.status}` |"
        )
    lines.extend(
        [
            "",
            "## Métricas por Dimensão",
            "",
            "| Dataset | Dimensão | Score | Falhas | Total Checks | Fonte |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for metric in metrics:
        lines.append(
            f"| `{metric.dataset_name}` | `{metric.dimension}` | {metric.score} | {metric.failed_checks} | {metric.total_checks} | `{Path(metric.source).as_posix()}` |"
        )
    return "\n".join(lines) + "\n"


def save_report(
    metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]
) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(metrics, scorecards), encoding="utf-8")
    return REPORT_PATH


def main() -> None:
    configure_logging()
    metrics = build_metrics()
    scorecards = build_dataset_scorecards(metrics)
    save_outputs(metrics, scorecards)
    save_report(metrics, scorecards)
    LOGGER.info(
        "Governance scorecards gerados | datasets=%s dimensoes=%s",
        len(scorecards),
        len(metrics),
    )


if __name__ == "__main__":
    main()
