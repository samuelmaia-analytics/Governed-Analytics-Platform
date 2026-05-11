from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale


def render_data_catalog(
    df: pd.DataFrame, classification_df: pd.DataFrame, locale: Locale
) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Data Catalog" if is_en else "Catálogo de Dados")

    catalog_df = pd.DataFrame(
        {
            "column_name": df.columns,
            "dtype": [str(dtype) for dtype in df.dtypes],
            "null_pct": (df.isna().mean() * 100).round(2).values,
            "distinct_values": [
                int(df[column].nunique(dropna=False)) for column in df.columns
            ],
        }
    ).merge(
        classification_df[["column_name", "lgpd_classification", "recommended_action"]],
        on="column_name",
        how="left",
    )

    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        search = st.text_input(
            "Buscar coluna" if not is_en else "Search column",
            placeholder="ex: customer_id" if not is_en else "e.g. customer_id",
            key="catalog_search",
        )
    with filter_col2:
        all_classifications = sorted(
            catalog_df["lgpd_classification"].dropna().unique().tolist()
        )
        selected_classifications = st.multiselect(
            "Filtrar por classificação LGPD"
            if not is_en
            else "Filter by LGPD classification",
            options=all_classifications,
            default=[],
            key="catalog_lgpd_filter",
        )

    filtered = catalog_df.copy()
    if search:
        filtered = filtered[
            filtered["column_name"].str.contains(search, case=False, na=False)
        ]
    if selected_classifications:
        filtered = filtered[
            filtered["lgpd_classification"].isin(selected_classifications)
        ]

    total = len(catalog_df)
    showing = len(filtered)
    st.caption(
        f"Exibindo {showing} de {total} colunas"
        if not is_en
        else f"Showing {showing} of {total} columns"
    )
    st.dataframe(filtered, width="stretch")
