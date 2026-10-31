from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.monitoring_components.models import MonitoringCheckResult


def run_monitoring(
    *,
    max_freshness_hours: int,
    published_path: Path,
    load_published_table_fn: Callable[[], pd.DataFrame],
    check_file_freshness_fn: Callable[..., MonitoringCheckResult],
    check_expected_schema_fn: Callable[[pd.DataFrame], MonitoringCheckResult],
    check_primary_key_duplicates_fn: Callable[[pd.DataFrame], MonitoringCheckResult],
    check_row_volume_fn: Callable[[pd.DataFrame], MonitoringCheckResult],
    check_critical_nulls_fn: Callable[[pd.DataFrame], list[MonitoringCheckResult]],
    check_semantic_coverage_fn: Callable[[pd.DataFrame], list[MonitoringCheckResult]],
) -> list[MonitoringCheckResult]:
    df = load_published_table_fn()
    results = [
        check_file_freshness_fn(
            published_path, max_freshness_hours=max_freshness_hours
        )
    ]
    results.append(check_expected_schema_fn(df))
    results.append(check_primary_key_duplicates_fn(df))
    results.append(check_row_volume_fn(df))
    results.extend(check_critical_nulls_fn(df))
    results.extend(check_semantic_coverage_fn(df))
    return results
