from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, LANDING_DIR
from src.observability import configure_logging as configure_application_logging

LOGGER = logging.getLogger(__name__)
OLIST_RAW_DIR = LANDING_DIR / "olist"
INVENTORY_PATH = DOCS_DIR / "raw_data_inventory.md"
EXPECTED_FILES = (
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
)
ENCODINGS_TO_TRY = ("utf-8", "utf-8-sig", "latin-1")


@dataclass
class DatasetSummary:
    file_name: str
    relative_path: str
    rows: int
    columns_count: int
    columns: list[str]
    dtypes: dict[str, str]
    parsed_date_columns: list[str]
    encoding: str


def configure_logging() -> None:
    configure_application_logging(logging.INFO)


def detect_date_columns(path: Path) -> list[str]:
    header = pd.read_csv(path, nrows=0)
    return [column for column in header.columns if "date" in column.lower() or "timestamp" in column.lower()]


def load_csv(path: Path) -> tuple[pd.DataFrame, str, list[str]]:
    date_columns = detect_date_columns(path)

    for encoding in ENCODINGS_TO_TRY:
        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
                parse_dates=date_columns or None,
                low_memory=False,
            )
            LOGGER.info("Arquivo carregado com sucesso: %s | encoding=%s", path.name, encoding)
            return df, encoding, date_columns
        except UnicodeDecodeError:
            LOGGER.warning("Falha de encoding em %s com %s. Tentando proximo fallback.", path.name, encoding)
        except ValueError as exc:
            if date_columns:
                LOGGER.warning(
                    "Falha ao aplicar parse de datas em %s (%s). Recarregando sem parse_dates.",
                    path.name,
                    exc,
                )
                for fallback_encoding in ENCODINGS_TO_TRY:
                    try:
                        df = pd.read_csv(path, encoding=fallback_encoding, low_memory=False)
                        LOGGER.info(
                            "Arquivo carregado sem parse de datas: %s | encoding=%s",
                            path.name,
                            fallback_encoding,
                        )
                        return df, fallback_encoding, []
                    except UnicodeDecodeError:
                        LOGGER.warning(
                            "Falha de encoding em %s com %s durante fallback sem datas.",
                            path.name,
                            fallback_encoding,
                        )

    raise RuntimeError(f"Não foi possível carregar o arquivo {path}.")


def validate_expected_files() -> list[Path]:
    LOGGER.info("Validando dataset Olist em %s", OLIST_RAW_DIR)

    if not OLIST_RAW_DIR.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {OLIST_RAW_DIR}")

    missing_files = [file_name for file_name in EXPECTED_FILES if not (OLIST_RAW_DIR / file_name).exists()]
    discovered_files = sorted(OLIST_RAW_DIR.glob("*.csv"))

    if missing_files:
        raise FileNotFoundError(f"Arquivos ausentes no dataset Olist: {', '.join(missing_files)}")

    LOGGER.info("Todos os arquivos esperados foram encontrados.")
    LOGGER.info("Arquivos localizados: %s", ", ".join(path.name for path in discovered_files))
    return discovered_files


def summarize_dataset(path: Path) -> DatasetSummary:
    df, encoding, parsed_date_columns = load_csv(path)
    summary = DatasetSummary(
        file_name=path.name,
        relative_path=str(path.relative_to(LANDING_DIR.parent.parent)).replace("\\", "/"),
        rows=df.shape[0],
        columns_count=df.shape[1],
        columns=list(df.columns),
        dtypes={column: str(dtype) for column, dtype in df.dtypes.items()},
        parsed_date_columns=parsed_date_columns,
        encoding=encoding,
    )

    LOGGER.info("Resumo %s | shape=(%s, %s)", path.name, summary.rows, summary.columns_count)
    LOGGER.info("Colunas %s | %s", path.name, ", ".join(summary.columns))
    LOGGER.info(
        "Tipos %s | %s",
        path.name,
        ", ".join(f"{column}: {dtype}" for column, dtype in summary.dtypes.items()),
    )
    return summary


def render_inventory_markdown(summaries: list[DatasetSummary]) -> str:
    lines = [
        "# Inventário de Dados Brutos",
        "",
        "Inventário gerado automaticamente a partir dos CSVs do dataset Olist em `data/raw/landing/olist/`.",
        "",
        f"Total de arquivos analisados: **{len(summaries)}**",
        "",
    ]

    for summary in summaries:
        lines.extend(
            [
                f"## {summary.file_name}",
                "",
                f"- Caminho: `{summary.relative_path}`",
                f"- Shape: `{summary.rows} x {summary.columns_count}`",
                f"- Encoding utilizado: `{summary.encoding}`",
                f"- Colunas com parsing de data: `{', '.join(summary.parsed_date_columns) if summary.parsed_date_columns else 'nenhuma'}`",
                "",
                "### Colunas",
                "",
                "| Coluna | Tipo |",
                "| --- | --- |",
            ]
        )
        lines.extend(f"| `{column}` | `{summary.dtypes[column]}` |" for column in summary.columns)
        lines.append("")

    return "\n".join(lines)


def save_inventory(summaries: list[DatasetSummary]) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INVENTORY_PATH.write_text(render_inventory_markdown(summaries), encoding="utf-8")
    LOGGER.info("Inventário salvo em %s", INVENTORY_PATH)
    return INVENTORY_PATH


def run_inventory() -> list[DatasetSummary]:
    csv_files = validate_expected_files()
    summaries = [summarize_dataset(path) for path in csv_files]
    save_inventory(summaries)
    return summaries


if __name__ == "__main__":
    configure_logging()
    run_inventory()
