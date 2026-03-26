from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PROFILING_DIR, STANDARDIZED_DIR
from src.ingest import configure_logging, load_csv, validate_expected_files


LOGGER = logging.getLogger(__name__)
EDA_SUMMARY_PATH = DOCS_DIR / "eda_summary.md"
STANDARDIZED_OLIST_DIR = STANDARDIZED_DIR / "olist"


@dataclass
class TableProfile:
    table_name: str
    file_name: str
    rows: int
    columns_count: int
    encoding: str
    id_columns: list[str]
    date_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    possible_keys: list[str]
    duplicate_rows: int
    duplicate_ratio: float


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: column.strip().lower() for column in df.columns}
    return df.rename(columns=renamed)


def save_standardized_table(df: pd.DataFrame, table_name: str) -> None:
    STANDARDIZED_OLIST_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(STANDARDIZED_OLIST_DIR / f"{table_name}.parquet", index=False)


def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    id_columns: list[str] = []
    date_columns: list[str] = []
    numeric_columns: list[str] = []
    categorical_columns: list[str] = []

    for column in df.columns:
        series = df[column]
        column_name = column.lower()

        if column_name.endswith("_id") or column_name == "id":
            id_columns.append(column)

        if is_datetime64_any_dtype(series) or "date" in column_name or "timestamp" in column_name:
            date_columns.append(column)
            continue

        if is_bool_dtype(series):
            categorical_columns.append(column)
            continue

        if is_numeric_dtype(series):
            numeric_columns.append(column)
            continue

        if is_object_dtype(series):
            categorical_columns.append(column)

    return {
        "id_columns": sorted(set(id_columns)),
        "date_columns": sorted(set(date_columns)),
        "numeric_columns": sorted(set(numeric_columns)),
        "categorical_columns": sorted(set(categorical_columns)),
    }


def build_nulls_profile(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    null_counts = df.isna().sum()
    null_ratio = (null_counts / len(df)).fillna(0) if len(df) else null_counts * 0

    profile = pd.DataFrame(
        {
            "table_name": table_name,
            "column_name": df.columns,
            "null_count": [int(null_counts[column]) for column in df.columns],
            "null_ratio": [float(null_ratio[column]) for column in df.columns],
        }
    )
    return profile.sort_values(["null_count", "column_name"], ascending=[False, True]).reset_index(drop=True)


def detect_possible_keys(df: pd.DataFrame, id_columns: list[str]) -> pd.DataFrame:
    candidate_columns = id_columns or [column for column in df.columns if column.lower().endswith("_id")]
    rows: list[dict[str, object]] = []

    for column in candidate_columns:
        non_null_series = df[column].dropna()
        if non_null_series.empty:
            uniqueness_ratio = 0.0
            is_possible_key = False
        else:
            uniqueness_ratio = float(non_null_series.nunique(dropna=True) / len(non_null_series))
            is_possible_key = non_null_series.is_unique and df[column].isna().sum() == 0

        rows.append(
            {
                "column_name": column,
                "non_null_count": int(non_null_series.shape[0]),
                "unique_non_null_count": int(non_null_series.nunique(dropna=True)),
                "uniqueness_ratio": uniqueness_ratio,
                "null_count": int(df[column].isna().sum()),
                "is_possible_key": is_possible_key,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "column_name",
                "non_null_count",
                "unique_non_null_count",
                "uniqueness_ratio",
                "null_count",
                "is_possible_key",
            ]
        )

    return pd.DataFrame(rows).sort_values(
        ["is_possible_key", "uniqueness_ratio", "column_name"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def build_columns_profile(df: pd.DataFrame, table_name: str, column_groups: dict[str, list[str]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column in df.columns:
        if column in column_groups["id_columns"]:
            semantic_type = "id"
        elif column in column_groups["date_columns"]:
            semantic_type = "date"
        elif column in column_groups["numeric_columns"]:
            semantic_type = "numeric"
        else:
            semantic_type = "categorical"

        rows.append(
            {
                "table_name": table_name,
                "column_name": column,
                "dtype": str(df[column].dtype),
                "semantic_type": semantic_type,
                "non_null_count": int(df[column].notna().sum()),
                "unique_count": int(df[column].nunique(dropna=True)),
            }
        )

    return pd.DataFrame(rows)


def build_duplicate_profile(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    duplicate_mask = df.duplicated(keep=False)
    duplicate_rows = int(duplicate_mask.sum())
    total_rows = int(len(df))
    duplicate_ratio = float(duplicate_rows / total_rows) if total_rows else 0.0

    return pd.DataFrame(
        [
            {
                "table_name": table_name,
                "total_rows": total_rows,
                "duplicate_rows": duplicate_rows,
                "duplicate_ratio": duplicate_ratio,
            }
        ]
    )


def profile_table(path: Path) -> tuple[TableProfile, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    table_name = path.stem
    df, encoding, _ = load_csv(path)
    df = standardize_columns(df)
    save_standardized_table(df, table_name)

    column_groups = classify_columns(df)
    nulls_profile = build_nulls_profile(df, table_name)
    possible_keys_profile = detect_possible_keys(df, column_groups["id_columns"])
    columns_profile = build_columns_profile(df, table_name, column_groups)
    duplicate_profile = build_duplicate_profile(df, table_name)

    possible_keys = possible_keys_profile.loc[possible_keys_profile["is_possible_key"], "column_name"].tolist()

    profile = TableProfile(
        table_name=table_name,
        file_name=path.name,
        rows=int(df.shape[0]),
        columns_count=int(df.shape[1]),
        encoding=encoding,
        id_columns=column_groups["id_columns"],
        date_columns=column_groups["date_columns"],
        numeric_columns=column_groups["numeric_columns"],
        categorical_columns=column_groups["categorical_columns"],
        possible_keys=possible_keys,
        duplicate_rows=int(duplicate_profile.loc[0, "duplicate_rows"]),
        duplicate_ratio=float(duplicate_profile.loc[0, "duplicate_ratio"]),
    )

    LOGGER.info(
        "Perfil concluído %s | linhas=%s | colunas=%s | chaves=%s | duplicadas=%s",
        path.name,
        profile.rows,
        profile.columns_count,
        ", ".join(profile.possible_keys) if profile.possible_keys else "nenhuma",
        profile.duplicate_rows,
    )
    return profile, columns_profile, nulls_profile, possible_keys_profile, duplicate_profile


def save_profile_tables(
    table_name: str,
    columns_profile: pd.DataFrame,
    nulls_profile: pd.DataFrame,
    possible_keys_profile: pd.DataFrame,
    duplicate_profile: pd.DataFrame,
) -> None:
    PROFILING_DIR.mkdir(parents=True, exist_ok=True)

    columns_profile.to_csv(PROFILING_DIR / f"{table_name}_columns_profile.csv", index=False)
    nulls_profile.to_csv(PROFILING_DIR / f"{table_name}_nulls_profile.csv", index=False)
    possible_keys_profile.to_csv(PROFILING_DIR / f"{table_name}_possible_keys.csv", index=False)
    duplicate_profile.to_csv(PROFILING_DIR / f"{table_name}_duplicate_profile.csv", index=False)


def save_consolidated_tables(
    profiles: list[TableProfile],
    columns_profiles: list[pd.DataFrame],
    nulls_profiles: list[pd.DataFrame],
    keys_profiles: list[pd.DataFrame],
    duplicate_profiles: list[pd.DataFrame],
) -> None:
    PROFILING_DIR.mkdir(parents=True, exist_ok=True)

    overview = pd.DataFrame(
        [
            {
                "table_name": profile.table_name,
                "file_name": profile.file_name,
                "rows": profile.rows,
                "columns_count": profile.columns_count,
                "encoding": profile.encoding,
                "id_columns": ", ".join(profile.id_columns),
                "date_columns": ", ".join(profile.date_columns),
                "numeric_columns": ", ".join(profile.numeric_columns),
                "categorical_columns": ", ".join(profile.categorical_columns),
                "possible_keys": ", ".join(profile.possible_keys),
                "duplicate_rows": profile.duplicate_rows,
                "duplicate_ratio": profile.duplicate_ratio,
            }
            for profile in profiles
        ]
    )

    overview.to_csv(PROFILING_DIR / "profiling_overview.csv", index=False)
    pd.concat(columns_profiles, ignore_index=True).to_csv(PROFILING_DIR / "all_columns_profile.csv", index=False)
    pd.concat(nulls_profiles, ignore_index=True).to_csv(PROFILING_DIR / "all_nulls_profile.csv", index=False)

    non_empty_keys_profiles = [profile for profile in keys_profiles if not profile.empty]
    if non_empty_keys_profiles:
        pd.concat(non_empty_keys_profiles, ignore_index=True).to_csv(
            PROFILING_DIR / "all_possible_keys.csv",
            index=False,
        )
    else:
        pd.DataFrame(
            columns=[
                "column_name",
                "non_null_count",
                "unique_non_null_count",
                "uniqueness_ratio",
                "null_count",
                "is_possible_key",
                "table_name",
            ]
        ).to_csv(PROFILING_DIR / "all_possible_keys.csv", index=False)

    pd.concat(duplicate_profiles, ignore_index=True).to_csv(PROFILING_DIR / "all_duplicate_profile.csv", index=False)


def render_eda_summary(profiles: list[TableProfile], nulls_profiles: list[pd.DataFrame]) -> str:
    lines = [
        "# Resumo de EDA",
        "",
        "Resumo exploratório inicial dos CSVs em `data/raw/landing/olist/`, com tabelas padronizadas promovidas para `data/standardized/olist/`.",
        "",
        "## Visão Geral",
        "",
        "| Tabela | Linhas | Colunas | IDs | Datas | Numéricas | Categóricas | Possíveis chaves | Linhas duplicadas |",
        "| --- | ---: | ---: | --- | --- | --- | --- | --- | ---: |",
    ]

    for profile in profiles:
        lines.append(
            "| {table} | {rows} | {cols} | {ids} | {dates} | {nums} | {cats} | {keys} | {dups} |".format(
                table=profile.table_name,
                rows=profile.rows,
                cols=profile.columns_count,
                ids=", ".join(profile.id_columns) or "-",
                dates=", ".join(profile.date_columns) or "-",
                nums=", ".join(profile.numeric_columns) or "-",
                cats=", ".join(profile.categorical_columns) or "-",
                keys=", ".join(profile.possible_keys) or "-",
                dups=profile.duplicate_rows,
            )
        )

    lines.extend(["", "## Detalhes por Tabela", ""])

    for profile, nulls_profile in zip(profiles, nulls_profiles):
        top_nulls = nulls_profile.loc[nulls_profile["null_count"] > 0].head(10)
        lines.extend(
            [
                f"### {profile.table_name}",
                "",
                f"- Arquivo: `{profile.file_name}`",
                f"- Encoding: `{profile.encoding}`",
                f"- Shape: `{profile.rows} x {profile.columns_count}`",
                f"- Colunas ID: `{', '.join(profile.id_columns) if profile.id_columns else 'nenhuma'}`",
                f"- Colunas de data: `{', '.join(profile.date_columns) if profile.date_columns else 'nenhuma'}`",
                f"- Colunas numéricas: `{', '.join(profile.numeric_columns) if profile.numeric_columns else 'nenhuma'}`",
                f"- Colunas categóricas: `{', '.join(profile.categorical_columns) if profile.categorical_columns else 'nenhuma'}`",
                f"- Possíveis chaves: `{', '.join(profile.possible_keys) if profile.possible_keys else 'nenhuma'}`",
                f"- Linhas duplicadas: `{profile.duplicate_rows}` ({profile.duplicate_ratio:.2%})",
                "",
                "#### Top colunas com nulos",
                "",
                "| Coluna | Nulos | Percentual |",
                "| --- | ---: | ---: |",
            ]
        )

        if top_nulls.empty:
            lines.append("| - | 0 | 0.00% |")
        else:
            lines.extend(
                f"| `{row.column_name}` | {int(row.null_count)} | {row.null_ratio:.2%} |"
                for row in top_nulls.itertuples(index=False)
            )
        lines.append("")

    lines.extend(
        [
            "## Artefatos Gerados",
            "",
            "- `data/standardized/olist/*.parquet`",
            "- `data/staging/profiling/profiling_overview.csv`",
            "- `data/staging/profiling/all_columns_profile.csv`",
            "- `data/staging/profiling/all_nulls_profile.csv`",
            "- `data/staging/profiling/all_possible_keys.csv`",
            "- `data/staging/profiling/all_duplicate_profile.csv`",
            "",
        ]
    )
    return "\n".join(lines)


def save_eda_summary(profiles: list[TableProfile], nulls_profiles: list[pd.DataFrame]) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    EDA_SUMMARY_PATH.write_text(render_eda_summary(profiles, nulls_profiles), encoding="utf-8")
    LOGGER.info("Relatório EDA salvo em %s", EDA_SUMMARY_PATH)
    return EDA_SUMMARY_PATH


def run_profiling() -> list[TableProfile]:
    csv_files = validate_expected_files()

    profiles: list[TableProfile] = []
    columns_profiles: list[pd.DataFrame] = []
    nulls_profiles: list[pd.DataFrame] = []
    keys_profiles: list[pd.DataFrame] = []
    duplicate_profiles: list[pd.DataFrame] = []

    for path in csv_files:
        profile, columns_profile, nulls_profile, possible_keys_profile, duplicate_profile = profile_table(path)
        profiles.append(profile)
        columns_profiles.append(columns_profile)
        nulls_profiles.append(nulls_profile)
        keys_profiles.append(possible_keys_profile.assign(table_name=profile.table_name))
        duplicate_profiles.append(duplicate_profile)
        save_profile_tables(
            profile.table_name,
            columns_profile,
            nulls_profile,
            possible_keys_profile,
            duplicate_profile,
        )

    save_consolidated_tables(profiles, columns_profiles, nulls_profiles, keys_profiles, duplicate_profiles)
    save_eda_summary(profiles, nulls_profiles)
    return profiles


if __name__ == "__main__":
    configure_logging()
    run_profiling()
