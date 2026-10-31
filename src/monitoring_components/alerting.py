from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Protocol

from src.monitoring_components.models import AlertDispatchResult, MonitoringCheckResult


class ResponseLike(Protocol):
    status_code: int

    def raise_for_status(self) -> None: ...


def build_alert_payload(
    results: list[MonitoringCheckResult],
    *,
    source: str = "published_layer_monitoring",
    environment: str = "prod",
) -> dict[str, object]:
    failed_results = [result for result in results if result.status == "FAIL"]
    severity_order = {"high": 3, "medium": 2, "low": 1}
    max_severity = "low"
    if failed_results:
        max_severity = max(
            failed_results, key=lambda result: severity_order.get(result.severity, 0)
        ).severity
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
    source: str = "published_layer_monitoring",
    timeout_seconds: int = 15,
    post_fn: Callable[..., ResponseLike],
) -> AlertDispatchResult:
    payload = build_alert_payload(results, source=source, environment=environment)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    response = post_fn(
        webhook_url, json=payload, headers=headers, timeout=timeout_seconds
    )
    response.raise_for_status()
    return AlertDispatchResult(
        delivered=True,
        status_code=response.status_code,
        destination=webhook_url,
    )
