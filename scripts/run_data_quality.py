from __future__ import annotations

# ruff: noqa: E402, I001

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from n8n_utils import load_config
from src.ingest import configure_logging
from src.quality import (
    load_fact_table,
    run_quality_checks,
    save_quality_report,
    save_quality_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="n8n wrapper for data quality checks.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_config(PROJECT_ROOT / args.config)
    configure_logging()
    fact_df = load_fact_table()
    results = run_quality_checks(fact_df)
    results_path = save_quality_results(results)
    report_path = save_quality_report(fact_df, results)
    failed_checks = [result for result in results if result.status == "FAIL"]
    payload = {
        "status": "failed" if failed_checks else "success",
        "total_checks": len(results),
        "failed_checks": len(failed_checks),
        "results_path": str(results_path),
        "report_path": str(report_path),
        "checks": [asdict(result) for result in results],
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
