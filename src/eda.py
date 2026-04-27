from __future__ import annotations

import pandas as pd


def dataset_overview(df: pd.DataFrame) -> dict[str, object]:
    return {
        "total_rows": int(len(df)),
        "total_columns": int(df.shape[1]),
        "numeric_columns": int(df.select_dtypes(include=["number"]).shape[1]),
        "categorical_columns": int(df.select_dtypes(include=["object", "category"]).shape[1]),
        "datetime_columns": int(df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).shape[1]),
    }


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.describe(include="all").transpose()
    return summary.where(summary.notna(), "")


def dtype_distribution(df: pd.DataFrame) -> pd.DataFrame:
    dist = df.dtypes.astype(str).value_counts().reset_index()
    dist.columns = ["dtype", "count"]
    dist["percentage"] = (dist["count"] / len(df.columns) * 100).round(2) if len(df.columns) else 0.0
    return dist


def top_categories(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns
    rows: list[dict[str, object]] = []
    for column in categorical_columns:
        counts = df[column].fillna("null").astype(str).value_counts().head(top_n)
        for category, count in counts.items():
            rows.append(
                {
                    "column_name": column,
                    "category": category,
                    "count": int(count),
                    "percentage": round((count / max(len(df), 1)) * 100, 2),
                }
            )
    return pd.DataFrame(rows)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr(numeric_only=True)


def detect_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"])
    rows: list[dict[str, object]] = []
    for column in numeric_df.columns:
        series = numeric_df[column].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = int(((series < lower) | (series > upper)).sum())
        rows.append(
            {
                "column_name": column,
                "q1": float(q1),
                "q3": float(q3),
                "iqr": float(iqr),
                "lower_bound": float(lower),
                "upper_bound": float(upper),
                "outlier_count": outlier_count,
                "outlier_pct": round((outlier_count / max(len(series), 1)) * 100, 2),
            }
        )
    return pd.DataFrame(rows)


def null_profile(df: pd.DataFrame) -> pd.DataFrame:
    null_count = df.isna().sum()
    null_pct = ((null_count / max(len(df), 1)) * 100).round(2)
    profile = pd.DataFrame(
        {
            "column_name": [str(column) for column in null_count.index.tolist()],
            "null_count": null_count.astype(int).tolist(),
            "null_pct": null_pct.astype(float).tolist(),
        }
    )
    return profile.sort_values("null_pct", ascending=False).reset_index(drop=True)
