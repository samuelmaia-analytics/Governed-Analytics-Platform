from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PUBLISHED_DASHBOARD_DIR, PUBLISHED_MONITORING_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
PUBLISHED_PARQUET_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
RESULTS_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
SUMMARY_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.json"
HISTORY_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring_history.csv"
REPORT_PATH = DOCS_DIR / "published_layer_monitoring.md"
EXPECTED_COLUMNS = {
    "order_id",
    "order_item_id",
    "customer_unique_id",
    "order_purchase_timestamp",
    "purchase_cohort_month",
    "customer_order_sequence",
    "is_first_order",
    "seller_key",
    "seller_volume_tier",
    "seller_delay_rate",
    "delivery_time_days",
    "seller_dispatch_time_days",
    "carrier_delivery_time_days",
    "estimated_delay_days",
    "is_delayed",
    "price",
    "freight_value",
    "freight_to_price_ratio",
    "total_item_value",
}
CRITICAL_COLUMNS = ["order_id", "order_item_id", "seller_key", "order_purchase_timestamp", "price", "freight_value"]
DEFAULT_MAX_FRESHNESS_HOURS = 36
MIN_ROWS = 100_001
MAX_MISSING_SELLER_DELAY_RATE_PCT = 1.0
DEFAULT_ALERT_SOURCE = "published_layer_monitoring"
MIN_PERIODS_FOR_ANOMALY_CHECK = 4
REVENUE_ANOMALY_MAX_DELTA_PCT = 35.0
ORDERS_ANOMALY_MAX_DELTA_PCT = 30.0
DELAY_RATE_MAX_DELTA_PCT_POINTS = 5.0


@dataclass
class MonitoringCheckResult:
    check_name: str
    status: str
    metric_value: float | str
    threshold: float | str
    severity: str
    details: str


@dataclass
class AlertDispatchResult:
    delivered: bool
    status_code: int | None
    destination: str


@dataclass(frozen=True)
class PublishedHealthScore:
    score: int
    status: str
    failed_checks: int
    max_severity: str
    main_risk: str


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


def load_published_table(path: Path | None = None) -> pd.DataFrame:
    path = path or PUBLISHED_PARQUET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Camada publicada nao encontrada: {path}")
    df = pd.read_parquet(path)
    if df.empty:
        raise ValueError("Camada publicada vazia.")
    return df


def check_file_freshness(path: Path, *, max_freshness_hours: int) -> MonitoringCheckResult:
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = round((datetime.now(timezone.utc) - modified_at).total_seconds() / 3600, 2)
    return build_result(
        "published_file_freshness_hours",
        age_hours <= max_freshness_hours,
        age_hours,
        max_freshness_hours,
        "high",
        f"Ultima modificacao UTC: {modified_at.isoformat()}",
    )


def check_expected_schema(df: pd.DataFrame) -> MonitoringCheckResult:
    missing_columns = sorted(EXPECTED_COLUMNS.difference(df.columns))
    return build_result(
        "published_expected_schema",
        not missing_columns,
        len(missing_columns),
        0,
        "high",
        f"Colunas ausentes: {missing_columns if missing_columns else 'nenhuma'}",
    )


def check_primary_key_duplicates(df: pd.DataFrame) -> MonitoringCheckResult:
    duplicate_count = int(df.duplicated(subset=["order_id", "order_item_id"], keep=False).sum())
    return build_result(
        "published_primary_key_duplicates",
        duplicate_count == 0,
        duplicate_count,
        0,
        "high",
        "Duplicidades na granularidade publicada `order_id + order_item_id`.",
    )


def check_row_volume(df: pd.DataFrame) -> MonitoringCheckResult:
    return build_result(
        "published_min_rows",
        len(df) >= MIN_ROWS,
        int(len(df)),
        MIN_ROWS,
        "high",
        "Volume minimo esperado para a camada publicada.",
    )


def check_critical_nulls(df: pd.DataFrame) -> list[MonitoringCheckResult]:
    results: list[MonitoringCheckResult] = []
    for column in CRITICAL_COLUMNS:
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


def check_semantic_coverage(df: pd.DataFrame) -> list[MonitoringCheckResult]:
    missing_semantic_columns = [
        column for column in ("purchase_cohort_month", "seller_delay_rate") if column not in df.columns
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
    cohort_missing_pct = round(float(df["purchase_cohort_month"].isna().mean() * 100), 2)
    seller_delay_missing_pct = round(float(df["seller_delay_rate"].isna().mean() * 100), 2)
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
            seller_delay_missing_pct <= MAX_MISSING_SELLER_DELAY_RATE_PCT,
            seller_delay_missing_pct,
            MAX_MISSING_SELLER_DELAY_RATE_PCT,
            "medium",
            "Cobertura da semantica de seller.",
        ),
    ]


def build_monthly_operational_metrics(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = {"order_purchase_timestamp", "order_id", "total_item_value", "is_delayed"}
    if not required_columns.issubset(df.columns):
        return pd.DataFrame()
    monthly = df.copy()
    monthly["month_start"] = pd.to_datetime(monthly["order_purchase_timestamp"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    monthly = monthly.dropna(subset=["month_start"])
    metrics = (
        monthly.groupby("month_start", as_index=False)
        .agg(
            revenue_gross=("total_item_value", "sum"),
            orders=("order_id", "nunique"),
            delayed_orders_pct=("is_delayed", "mean"),
        )
        .sort_values("month_start")
    )
    metrics["avg_ticket"] = metrics["revenue_gross"] / metrics["orders"].replace(0, pd.NA)
    metrics["delayed_orders_pct"] = pd.to_numeric(metrics["delayed_orders_pct"], errors="coerce").mul(100)
    return metrics


def check_recent_anomalies(df: pd.DataFrame) -> list[MonitoringCheckResult]:
    monthly = build_monthly_operational_metrics(df)
    if monthly.empty or len(monthly) < MIN_PERIODS_FOR_ANOMALY_CHECK:
        return []

    latest = monthly.iloc[-1]
    history = monthly.iloc[:-1]
    results: list[MonitoringCheckResult] = []

    def relative_check(
        *,
        check_name: str,
        current_value: float,
        baseline_value: float,
        threshold: float,
        details: str,
    ) -> MonitoringCheckResult:
        delta_pct = 0.0 if baseline_value == 0 else abs(((current_value / baseline_value) - 1) * 100)
        return build_result(
            check_name,
            delta_pct <= threshold,
            round(delta_pct, 2),
            threshold,
            "medium",
            details,
        )

    revenue_baseline = float(history["revenue_gross"].median())
    results.append(
        relative_check(
            check_name="published_anomaly__revenue_gross_latest_month_delta_pct",
            current_value=float(latest["revenue_gross"]),
            baseline_value=revenue_baseline,
            threshold=REVENUE_ANOMALY_MAX_DELTA_PCT,
            details="Variação da receita do mês mais recente contra a mediana histórica anterior.",
        )
    )

    orders_baseline = float(history["orders"].median())
    results.append(
        relative_check(
            check_name="published_anomaly__orders_latest_month_delta_pct",
            current_value=float(latest["orders"]),
            baseline_value=orders_baseline,
            threshold=ORDERS_ANOMALY_MAX_DELTA_PCT,
            details="Variação do volume de pedidos do mês mais recente contra a mediana histórica anterior.",
        )
    )

    delay_baseline = float(history["delayed_orders_pct"].median())
    delay_current = float(latest["delayed_orders_pct"])
    delay_delta = max(0.0, round(delay_current - delay_baseline, 2))
    results.append(
        build_result(
            "published_anomaly__delay_rate_latest_month_delta_pct_points",
            delay_delta <= DELAY_RATE_MAX_DELTA_PCT_POINTS,
            delay_delta,
            DELAY_RATE_MAX_DELTA_PCT_POINTS,
            "medium",
            "Aumento da taxa de atraso do mês mais recente contra a mediana histórica anterior.",
        )
    )
    return results
def run_monitoring(*, max_freshness_hours: int = DEFAULT_MAX_FRESHNESS_HOURS) -> list[MonitoringCheckResult]:
    df = load_published_table()
    results = [check_file_freshness(PUBLISHED_PARQUET_PATH, max_freshness_hours=max_freshness_hours)]
    results.append(check_expected_schema(df))
    results.append(check_primary_key_duplicates(df))
    results.append(check_row_volume(df))
    results.extend(check_critical_nulls(df))
    results.extend(check_semantic_coverage(df))
    results.extend(check_recent_anomalies(df))
    return results


def build_health_score(results: list[MonitoringCheckResult]) -> PublishedHealthScore:
    failed_results = [result for result in results if result.status == "FAIL"]
    if not failed_results:
        return PublishedHealthScore(
            score=100,
            status="healthy",
            failed_checks=0,
            max_severity="low",
            main_risk="none",
        )

    severity_penalty = {"high": 15, "medium": 7, "low": 3}
    severity_order = {"high": 3, "medium": 2, "low": 1}
    penalty = sum(severity_penalty.get(result.severity, 5) for result in failed_results)
    score = max(0, 100 - penalty)
    if score >= 90:
        status = "healthy_with_warnings"
    elif score >= 70:
        status = "attention_required"
    else:
        status = "critical"
    max_severity = max(failed_results, key=lambda result: severity_order.get(result.severity, 0)).severity
    main_risk = failed_results[0].check_name
    return PublishedHealthScore(
        score=score,
        status=status,
        failed_checks=len(failed_results),
        max_severity=max_severity,
        main_risk=main_risk,
    )


def build_alert_payload(
    results: list[MonitoringCheckResult],
    *,
    source: str = DEFAULT_ALERT_SOURCE,
    environment: str = "prod",
) -> dict[str, object]:
    failed_results = [result for result in results if result.status == "FAIL"]
    severity_order = {"high": 3, "medium": 2, "low": 1}
    max_severity = "low"
    if failed_results:
        max_severity = max(failed_results, key=lambda result: severity_order.get(result.severity, 0)).severity
    return {
        "source": source,
        "environment": environment,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failed_results else "PASS",
        "failed_checks": len(failed_results),
        "max_severity": max_severity,
        "results": [asdict(result) for result in failed_results],
    }


def send_external_alert(
    results: list[MonitoringCheckResult],
    *,
    webhook_url: str,
    token: str | None = None,
    environment: str = "prod",
    source: str = DEFAULT_ALERT_SOURCE,
    timeout_seconds: int = 15,
) -> AlertDispatchResult:
    payload = build_alert_payload(results, source=source, environment=environment)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    response = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout_seconds)
    response.raise_for_status()
    return AlertDispatchResult(
        delivered=True,
        status_code=response.status_code,
        destination=webhook_url,
    )


def save_health_history(
    *,
    generated_at_utc: str,
    results: list[MonitoringCheckResult],
    health_score: PublishedHealthScore,
) -> Path:
    ensure_directory(PUBLISHED_MONITORING_DIR)
    history_entry = pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at_utc,
                "health_score": health_score.score,
                "health_status": health_score.status,
                "failed_checks": health_score.failed_checks,
                "total_checks": len(results),
                "max_severity": health_score.max_severity,
                "main_risk": health_score.main_risk,
            }
        ]
    )
    if HISTORY_PATH.exists():
        history_df = pd.read_csv(HISTORY_PATH)
        history_df = pd.concat([history_df, history_entry], ignore_index=True)
        history_df = history_df.drop_duplicates(subset=["generated_at_utc"], keep="last")
    else:
        history_df = history_entry
    history_df = history_df.sort_values("generated_at_utc")
    history_df.to_csv(HISTORY_PATH, index=False)
    return HISTORY_PATH


def save_results(results: list[MonitoringCheckResult]) -> tuple[Path, Path]:
    ensure_directory(PUBLISHED_MONITORING_DIR)
    results_df = pd.DataFrame(asdict(result) for result in results)
    health_score = build_health_score(results)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    results_df.to_csv(RESULTS_PATH, index=False)
    save_health_history(generated_at_utc=generated_at_utc, results=results, health_score=health_score)
    SUMMARY_PATH.write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at_utc,
                "total_checks": len(results),
                "failed_checks": int((results_df["status"] == "FAIL").sum()),
                "health_score": asdict(health_score),
                "results": [asdict(result) for result in results],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return RESULTS_PATH, SUMMARY_PATH


def render_report(results: list[MonitoringCheckResult]) -> str:
    results_df = pd.DataFrame(asdict(result) for result in results)
    failed_df = results_df[results_df["status"] == "FAIL"]
    health_score = build_health_score(results)
    lines = [
        "# Monitoramento da Camada Published",
        "",
        "Relatorio recorrente de freshness e qualidade da camada `fact_orders_dashboard`.",
        "",
        "## Resumo",
        "",
        f"- Checks executados: **{len(results)}**",
        f"- Checks aprovados: **{int((results_df['status'] == 'PASS').sum())}**",
        f"- Checks reprovados: **{int((results_df['status'] == 'FAIL').sum())}**",
        f"- Health score da camada publicada: **{health_score.score}/100**",
        f"- Status de saúde: **{health_score.status}**",
        f"- Risco principal: **{health_score.main_risk}**",
        "",
        "## Resultado dos Checks",
        "",
        "| Check | Status | Valor | Threshold | Severidade |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in results_df.itertuples(index=False):
        lines.append(
            f"| `{row.check_name}` | **{row.status}** | {row.metric_value} | {row.threshold} | {row.severity} |"
        )
    lines.extend(["", "## Alertas", ""])
    if failed_df.empty:
        lines.append("- Nenhum alerta aberto na execucao atual.")
    else:
        for row in failed_df.itertuples(index=False):
            lines.append(f"- `{row.check_name}`: {row.details} Valor observado={row.metric_value}.")
    if HISTORY_PATH.exists():
        history_df = pd.read_csv(HISTORY_PATH).tail(5)
        lines.extend(["", "## Tendência recente de saúde", "", "| Data UTC | Score | Status | Falhas | Risco principal |", "| --- | ---: | --- | ---: | --- |"])
        for row in history_df.itertuples(index=False):
            lines.append(
                f"| `{row.generated_at_utc}` | {row.health_score} | {row.health_status} | {row.failed_checks} | `{row.main_risk}` |"
            )
    return "\n".join(lines) + "\n"


def save_report(results: list[MonitoringCheckResult]) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(results), encoding="utf-8")
    return REPORT_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitora freshness e qualidade da camada published.")
    parser.add_argument("--max-freshness-hours", type=int, default=DEFAULT_MAX_FRESHNESS_HOURS)
    parser.add_argument("--fail-on-alert", action="store_true")
    parser.add_argument("--alert-webhook-url", default=os.getenv("EXTERNAL_ALERT_WEBHOOK_URL", ""))
    parser.add_argument("--alert-webhook-token", default=os.getenv("EXTERNAL_ALERT_WEBHOOK_TOKEN", ""))
    parser.add_argument("--alert-environment", default=os.getenv("APP_ENV", "prod"))
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    results = run_monitoring(max_freshness_hours=args.max_freshness_hours)
    save_results(results)
    save_report(results)
    failed_count = sum(result.status == "FAIL" for result in results)
    LOGGER.info("Monitoramento da camada publicada concluido | falhas=%s", failed_count)
    if failed_count and args.alert_webhook_url:
        dispatch = send_external_alert(
            results,
            webhook_url=args.alert_webhook_url,
            token=args.alert_webhook_token or None,
            environment=args.alert_environment,
        )
        LOGGER.info(
            "Alerta externo enviado | destino=%s status_code=%s",
            dispatch.destination,
            dispatch.status_code,
        )
    if args.fail_on_alert and failed_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
