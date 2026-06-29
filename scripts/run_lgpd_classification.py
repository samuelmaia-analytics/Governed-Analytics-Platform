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
from src.lgpd_classifier import classify_dataframe_columns
from src.utils import ensure_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="n8n wrapper for LGPD classification.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    parser.add_argument("--input-path")
    parser.add_argument("--output-path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(PROJECT_ROOT / args.config)
    dataset_config = config.get("datasets", {})
    paths_config = config.get("paths", {})
    data_input_dir = str(paths_config.get("data_input", "data/"))
    input_path = PROJECT_ROOT / (
        args.input_path
        or dataset_config.get("governance_sample_path", "")
        or str(Path(data_input_dir) / "samples" / "sample_governance_dataset.csv")
    )
    output_path = PROJECT_ROOT / (
        args.output_path
        or dataset_config.get(
            "lgpd_classification_output_path",
            "logs/lgpd_classification_runtime.csv",
        )
    )
    df = pd.read_csv(input_path)
    classification_df = classify_dataframe_columns(df)
    ensure_directory(output_path.parent)
    classification_df.to_csv(output_path, index=False)
    payload = {
        "status": "success",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "total_columns": int(len(classification_df)),
        "high_risk_columns": int(
            classification_df["risk_level"].astype(str).str.lower().eq("high").sum()
        ),
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
