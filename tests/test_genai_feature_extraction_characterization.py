from __future__ import annotations

import dataclasses
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

import src.genai_feature_extraction as genai


def test_public_api_imports_signatures_and_dataclass_schema() -> None:
    from src.genai_feature_extraction import (  # noqa: PLC0415
        ExtractionResult,
        extract_features,
        flatten_results,
        main,
        write_jsonl,
    )

    assert callable(extract_features)
    assert callable(flatten_results)
    assert callable(write_jsonl)
    assert callable(main)

    signature = inspect.signature(extract_features)
    assert list(signature.parameters) == ["df", "mode", "model"]

    assert dataclasses.is_dataclass(ExtractionResult)
    field_names = [field.name for field in dataclasses.fields(ExtractionResult)]
    assert field_names == [
        "source_id",
        "title",
        "product_description",
        "features",
        "extraction_mode",
        "model_name",
    ]

    result = ExtractionResult(
        source_id="x",
        title="y",
        product_description="z",
        features={},
        extraction_mode="reference",
        model_name="reference_output",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.source_id = "new"  # type: ignore[misc]


def test_extract_features_reference_is_deterministic_and_no_external_calls(
    monkeypatch,
) -> None:
    df = pd.DataFrame(
        {
            "source_id": ["phone_case_001"],
            "title": ["Phone Case"],
            "product_description": ["Leather wallet case"],
        }
    )

    def fail_call_openai(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("call_openai não deve ser chamado no modo reference")

    monkeypatch.setattr(genai, "call_openai", fail_call_openai)
    monkeypatch.setattr(
        genai.request,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("urlopen não deve ser chamado no modo reference")
        ),
    )

    first = genai.extract_features(df, mode="reference", model="demo-model")
    second = genai.extract_features(df, mode="reference", model="demo-model")

    assert first == second
    assert len(first) == 1
    assert first[0].extraction_mode == "reference"
    assert first[0].model_name == "reference_output"


def test_write_jsonl_emits_expected_schema_and_utf8(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    results = [
        genai.ExtractionResult(
            source_id="id-1",
            title="Título",
            product_description="Descrição",
            features={"summary": "ação"},
            extraction_mode="reference",
            model_name="reference_output",
        )
    ]

    genai.write_jsonl(results, path)

    raw = path.read_text(encoding="utf-8")
    assert "ação" in raw

    payload = json.loads(raw.splitlines()[0])
    assert set(payload) == {
        "source_id",
        "title",
        "product_description",
        "features",
        "extraction_mode",
        "model_name",
    }
    assert payload["features"]["summary"] == "ação"


def test_cli_reference_mode_python_m_executes_and_writes_outputs(tmp_path: Path) -> None:
    input_path = tmp_path / "input.csv"
    output_csv = tmp_path / "out.csv"
    output_jsonl = tmp_path / "out.jsonl"
    df = pd.DataFrame(
        {
            "source_id": ["phone_case_001"],
            "title": ["Phone Case"],
            "product_description": ["Leather wallet case"],
        }
    )
    df.to_csv(input_path, index=False)

    project_root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.genai_feature_extraction",
            "--input",
            str(input_path),
            "--output-csv",
            str(output_csv),
            "--output-jsonl",
            str(output_jsonl),
            "--mode",
            "reference",
            "--model",
            "demo-model",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "Features geradas com sucesso" in proc.stdout
    assert output_csv.exists()
    assert output_jsonl.exists()

    first_line = output_jsonl.read_text(encoding="utf-8").splitlines()[0]
    payload = json.loads(first_line)
    assert payload["source_id"] == "phone_case_001"
