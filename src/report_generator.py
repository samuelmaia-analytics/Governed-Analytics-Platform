from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data_quality import generate_data_quality_table, run_data_quality_checks
from src.eda import dataset_overview
from src.governance_types import DataQualityResult, PrivacyRiskResult
from src.lgpd_classifier import classify_dataframe_columns
from src.privacy_governance_artifacts import (
    build_risk_matrix,
    build_treatment_inventory,
    generate_ripd_markdown,
)
from src.risk_scoring import calculate_privacy_risk_score

DEFAULT_DOCS_DIR = Path("docs")
DEFAULT_REPORTS_DIR = DEFAULT_DOCS_DIR / "reports"
DEFAULT_GOVERNANCE_DIR = DEFAULT_DOCS_DIR / "governance"


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data available._"
    safe_df = df.fillna("")
    headers = [str(column) for column in safe_df.columns]
    separator = ["---"] * len(headers)
    rows: list[list[str]] = []
    for row in safe_df.itertuples(index=False, name=None):
        rows.append([str(value) for value in row])
    lines = [
        f"| {' | '.join(headers)} |",
        f"| {' | '.join(separator)} |",
    ]
    for row_values in rows:
        lines.append(f"| {' | '.join(row_values)} |")
    return "\n".join(lines)


def _build_data_dictionary_markdown(
    df: pd.DataFrame, classification_df: pd.DataFrame
) -> str:
    generated_at = _now_utc_iso()
    dictionary_df = pd.DataFrame(
        {
            "column_name": df.columns,
            "dtype": [str(dtype) for dtype in df.dtypes],
            "null_pct": (df.isna().mean() * 100).round(2).values,
            "distinct_values": [
                int(df[column].nunique(dropna=False)) for column in df.columns
            ],
        }
    ).merge(
        classification_df[["column_name", "lgpd_classification"]],
        on="column_name",
        how="left",
    )
    return "\n".join(
        [
            "# Data Dictionary",
            "",
            f"- Generated at: **{generated_at}**",
            f"- Total rows: **{len(df)}**",
            f"- Total columns: **{df.shape[1]}**",
            "",
            "## Column Dictionary",
            "",
            _markdown_table(dictionary_df),
        ]
    )


def _build_lgpd_controls_markdown(
    df: pd.DataFrame, classification_df: pd.DataFrame, risk_result: PrivacyRiskResult
) -> str:
    generated_at = _now_utc_iso()
    recommendations = "\n".join(f"- {item}" for item in risk_result["recommendations"])
    return "\n".join(
        [
            "# LGPD Controls",
            "",
            f"- Generated at: **{generated_at}**",
            f"- Risk score: **{risk_result['score']} / 100**",
            f"- Risk level: **{risk_result['risk_level']}**",
            "",
            "## Dataset Summary",
            "",
            f"- Total rows: **{len(df)}**",
            f"- Total columns: **{df.shape[1]}**",
            f"- Risk summary: {risk_result['summary']}",
            "",
            "## LGPD Classification by Column",
            "",
            _markdown_table(classification_df),
            "",
            "## Governance Recommendations",
            "",
            recommendations,
        ]
    )


def _build_data_quality_markdown(
    df: pd.DataFrame, quality_table: pd.DataFrame, quality_results: DataQualityResult
) -> str:
    generated_at = _now_utc_iso()
    failed_checks = int(quality_results["failed_checks_count"])
    next_steps = [
        "Prioritize high-severity failed checks and assign owners.",
        "Create remediation SLA for duplicated records and null critical fields.",
        "Automate recurring quality checks in CI/CD and monitoring jobs.",
    ]
    steps_text = "\n".join(f"- {step}" for step in next_steps)
    return "\n".join(
        [
            "# Data Quality Report",
            "",
            f"- Generated at: **{generated_at}**",
            f"- Total rows: **{quality_results['total_rows']}**",
            f"- Total columns: **{quality_results['total_columns']}**",
            f"- Failed checks: **{failed_checks}**",
            "",
            "## Quality Checks",
            "",
            _markdown_table(quality_table),
            "",
            "## Risks Found",
            "",
            f"- Failed checks count: **{failed_checks}**",
            f"- Columns with >30% nulls: **{', '.join(quality_results['columns_over_30pct_null']) or 'none'}**",
            f"- Duplicate rows: **{quality_results['duplicate_rows']}**",
            "",
            "## Next Steps",
            "",
            steps_text,
            "",
            "## Dataset Overview",
            "",
            _markdown_table(pd.DataFrame([dataset_overview(df)])),
        ]
    )


def generate_markdown_reports(
    df: pd.DataFrame, docs_dir: str | Path = DEFAULT_DOCS_DIR
) -> dict[str, Path]:
    docs_path = Path(docs_dir)
    docs_path.mkdir(parents=True, exist_ok=True)
    reports_path = docs_path / "reports"
    governance_path = docs_path / "governance"
    reports_path.mkdir(parents=True, exist_ok=True)
    governance_path.mkdir(parents=True, exist_ok=True)

    classification_df = classify_dataframe_columns(df)
    risk_result = calculate_privacy_risk_score(classification_df, total_rows=len(df))
    quality_results: DataQualityResult = run_data_quality_checks(df)
    quality_table = generate_data_quality_table(df)

    data_dictionary_path = reports_path / "data_dictionary.md"
    lgpd_controls_path = governance_path / "lgpd_controls.md"
    data_quality_path = reports_path / "data_quality_report.md"
    ripd_sample_path = governance_path / "lgpd_ripd_sample.md"

    data_dictionary_path.write_text(
        _build_data_dictionary_markdown(df, classification_df),
        encoding="utf-8",
    )
    lgpd_controls_path.write_text(
        _build_lgpd_controls_markdown(df, classification_df, risk_result),
        encoding="utf-8",
    )
    data_quality_path.write_text(
        _build_data_quality_markdown(df, quality_table, quality_results),
        encoding="utf-8",
    )

    treatment_inventory = build_treatment_inventory("fact_orders_dashboard")
    risk_matrix = build_risk_matrix(classification_df, risk_result, quality_results)
    ripd_sample_path.write_text(
        generate_ripd_markdown(
            dataset_name="fact_orders_dashboard",
            treatment_inventory=treatment_inventory,
            risk_matrix=risk_matrix,
            risk_result=risk_result,
            quality_result=quality_results,
        ),
        encoding="utf-8",
    )

    return {
        "data_dictionary": data_dictionary_path,
        "lgpd_controls": lgpd_controls_path,
        "data_quality_report": data_quality_path,
        "lgpd_ripd_sample": ripd_sample_path,
    }
