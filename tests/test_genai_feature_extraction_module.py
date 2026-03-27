from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import src.genai_feature_extraction as genai


def test_build_prompt_and_reference_extraction() -> None:
    prompt = genai.build_prompt("Phone Case", "Leather wallet case")
    df = pd.DataFrame(
        {
            "source_id": ["phone_case_001"],
            "title": ["Phone Case"],
            "product_description": ["Leather wallet case"],
        }
    )

    results = genai.extract_features(df, mode="reference", model="demo-model")

    assert "Return only valid JSON" in prompt
    assert results[0].extraction_mode == "reference"
    assert results[0].features["category"] == "Phone Accessories"


def test_extract_features_raises_for_missing_reference() -> None:
    df = pd.DataFrame(
        {
            "source_id": ["missing"],
            "title": ["Item"],
            "product_description": ["Desc"],
        }
    )

    with pytest.raises(KeyError):
        genai.extract_features(df, mode="reference", model="demo-model")


def test_flatten_results_write_jsonl_and_main(tmp_path: Path, monkeypatch, capsys) -> None:
    input_path = tmp_path / "input.csv"
    output_csv = tmp_path / "output" / "features.csv"
    output_jsonl = tmp_path / "output" / "features.jsonl"
    df = pd.DataFrame(
        {
            "source_id": ["phone_case_001"],
            "title": ["Phone Case"],
            "product_description": ["Leather wallet case"],
        }
    )
    df.to_csv(input_path, index=False)

    results = genai.extract_features(df, mode="reference", model="demo-model")
    flat_df = genai.flatten_results(results)
    genai.write_jsonl(results, output_jsonl)

    assert "category" in flat_df.columns
    assert output_jsonl.exists()
    first_line = output_jsonl.read_text(encoding="utf-8").splitlines()[0]
    assert json.loads(first_line)["source_id"] == "phone_case_001"

    class Args:
        pass

    Args.input = input_path
    Args.output_csv = output_csv
    Args.output_jsonl = output_jsonl
    Args.mode = "reference"
    Args.model = "demo-model"

    monkeypatch.setattr(genai, "parse_args", lambda: Args())
    genai.main()

    stdout = capsys.readouterr().out
    assert "Features geradas com sucesso" in stdout
    assert output_csv.exists()


def test_main_rejects_missing_required_columns(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "bad.csv"
    pd.DataFrame({"source_id": ["x"], "title": ["y"]}).to_csv(input_path, index=False)

    class Args:
        pass

    Args.input = input_path
    Args.output_csv = tmp_path / "o.csv"
    Args.output_jsonl = tmp_path / "o.jsonl"
    Args.mode = "reference"
    Args.model = "demo-model"

    monkeypatch.setattr(genai, "parse_args", lambda: Args())

    with pytest.raises(ValueError):
        genai.main()
