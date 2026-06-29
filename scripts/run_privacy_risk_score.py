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
from src.risk_scoring import calculate_privacy_risk_score
from src.utils import ensure_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="n8n wrapper for privacy risk scoring.")
    parser.add_argument("--config", default="config/pipeline_config.yml")
    parser.add_argument("--input-path")
    parser.add_argument("--output-path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(PROJECT_ROOT / args.config)
    dataset_config = config.get("datasets", {})
    input_path = PROJECT_ROOT / (
        args.input_path or dataset_config.get("governance_sample_path", "")
    )
    output_path = PROJECT_ROOT / (
        args.output_path
        or dataset_config.get(
            "privacy_risk_output_path", "data/curated/ops/privacy_risk_score.json"
        )
    )
    df = pd.read_csv(input_path)
    classification_df = classify_dataframe_columns(df)
    risk_result = calculate_privacy_risk_score(classification_df, total_rows=len(df))
    ensure_directory(output_path.parent)
    output_path.write_text(
        json.dumps(risk_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    payload = {
        "status": "success",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "score": risk_result["score"],
        "risk_level": risk_result["risk_level"],
        "publication_recommendation": risk_result["publication_recommendation"],
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
