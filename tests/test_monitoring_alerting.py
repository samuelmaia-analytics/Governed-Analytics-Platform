from __future__ import annotations

import pytest

from src.monitoring_components import alerting
from src.monitoring_components.models import MonitoringCheckResult


def _results() -> list[MonitoringCheckResult]:
    return [
        MonitoringCheckResult("pass", "PASS", 0, 0, "low", "ok"),
        MonitoringCheckResult("medium", "FAIL", 1, 0, "medium", "warning"),
        MonitoringCheckResult("high", "FAIL", 2, 0, "high", "broken"),
    ]


def test_alert_payload_contains_only_failures_and_highest_severity() -> None:
    payload = alerting.build_alert_payload(
        _results(), source="source", environment="stage"
    )

    assert payload["source"] == "source"
    assert payload["environment"] == "stage"
    assert payload["status"] == "FAIL"
    assert payload["failed_checks"] == 2
    assert payload["max_severity"] == "high"
    assert [item["check_name"] for item in payload["results"]] == [  # type: ignore[index]
        "medium",
        "high",
    ]


def test_send_external_alert_preserves_headers_payload_and_timeout() -> None:
    captured: dict[str, object] = {}

    class Response:
        status_code = 202

        def raise_for_status(self) -> None:
            captured["raised"] = True

    def fake_post(
        url: str, *, json: object, headers: object, timeout: int
    ) -> Response:
        captured.update(url=url, json=json, headers=headers, timeout=timeout)
        return Response()

    result = alerting.send_external_alert(
        _results(),
        webhook_url="https://example.invalid/hook",
        token="secret",
        environment="prod",
        timeout_seconds=9,
        post_fn=fake_post,
    )

    assert result.delivered is True
    assert result.status_code == 202
    assert result.destination == "https://example.invalid/hook"
    assert captured["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "secret",
    }
    assert captured["timeout"] == 9
    assert captured["raised"] is True


def test_send_external_alert_without_token_omits_authorization() -> None:
    captured: dict[str, object] = {}

    class Response:
        status_code = 200

        @staticmethod
        def raise_for_status() -> None:
            return None

    def fake_post(url: str, **kwargs: object) -> Response:
        captured.update(kwargs)
        return Response()

    alerting.send_external_alert(
        [], webhook_url="https://example.invalid", post_fn=fake_post
    )
    assert captured["headers"] == {"Content-Type": "application/json"}


def test_http_errors_are_propagated() -> None:
    class Response:
        status_code = 500

        @staticmethod
        def raise_for_status() -> None:
            raise RuntimeError("HTTP 500")

    with pytest.raises(RuntimeError, match="HTTP 500"):
        alerting.send_external_alert(
            _results(),
            webhook_url="https://example.invalid",
            post_fn=lambda *args, **kwargs: Response(),
        )
