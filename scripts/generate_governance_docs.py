from __future__ import annotations

# ruff: noqa: E402, I001

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from n8n_utils import load_config
from src.report_generator import generate_markdown_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="n8n wrapper for governance docs.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    parser.add_argument("--input-path")
    parser.add_argument("--docs-dir")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(PROJECT_ROOT / args.config)
    paths_config = config.get("paths", {})
    data_input_dir = str(paths_config.get("data_input", "data/"))
    input_path = PROJECT_ROOT / (
        args.input_path
        or config.get("datasets", {}).get("governance_sample_path", "")
        or str(Path(data_input_dir) / "samples" / "sample_governance_dataset.csv")
    )
    docs_dir = PROJECT_ROOT / (
        args.docs_dir
        or config.get("reports", {}).get("docs_dir", "")
        or str(paths_config.get("docs", "docs"))
    )
    df = pd.read_csv(input_path)
    generated_paths = generate_markdown_reports(df, docs_dir=docs_dir)
    payload = {
        "status": "success",
        "input_path": str(input_path),
        "docs_dir": str(docs_dir),
        "generated_paths": {
            name: str(path) for name, path in generated_paths.items()
        },
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
