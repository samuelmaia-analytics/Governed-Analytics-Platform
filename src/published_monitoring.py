from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import requests

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PUBLISHED_DASHBOARD_DIR, PUBLISHED_MONITORING_DIR
from src.ingest import configure_logging
from src.monitoring_components import alerting as _alerting
from src.monitoring_components import checks as _checks
from src.monitoring_components import outputs as _outputs
from src.monitoring_components import pipeline as _pipeline
from src.monitoring_components.models import AlertDispatchResult, MonitoringCheckResult

LOGGER = logging.getLogger(__name__)
PUBLISHED_PARQUET_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
RESULTS_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
SUMMARY_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.json"
REPORT_PATH = DOCS_DIR / "reports" / "published_layer_monitoring.md"
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
CRITICAL_COLUMNS = [
    "order_id",
    "order_item_id",
    "seller_key",
    "order_purchase_timestamp",
    "price",
    "freight_value",
]
DEFAULT_MAX_FRESHNESS_HOURS = 36
MIN_ROWS = 100_001
MAX_MISSING_SELLER_DELAY_RATE_PCT = 1.0
DEFAULT_ALERT_SOURCE = "published_layer_monitoring"


def build_result(
    check_name: str,
    passed: bool,
    metric_value: float | str,
    threshold: float | str,
    severity: str,
    details: str,
) -> MonitoringCheckResult:
    return _checks.build_result(
        check_name, passed, metric_value, threshold, severity, details
    )


def load_published_table(path: Path | None = None) -> pd.DataFrame:
    path = path or PUBLISHED_PARQUET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Camada publicada nao encontrada: {path}")
    df = pd.read_parquet(path)
    if df.empty:
        raise ValueError("Camada publicada vazia.")
    return df


def check_file_freshness(
    path: Path, *, max_freshness_hours: int
) -> MonitoringCheckResult:
    return _checks.check_file_freshness(
        path, max_freshness_hours=max_freshness_hours
    )


def check_expected_schema(df: pd.DataFrame) -> MonitoringCheckResult:
    return _checks.check_expected_schema(df, expected_columns=EXPECTED_COLUMNS)


def check_primary_key_duplicates(df: pd.DataFrame) -> MonitoringCheckResult:
    return _checks.check_primary_key_duplicates(df)


def check_row_volume(df: pd.DataFrame) -> MonitoringCheckResult:
    return _checks.check_row_volume(df, min_rows=MIN_ROWS)


def check_critical_nulls(df: pd.DataFrame) -> list[MonitoringCheckResult]:
    return _checks.check_critical_nulls(df, critical_columns=CRITICAL_COLUMNS)


def check_semantic_coverage(df: pd.DataFrame) -> list[MonitoringCheckResult]:
    return _checks.check_semantic_coverage(
        df,
        max_missing_seller_delay_rate_pct=MAX_MISSING_SELLER_DELAY_RATE_PCT,
    )


def run_monitoring(
    *, max_freshness_hours: int = DEFAULT_MAX_FRESHNESS_HOURS
) -> list[MonitoringCheckResult]:
    return _pipeline.run_monitoring(
        max_freshness_hours=max_freshness_hours,
        published_path=PUBLISHED_PARQUET_PATH,
        load_published_table_fn=load_published_table,
        check_file_freshness_fn=check_file_freshness,
        check_expected_schema_fn=check_expected_schema,
        check_primary_key_duplicates_fn=check_primary_key_duplicates,
        check_row_volume_fn=check_row_volume,
        check_critical_nulls_fn=check_critical_nulls,
        check_semantic_coverage_fn=check_semantic_coverage,
    )


def build_alert_payload(
    results: list[MonitoringCheckResult],
    *,
    source: str = DEFAULT_ALERT_SOURCE,
    environment: str = "prod",
) -> dict[str, object]:
    return _alerting.build_alert_payload(
        results, source=source, environment=environment
    )


def send_external_alert(
    results: list[MonitoringCheckResult],
    *,
    webhook_url: str,
    token: str | None = None,
    environment: str = "prod",
    source: str = DEFAULT_ALERT_SOURCE,
    timeout_seconds: int = 15,
) -> AlertDispatchResult:
    return _alerting.send_external_alert(
        results,
        webhook_url=webhook_url,
        token=token,
        environment=environment,
        source=source,
        timeout_seconds=timeout_seconds,
        post_fn=requests.post,
    )


def save_results(results: list[MonitoringCheckResult]) -> tuple[Path, Path]:
    return _outputs.save_results(
        results,
        monitoring_dir=PUBLISHED_MONITORING_DIR,
        results_path=RESULTS_PATH,
        summary_path=SUMMARY_PATH,
    )


def render_report(results: list[MonitoringCheckResult]) -> str:
    return _outputs.render_report(results)


def save_report(results: list[MonitoringCheckResult]) -> Path:
    return _outputs.save_report(
        render_report(results), docs_dir=DOCS_DIR, report_path=REPORT_PATH
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitora freshness e qualidade da camada published."
    )
    parser.add_argument(
        "--max-freshness-hours", type=int, default=DEFAULT_MAX_FRESHNESS_HOURS
    )
    parser.add_argument("--fail-on-alert", action="store_true")
    parser.add_argument(
        "--alert-webhook-url", default=os.getenv("EXTERNAL_ALERT_WEBHOOK_URL", "")
    )
    parser.add_argument(
        "--alert-webhook-token", default=os.getenv("EXTERNAL_ALERT_WEBHOOK_TOKEN", "")
    )
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
