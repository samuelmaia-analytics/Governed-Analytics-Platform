from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PUBLISHED_MONITORING_DIR, QUALITY_DIR
from src.ingest import configure_logging
from src.scorecard_components import outputs as _outputs
from src.scorecard_components import pipeline as _pipeline
from src.scorecard_components import readers as _readers
from src.scorecard_components import scoring as _scoring
from src.scorecard_components.models import DatasetScorecard, ScorecardMetric

LOGGER = logging.getLogger(__name__)
SCORECARD_CSV_PATH = PUBLISHED_MONITORING_DIR / "governance_scorecards.csv"
SCORECARD_JSON_PATH = PUBLISHED_MONITORING_DIR / "governance_scorecards.json"
REPORT_PATH = DOCS_DIR / "governance_scorecards.md"
QUALITY_RESULTS_PATH = QUALITY_DIR / "fact_orders_enriched_quality_checks.csv"
PRIVACY_RESULTS_PATH = QUALITY_DIR / "privacy_governance_results.csv"
SCHEMA_CONTRACT_RESULTS_PATH = QUALITY_DIR / "schema_contract_results.csv"
BUSINESS_RULE_RESULTS_PATH = QUALITY_DIR / "business_rule_results.csv"
PUBLISHED_MONITORING_RESULTS_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"


def _severity_weight(value: object) -> int:
    return _scoring.severity_weight(value)


def _read_csv(path: Path) -> pd.DataFrame:
    return _readers.read_csv(path)


def _score_from_checks(df: pd.DataFrame) -> tuple[float, int, int]:
    return _scoring.score_from_checks(df)


def _status_from_score(score: float) -> str:
    return _scoring.status_from_score(score)


def build_metrics() -> list[ScorecardMetric]:
    return _scoring.build_metrics(
        read_csv_fn=_read_csv,
        quality_results_path=QUALITY_RESULTS_PATH,
        business_rule_results_path=BUSINESS_RULE_RESULTS_PATH,
        schema_contract_results_path=SCHEMA_CONTRACT_RESULTS_PATH,
        privacy_results_path=PRIVACY_RESULTS_PATH,
        published_monitoring_results_path=PUBLISHED_MONITORING_RESULTS_PATH,
    )


def build_dataset_scorecards(metrics: list[ScorecardMetric]) -> list[DatasetScorecard]:
    return _scoring.build_dataset_scorecards(metrics)


def save_outputs(metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]) -> tuple[Path, Path]:
    return _outputs.save_outputs(metrics, scorecards, output_dir=PUBLISHED_MONITORING_DIR, csv_path=SCORECARD_CSV_PATH, json_path=SCORECARD_JSON_PATH)


def render_report(metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]) -> str:
    return _outputs.render_report(metrics, scorecards)


def save_report(metrics: list[ScorecardMetric], scorecards: list[DatasetScorecard]) -> Path:
    return _outputs.save_report(render_report(metrics, scorecards), docs_dir=DOCS_DIR, report_path=REPORT_PATH)


def main() -> None:
    configure_logging()
    metrics, scorecards = _pipeline.run_scorecards(
        build_metrics_fn=build_metrics,
        build_dataset_scorecards_fn=build_dataset_scorecards,
        save_outputs_fn=save_outputs,
        save_report_fn=save_report,
    )
    LOGGER.info("Governance scorecards gerados | datasets=%s dimensoes=%s", len(scorecards), len(metrics))


if __name__ == "__main__":
    main()
