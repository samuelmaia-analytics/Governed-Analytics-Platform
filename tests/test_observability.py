from __future__ import annotations

import json
import logging

from src.observability import JsonLogFormatter


def test_json_log_formatter_renders_structured_payload() -> None:
    formatter = JsonLogFormatter()
    record = logging.LogRecord(
        name="src.enterprise",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="pipeline started",
        args=(),
        exc_info=None,
    )
    record.operation = "pipeline_run"
    record.run_id = "run-123"

    payload = json.loads(formatter.format(record))

    assert payload["logger"] == "src.enterprise"
    assert payload["message"] == "pipeline started"
    assert payload["operation"] == "pipeline_run"
    assert payload["run_id"] == "run-123"
