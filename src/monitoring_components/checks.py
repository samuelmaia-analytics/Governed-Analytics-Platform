from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.monitoring_components.models import MonitoringCheckResult


def build_result(
    check_name: str,
    passed: bool,
    metric_value: float | str,
    threshold: float | str,
    severity: str,
    details: str,
) -> MonitoringCheckResult:
    return MonitoringCheckResult(
        check_name=check_name,
        status="PASS" if passed else "FAIL",
        metric_value=metric_value,
        threshold=threshold,
        severity=severity,
        details=details,
    )


def check_file_freshness(
    path: Path, *, max_freshness_hours: int
) -> MonitoringCheckResult:
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = round(
        (datetime.now(timezone.utc) - modified_at).total_seconds() / 3600, 2
    )
    return build_result(
        "published_file_freshness_hours",
        age_hours <= max_freshness_hours,
        age_hours,
        max_freshness_hours,
        "high",
        f"Ultima modificacao UTC: {modified_at.isoformat()}",
    )


def check_expected_schema(
    df: pd.DataFrame, *, expected_columns: set[str]
) -> MonitoringCheckResult:
    missing_columns = sorted(expected_columns.difference(df.columns))
    return build_result(
        "published_expected_schema",
        not missing_columns,
        len(missing_columns),
        0,
        "high",
        f"Colunas ausentes: {missing_columns if missing_columns else 'nenhuma'}",
    )


def check_primary_key_duplicates(df: pd.DataFrame) -> MonitoringCheckResult:
    duplicate_count = int(
        df.duplicated(subset=["order_id", "order_item_id"], keep=False).sum()
    )
    return build_result(
        "published_primary_key_duplicates",
        duplicate_count == 0,
        duplicate_count,
        0,
        "high",
        "Duplicidades na granularidade publicada `order_id + order_item_id`.",
    )


def check_row_volume(
    df: pd.DataFrame, *, min_rows: int
) -> MonitoringCheckResult:
    return build_result(
        "published_min_rows",
        len(df) >= min_rows,
        int(len(df)),
        min_rows,
        "high",
        "Volume minimo esperado para a camada publicada.",
    )


def check_critical_nulls(
    df: pd.DataFrame, *, critical_columns: list[str]
) -> list[MonitoringCheckResult]:
    results: list[MonitoringCheckResult] = []
    for column in critical_columns:
        if column not in df.columns:
            results.append(
                build_result(
                    f"published_critical_nulls__{column}",
                    False,
                    "missing_column",
                    0,
                    "high",
                    f"Coluna critica ausente no schema publicado: `{column}`.",
                )
            )
            continue
        null_count = int(df[column].isna().sum())
        results.append(
            build_result(
                f"published_critical_nulls__{column}",
                null_count == 0,
                null_count,
                0,
                "high",
                f"Nulos observados na coluna `{column}`.",
            )
        )
    return results


def check_semantic_coverage(
    df: pd.DataFrame, *, max_missing_seller_delay_rate_pct: float
) -> list[MonitoringCheckResult]:
    missing_semantic_columns = [
        column
        for column in ("purchase_cohort_month", "seller_delay_rate")
        if column not in df.columns
    ]
    if missing_semantic_columns:
        return [
            build_result(
                "published_semantic_coverage_schema",
                False,
                len(missing_semantic_columns),
                0,
                "high",
                f"Colunas semanticas ausentes: {missing_semantic_columns}",
            )
        ]
    cohort_missing_pct = round(
        float(df["purchase_cohort_month"].isna().mean() * 100), 2
    )
    seller_delay_missing_pct = round(
        float(df["seller_delay_rate"].isna().mean() * 100), 2
    )
    return [
        build_result(
            "published_missing_pct__purchase_cohort_month",
            cohort_missing_pct == 0,
            cohort_missing_pct,
            0,
            "medium",
            "Cobertura da semantica de cohort.",
        ),
        build_result(
            "published_missing_pct__seller_delay_rate",
            seller_delay_missing_pct <= max_missing_seller_delay_rate_pct,
            seller_delay_missing_pct,
            max_missing_seller_delay_rate_pct,
            "medium",
            "Cobertura da semantica de seller.",
        ),
    ]
