from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.scorecard_components.models import DatasetScorecard, ScorecardMetric


def severity_weight(value: object) -> int:
    severity = str(value).strip().lower()
    return {"high": 3, "medium": 2, "low": 1}.get(severity, 2)


def score_from_checks(df: pd.DataFrame) -> tuple[float, int, int]:
    if df.empty:
        return 0.0, 0, 0
    weighted_total = 0
    weighted_pass = 0
    failed_checks = 0
    for row in df.to_dict("records"):
        weight = severity_weight(row.get("severity", "medium"))
        weighted_total += weight
        if str(row.get("status", "")).upper() == "PASS":
            weighted_pass += weight
        else:
            failed_checks += 1
    if weighted_total == 0:
        return 0.0, len(df), failed_checks
    return round((weighted_pass / weighted_total) * 100, 2), len(df), failed_checks


def status_from_score(score: float) -> str:
    if score >= 95:
        return "healthy"
    if score >= 80:
        return "attention"
    return "critical"


def build_metrics(
    *,
    read_csv_fn: Callable[[Path], pd.DataFrame],
    quality_results_path: Path,
    business_rule_results_path: Path,
    schema_contract_results_path: Path,
    privacy_results_path: Path,
    published_monitoring_results_path: Path,
) -> list[ScorecardMetric]:
    metrics: list[ScorecardMetric] = []
    curated_quality = read_csv_fn(quality_results_path)
    if not curated_quality.empty:
        score, total, failed = score_from_checks(curated_quality)
        metrics.append(ScorecardMetric("fact_orders_enriched", "data_quality", score, status_from_score(score), str(quality_results_path), total, failed))

    business_rules = read_csv_fn(business_rule_results_path)
    if not business_rules.empty:
        score, total, failed = score_from_checks(business_rules)
        metrics.append(ScorecardMetric("fact_orders_enriched", "business_rules", score, status_from_score(score), str(business_rule_results_path), total, failed))

    schema_contracts = read_csv_fn(schema_contract_results_path)
    if not schema_contracts.empty and {"dataset_name", "status"}.issubset(schema_contracts.columns):
        for dataset_name, slice_df in schema_contracts.groupby("dataset_name"):
            score, total, failed = score_from_checks(slice_df)
            metrics.append(ScorecardMetric(str(dataset_name), "schema_contracts", score, status_from_score(score), str(schema_contract_results_path), total, failed))

    privacy_results = read_csv_fn(privacy_results_path)
    if not privacy_results.empty:
        score, total, failed = score_from_checks(privacy_results)
        metrics.append(ScorecardMetric("fact_orders_dashboard", "privacy_governance", score, status_from_score(score), str(privacy_results_path), total, failed))

    published_monitoring = read_csv_fn(published_monitoring_results_path)
    if not published_monitoring.empty:
        score, total, failed = score_from_checks(published_monitoring)
        metrics.append(ScorecardMetric("fact_orders_dashboard", "published_monitoring", score, status_from_score(score), str(published_monitoring_results_path), total, failed))
    return metrics


def build_dataset_scorecards(metrics: list[ScorecardMetric]) -> list[DatasetScorecard]:
    if not metrics:
        return []
    by_dataset: dict[str, list[ScorecardMetric]] = {}
    for metric in metrics:
        by_dataset.setdefault(metric.dataset_name, []).append(metric)
    scorecards: list[DatasetScorecard] = []
    for dataset_name, dataset_metrics in sorted(by_dataset.items()):
        score = round(sum(metric.score for metric in dataset_metrics) / len(dataset_metrics), 2)
        scorecards.append(DatasetScorecard(dataset_name, score, status_from_score(score)))
    return scorecards
