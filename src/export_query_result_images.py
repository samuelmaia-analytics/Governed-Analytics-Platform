from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys
import textwrap

import matplotlib.pyplot as plt
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import QUERY_RESULTS_DIR, SCREENSHOTS_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory


LOGGER = logging.getLogger(__name__)
OUTPUT_DIR = SCREENSHOTS_DIR / "query_results"
MAX_ROWS = 20
MAX_COLUMN_WIDTH = 28
FONT_SIZE = 9
ROW_HEIGHT = 0.42
COL_WIDTH = 2.4


@dataclass
class ExportedImage:
    source_csv: Path
    output_png: Path
    rows_rendered: int
    total_rows: int
    total_columns: int


def validate_input_files() -> list[Path]:
    if not QUERY_RESULTS_DIR.exists():
        raise FileNotFoundError(
            f"Diretorio nao encontrado: {QUERY_RESULTS_DIR}. "
            "Execute primeiro o runner das queries analiticas."
        )

    csv_files = sorted(path for path in QUERY_RESULTS_DIR.glob("*.csv") if path.name != "query_execution_manifest.csv")
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {QUERY_RESULTS_DIR}")

    return csv_files


def format_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def wrap_cell_text(value: object) -> str:
    return textwrap.fill(format_value(value), width=MAX_COLUMN_WIDTH)


def prepare_display_df(df: pd.DataFrame) -> pd.DataFrame:
    preview = df.head(MAX_ROWS).copy()
    for column in preview.columns:
        preview[column] = preview[column].map(wrap_cell_text)
    return preview


def compute_figure_size(df: pd.DataFrame) -> tuple[float, float]:
    width = max(12, min(28, df.shape[1] * COL_WIDTH))
    height = max(2.8, min(18, (len(df) + 1) * ROW_HEIGHT + 1.2))
    return width, height


def render_table_image(df: pd.DataFrame, title: str, output_path: Path) -> None:
    display_df = prepare_display_df(df)
    width, height = compute_figure_size(display_df)

    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor("white")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=14)

    table = ax.table(
        cellText=display_df.values,
        colLabels=list(display_df.columns),
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(FONT_SIZE)
    table.scale(1, 1.35)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#D9D9D9")
        if row == 0:
            cell.set_facecolor("#EAF2FF")
            cell.set_text_props(weight="bold", color="#1A1A1A")
        else:
            cell.set_facecolor("#FFFFFF" if row % 2 else "#F7F9FC")

    ensure_directory(output_path.parent)
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def export_csv_as_png(csv_path: Path) -> ExportedImage:
    df = pd.read_csv(csv_path)
    if df.empty:
        LOGGER.warning("CSV vazio ignorado: %s", csv_path.name)

    output_path = OUTPUT_DIR / f"{csv_path.stem}.png"
    title = f"{csv_path.stem} | preview {min(len(df), MAX_ROWS)} of {len(df)} rows"
    render_table_image(df, title, output_path)

    LOGGER.info(
        "Imagem exportada: %s | rows_rendered=%s | total_rows=%s | total_columns=%s",
        output_path.name,
        min(len(df), MAX_ROWS),
        len(df),
        df.shape[1],
    )
    return ExportedImage(
        source_csv=csv_path,
        output_png=output_path,
        rows_rendered=min(len(df), MAX_ROWS),
        total_rows=int(len(df)),
        total_columns=int(df.shape[1]),
    )


def export_all_query_result_images() -> list[ExportedImage]:
    csv_files = validate_input_files()
    ensure_directory(OUTPUT_DIR)
    return [export_csv_as_png(csv_path) for csv_path in csv_files]


def main() -> None:
    configure_logging()
    try:
        export_all_query_result_images()
    except FileNotFoundError as exc:
        LOGGER.error(str(exc))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
