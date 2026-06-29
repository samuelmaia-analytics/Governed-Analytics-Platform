from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from n8n_utils import load_config

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a pipeline execution log.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    parser.add_argument("--pipeline-name", default="governed_analytics_pipeline")
    parser.add_argument(
        "--status", required=True, choices=["success", "failed", "warning"]
    )
    parser.add_argument("--message", default="")
    parser.add_argument("--source", default="manual")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(PROJECT_ROOT / args.config)
    logging_config = config.get("logging", {})
    log_path = PROJECT_ROOT / logging_config.get(
        "pipeline_log_path", logging_config.get("file", "logs/pipeline_runs.jsonl")
    )
    log_format = str(logging_config.get("format", "jsonl")).lower()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "pipeline_name": args.pipeline_name,
        "status": args.status,
        "message": args.message,
        "source": args.source,
    }
    if log_format == "csv":
        write_header = not log_path.exists() or log_path.stat().st_size == 0
        with log_path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(record))
            if write_header:
                writer.writeheader()
            writer.writerow(record)
    else:
        with log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {"status": "success", "log_path": str(log_path), "record": record},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
