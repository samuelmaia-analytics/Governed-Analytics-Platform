from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.governance_types import DataQualityCheck, DataQualityResult


def _is_probably_date_column(column_name: str, series: pd.Series) -> bool:
    lowered = column_name.lower()
    if any(token in lowered for token in ["date", "data", "timestamp", "dt_"]):
        return True
    return pd.api.types.is_datetime64_any_dtype(series)


def _check_negative_numeric_values(df: pd.DataFrame) -> list[DataQualityCheck]:
    checks: list[DataQualityCheck] = []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    guarded_keywords = ("revenue", "price", "value", "amount", "qty", "quant", "score", "total", "freight")
    for column in numeric_cols:
        if not any(keyword in column.lower() for keyword in guarded_keywords):
            continue
        negative_rows = int((df[column].fillna(0) < 0).sum())
        checks.append(
            {
                "check_name": f"negative_values__{column}",
                "status": "FAIL" if negative_rows > 0 else "PASS",
                "severity": "medium" if negative_rows > 0 else "low",
                "affected_columns": column,
                "affected_rows": negative_rows,
                "recommendation": "Validate business rule and fix negative values or document accepted exceptions.",
            }
        )
    return checks


def _check_future_dates(df: pd.DataFrame) -> list[DataQualityCheck]:
    checks: list[DataQualityCheck] = []
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    for column in df.columns:
        series = df[column]
        if not _is_probably_date_column(column, series):
            continue
        date_series = pd.to_datetime(series, errors="coerce").dt.tz_localize(None)
        affected_rows = int((date_series > now).sum())
        checks.append(
            {
                "check_name": f"future_dates__{column}",
                "status": "FAIL" if affected_rows > 0 else "PASS",
                "severity": "medium" if affected_rows > 0 else "low",
                "affected_columns": column,
                "affected_rows": affected_rows,
                "recommendation": "Correct reference dates or ensure timezone/calendar conventions are applied.",
            }
        )
    return checks


def run_data_quality_checks(df: pd.DataFrame) -> DataQualityResult:
    total_rows = int(len(df))
    total_columns = int(df.shape[1])
    null_pct_by_column = {
        str(column): float(value)
        for column, value in (df.isna().mean() * 100).round(2).sort_values(ascending=False).to_dict().items()
    }
    high_null_columns = [str(column) for column, pct in null_pct_by_column.items() if pct > 30.0]
    duplicate_rows = int(df.duplicated().sum())
    dtype_summary = {str(column): str(dtype) for column, dtype in df.dtypes.items()}
    cardinality = {str(column): int(value) for column, value in df.nunique(dropna=False).to_dict().items()}
    possible_unique_keys = [column for column, unique_count in cardinality.items() if unique_count == total_rows and total_rows > 0]
    constant_columns = [column for column, unique_count in cardinality.items() if unique_count <= 1]

    checks: list[DataQualityCheck] = [
        {
            "check_name": "high_null_columns_over_30pct",
            "status": "FAIL" if high_null_columns else "PASS",
            "severity": "high" if high_null_columns else "low",
            "affected_columns": ", ".join(high_null_columns) if high_null_columns else "",
            "affected_rows": total_rows if high_null_columns else 0,
            "recommendation": "Review source completeness and enforce mandatory fields for critical columns.",
        },
        {
            "check_name": "duplicate_rows",
            "status": "FAIL" if duplicate_rows > 0 else "PASS",
            "severity": "high" if duplicate_rows > 0 else "low",
            "affected_columns": "",
            "affected_rows": duplicate_rows,
            "recommendation": "Remove duplicates and validate ingestion keys/grain assumptions.",
        },
        {
            "check_name": "constant_columns",
            "status": "FAIL" if constant_columns else "PASS",
            "severity": "medium" if constant_columns else "low",
            "affected_columns": ", ".join(constant_columns) if constant_columns else "",
            "affected_rows": total_rows if constant_columns else 0,
            "recommendation": "Drop or review constant columns to simplify the analytical model.",
        },
    ]
    checks.extend(_check_negative_numeric_values(df))
    checks.extend(_check_future_dates(df))

    failed_checks = [check for check in checks if check["status"] == "FAIL"]
    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "null_pct_by_column": null_pct_by_column,
        "columns_over_30pct_null": high_null_columns,
        "duplicate_rows": duplicate_rows,
        "dtypes": dtype_summary,
        "cardinality": cardinality,
        "possible_unique_keys": possible_unique_keys,
        "constant_columns": constant_columns,
        "checks": checks,
        "failed_checks_count": len(failed_checks),
    }


def generate_data_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    quality_results = run_data_quality_checks(df)
    checks = quality_results["checks"]
    return pd.DataFrame(checks)
