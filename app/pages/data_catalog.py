from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale


def render_data_catalog(df: pd.DataFrame, classification_df: pd.DataFrame, locale: Locale) -> None:
    catalog_df = pd.DataFrame(
        {
            "column_name": df.columns,
            "dtype": [str(dtype) for dtype in df.dtypes],
            "null_pct": (df.isna().mean() * 100).round(2).values,
            "distinct_values": [int(df[column].nunique(dropna=False)) for column in df.columns],
        }
    ).merge(
        classification_df[["column_name", "lgpd_classification", "recommended_action"]],
        on="column_name",
        how="left",
    )
    st.subheader("Data Catalog" if locale == LOCALE_EN_US else "Catálogo de Dados")
    st.dataframe(catalog_df, width="stretch")
