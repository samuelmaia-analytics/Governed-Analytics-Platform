import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import GENAI_INPUT_DIR, GENAI_OUTPUT_DIR
from src.utils import ensure_directory, write_csv

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass(frozen=True)
class ExtractionResult:
    source_id: str
    title: str
    product_description: str
    features: dict[str, Any]
    extraction_mode: str
    model_name: str


REFERENCE_OUTPUTS = {
    "phone_case_001": {
        "category": "Phone Accessories",
        "material": "Premium PU Leather",
        "compatibility": ["Samsung Galaxy S8 Plus"],
        "quality_signals": ["100% Handmade", "Reinforced stitching", "RFID shielding"],
        "functional_features": [
            "receiver design",
            "hand strap",
            "card slots",
            "cosmetic mirror",
            "kickstand function",
            "space amplification",
        ],
        "security_features": ["RFID shielding technology"],
        "aesthetic_signals": ["variety of dashing colors", "sleek", "elegant"],
        "target_use_cases": ["movie-watching", "video-chatting", "makeup", "carry cards"],
        "summary": "Wallet-style phone case with mirror, card slots, RFID shielding and kickstand for Samsung Galaxy S8 Plus.",
    }
}


def build_prompt(title: str, description: str) -> str:
    return f"""
You are extracting structured product features from unstructured e-commerce text.

Return only valid JSON with this schema:
{{
  "category": string,
  "material": string or null,
  "compatibility": [string],
  "quality_signals": [string],
  "functional_features": [string],
  "security_features": [string],
  "aesthetic_signals": [string],
  "target_use_cases": [string],
  "summary": string
}}

Title:
{title}

Product Description:
{description}
""".strip()


def call_openai(prompt: str, model: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não encontrada. Use --mode reference ou configure a chave.")

    payload = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "You extract product features from unstructured retail text and return strict JSON.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    req = request.Request(
        OPENAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Erro ao chamar OpenAI API: {exc.code} - {body}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Falha de rede ao chamar OpenAI API: {exc.reason}") from exc

    content = raw["choices"][0]["message"]["content"]
    return json.loads(content)


def extract_features(df: pd.DataFrame, mode: str, model: str) -> list[ExtractionResult]:
    results: list[ExtractionResult] = []
    for row in df.itertuples(index=False):
        prompt = build_prompt(row.title, row.product_description)
        if mode == "reference":
            features = REFERENCE_OUTPUTS.get(row.source_id)
            if features is None:
                raise KeyError(f"Não existe saída de referência para source_id={row.source_id}.")
            extraction_mode = "reference"
            model_name = "reference_output"
        else:
            features = call_openai(prompt, model=model)
            extraction_mode = "openai_api"
            model_name = model

        results.append(
            ExtractionResult(
                source_id=row.source_id,
                title=row.title,
                product_description=row.product_description,
                features=features,
                extraction_mode=extraction_mode,
                model_name=model_name,
            )
        )
    return results


def flatten_results(results: list[ExtractionResult]) -> pd.DataFrame:
    records = []
    for item in results:
        features = item.features
        records.append(
            {
                "source_id": item.source_id,
                "title": item.title,
                "category": features.get("category"),
                "material": features.get("material"),
                "compatibility": " | ".join(features.get("compatibility", [])),
                "quality_signals": " | ".join(features.get("quality_signals", [])),
                "functional_features": " | ".join(features.get("functional_features", [])),
                "security_features": " | ".join(features.get("security_features", [])),
                "aesthetic_signals": " | ".join(features.get("aesthetic_signals", [])),
                "target_use_cases": " | ".join(features.get("target_use_cases", [])),
                "summary": features.get("summary"),
                "extraction_mode": item.extraction_mode,
                "model_name": item.model_name,
            }
        )
    return pd.DataFrame(records)


def write_jsonl(results: list[ExtractionResult], path: Path) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        for item in results:
            payload = {
                "source_id": item.source_id,
                "title": item.title,
                "product_description": item.product_description,
                "features": item.features,
                "extraction_mode": item.extraction_mode,
                "model_name": item.model_name,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extrai features estruturadas de texto desestruturado.")
    parser.add_argument(
        "--input",
        type=Path,
        default=GENAI_INPUT_DIR / "product_text_samples.csv",
        help="CSV com colunas source_id, title e product_description.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=GENAI_OUTPUT_DIR / "product_text_features.csv",
        help="Arquivo CSV final com as features materializadas.",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=GENAI_OUTPUT_DIR / "product_text_features.jsonl",
        help="Arquivo JSONL com payload completo por registro.",
    )
    parser.add_argument(
        "--mode",
        choices=["reference", "openai"],
        default="reference",
        help="reference usa saída de referência versionada; openai chama a API real.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Modelo da OpenAI usado no modo openai.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)
    required_columns = {"source_id", "title", "product_description"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV de entrada sem colunas obrigatórias: {missing}")

    results = extract_features(df, mode=args.mode, model=args.model)
    features_df = flatten_results(results)
    write_csv(features_df, args.output_csv)
    write_jsonl(results, args.output_jsonl)

    print(f"Features geradas com sucesso: {args.output_csv}")
    print(f"Payload JSONL salvo em: {args.output_jsonl}")


if __name__ == "__main__":
    main()
