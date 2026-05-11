from __future__ import annotations

import math

import numpy as np
import pandas as pd


def dataset_overview(df: pd.DataFrame) -> dict[str, object]:
    return {
        "total_rows": int(len(df)),
        "total_columns": int(df.shape[1]),
        "numeric_columns": int(df.select_dtypes(include=["number"]).shape[1]),
        "categorical_columns": int(
            df.select_dtypes(include=["object", "category"]).shape[1]
        ),
        "datetime_columns": int(
            df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).shape[1]
        ),
    }


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.describe(include="all").transpose()
    return summary.where(summary.notna(), "")


def dtype_distribution(df: pd.DataFrame) -> pd.DataFrame:
    dist = df.dtypes.astype(str).value_counts().reset_index()
    dist.columns = ["dtype", "count"]
    dist["percentage"] = (
        (dist["count"] / len(df.columns) * 100).round(2) if len(df.columns) else 0.0
    )
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


def generate_storytelling_insights(df: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    if df.empty:
        return insights

    nulls = null_profile(df)
    if not nulls.empty:
        top_null = nulls.iloc[0]
        if float(top_null["null_pct"]) > 0:
            insights.append(
                f"Highest null concentration is `{top_null['column_name']}` with {float(top_null['null_pct']):.1f}% missing values."
            )

    categories = top_categories(df, top_n=1)
    if not categories.empty:
        top_cat = categories.sort_values("count", ascending=False).iloc[0]
        insights.append(
            f"Top category concentration: `{top_cat['column_name']}` = `{top_cat['category']}` with {int(top_cat['count'])} rows ({float(top_cat['percentage']):.1f}%)."
        )

    outliers = detect_outliers_iqr(df)
    if not outliers.empty:
        top_outlier = outliers.sort_values("outlier_pct", ascending=False).iloc[0]
        if float(top_outlier["outlier_pct"]) > 0:
            insights.append(
                f"Strongest outlier signal appears in `{top_outlier['column_name']}` ({float(top_outlier['outlier_pct']):.1f}% rows outside IQR bounds)."
            )

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr(numeric_only=True).abs()
        np.fill_diagonal(corr.values, np.nan)
        stacked = corr.stack()
        if not stacked.empty:
            best_pair = stacked.idxmax()
            best_value = float(stacked.max())
            insights.append(
                f"Highest numeric correlation is between `{best_pair[0]}` and `{best_pair[1]}` (|r|={best_value:.2f})."
            )

    return insights


def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    numeric_df = df.select_dtypes(include=["number"])
    for column in numeric_df.columns[:5]:
        series = numeric_df[column].dropna().astype(float)
        n = int(series.shape[0])
        if n < 8:
            continue
        centered = series - series.mean()
        variance = float((centered**2).mean())
        if variance == 0:
            continue
        skew = float(((centered**3).mean()) / (variance ** 1.5))
        kurt = float(((centered**4).mean()) / (variance**2))
        jb_stat = (n / 6.0) * (skew**2 + ((kurt - 3.0) ** 2) / 4.0)
        # For chi-square(df=2), survival function is exp(-x/2).
        p_value = float(math.exp(-jb_stat / 2.0))
        rows.append(
            {
                "test_name": "jarque_bera_normality",
                "target": column,
                "statistic": round(jb_stat, 4),
                "p_value": round(p_value, 6),
                "interpretation": "non_normal"
                if p_value < 0.05
                else "cannot_reject_normality",
            }
        )

    if numeric_df.shape[1] >= 2 and len(numeric_df) >= 8:
        corr = numeric_df.corr(numeric_only=True).abs()
        np.fill_diagonal(corr.values, np.nan)
        stacked = corr.stack()
        if not stacked.empty:
            col_x, col_y = stacked.idxmax()
            pair = numeric_df[[col_x, col_y]].dropna()
            n = len(pair)
            if n >= 8:
                r = float(pair[col_x].corr(pair[col_y]))
                clamped_r = min(max(r, -0.999999), 0.999999)
                z = 0.5 * math.log((1 + clamped_r) / (1 - clamped_r)) * math.sqrt(n - 3)
                p_value = float(math.erfc(abs(z) / math.sqrt(2)))
                rows.append(
                    {
                        "test_name": "pearson_correlation_significance",
                        "target": f"{col_x}~{col_y}",
                        "statistic": round(r, 4),
                        "p_value": round(p_value, 6),
                        "interpretation": "significant_correlation"
                        if p_value < 0.05
                        else "weak_evidence",
                    }
                )

    return pd.DataFrame(rows)
