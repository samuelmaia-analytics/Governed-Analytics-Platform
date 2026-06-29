from __future__ import annotations

# ruff: noqa: E402, I001

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from n8n_utils import load_config
from src.ingest import configure_logging
from src.run_platform_pipeline import (
    build_run_metadata,
    resolve_steps,
    run_selected_steps,
    save_pipeline_execution_report,
)


def _configured_steps(config: dict[str, object]) -> list[str] | None:
    steps = config.get("pipeline", {}).get("default_steps")
    if not steps:
        return None
    return [str(step) for step in steps]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="n8n wrapper for the governed pipeline.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    parser.add_argument("--steps", nargs="*", help="Optional explicit pipeline steps.")
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(PROJECT_ROOT / args.config)
    configured_continue = bool(config.get("pipeline", {}).get("continue_on_error", False))
    continue_on_error = args.continue_on_error or configured_continue
    selected_steps = resolve_steps(args.steps or _configured_steps(config))

    configure_logging()
    started_at = datetime.now(UTC)
    started_timer = perf_counter()
    executions = []
    status = "success"
    error_message = ""

    try:
        executions = run_selected_steps(
            selected_steps, continue_on_error=continue_on_error
        )
    except Exception as exc:
        status = "failed"
        error_message = str(exc)
        raise
    finally:
        completed_at = datetime.now(UTC)
        metadata = build_run_metadata(started_at, completed_at)
        results_path, report_path = save_pipeline_execution_report(
            selected_steps, executions, metadata
        )
        payload = {
            "status": status,
            "error_message": error_message,
            "run_id": metadata.run_id,
            "duration_seconds": round(perf_counter() - started_timer, 2),
            "selected_steps": selected_steps,
            "results_path": str(results_path),
            "report_path": str(report_path),
        }
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
