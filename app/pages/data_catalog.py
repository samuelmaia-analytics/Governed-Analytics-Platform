from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

_CLASSIFICATION_LABELS_PT = {
    "non_personal": "Não pessoal",
    "indirect_identifier": "Identificador indireto",
    "personal_data": "Dado pessoal",
    "sensitive_personal_data": "Dado pessoal sensível",
}

_CLASSIFICATION_LABELS_EN = {
    "non_personal": "Non-personal",
    "indirect_identifier": "Indirect identifier",
    "personal_data": "Personal data",
    "sensitive_personal_data": "Sensitive personal data",
}

_ACTION_LABELS_PT = {
    "keep": "Manter",
    "review": "Revisar",
    "mask": "Mascarar",
}

_ACTION_LABELS_EN = {
    "keep": "Keep",
    "review": "Review",
    "mask": "Mask",
}


def _format_decimal(value: int | float, decimal_places: int) -> str:
    if pd.isna(value):
        return "—"
    formatted = f"{float(value):,.{decimal_places}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def _format_percentage(value: int | float) -> str:
    formatted = _format_decimal(value, 2)
    return formatted if formatted == "—" else f"{formatted}%"


def _format_integer(value: int | float) -> str:
    return f"{int(float(value)):,}".replace(",", ".")


def render_data_catalog(
    df: pd.DataFrame, classification_df: pd.DataFrame, locale: Locale
) -> None:
    is_en = locale == LOCALE_EN_US
    classification_labels = (
        _CLASSIFICATION_LABELS_EN if is_en else _CLASSIFICATION_LABELS_PT
    )
    action_labels = _ACTION_LABELS_EN if is_en else _ACTION_LABELS_PT

    st.title("Data Catalog" if is_en else "Catálogo de Dados")
    st.subheader(
        "Technical inventory of the analytical asset columns, with structural "
        "profiling and governance classification."
        if is_en
        else "Inventário técnico das colunas do ativo analítico, com perfil "
        "estrutural e classificação de governança."
    )
    st.caption(
        "This page presents metadata calculated from the active dataset and "
        "consumes the LGPD classification already produced by governance rules."
        if is_en
        else "A página apresenta metadados calculados sobre o dataset ativo e "
        "consome a classificação LGPD já produzida pelas regras de governança."
    )
    st.markdown(
        "### How to interpret this page"
        if is_en
        else "### Como interpretar esta página"
    )
    st.write(
        "Each row represents a column in the active dataset. The catalog combines "
        "data type, percentage of missing values, cardinality, and LGPD "
        "classification to support discovery, review, and responsible data use."
        if is_en
        else "Cada linha representa uma coluna do dataset ativo. O catálogo combina "
        "tipo de dado, percentual de valores ausentes, cardinalidade e classificação "
        "LGPD para apoiar descoberta, revisão e uso responsável dos dados."
    )

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

    total_columns = len(catalog_df)
    personal_data_columns = int(
        (catalog_df["lgpd_classification"] == "personal_data").sum()
    )
    indirect_identifier_columns = int(
        (catalog_df["lgpd_classification"] == "indirect_identifier").sum()
    )
    action_required_columns = int(
        (catalog_df["recommended_action"] != "keep").sum()
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric(
        "Cataloged columns" if is_en else "Colunas catalogadas",
        _format_integer(total_columns),
    )
    metric_2.metric(
        "Personal data" if is_en else "Dados pessoais",
        _format_integer(personal_data_columns),
    )
    metric_3.metric(
        "Indirect identifiers" if is_en else "Identificadores indiretos",
        _format_integer(indirect_identifier_columns),
    )
    metric_4.metric(
        "Columns requiring action" if is_en else "Colunas que exigem ação",
        _format_integer(action_required_columns),
    )

    st.markdown("### Executive reading" if is_en else "### Leitura executiva")
    if is_en:
        st.markdown(
            f"- The current asset has **{_format_integer(len(df))} records** and "
            f"**{_format_integer(len(df.columns))} cataloged columns**.\n"
            f"- **{_format_integer(personal_data_columns)} columns** are classified "
            "as personal data.\n"
            f"- **{_format_integer(indirect_identifier_columns)} columns** are "
            "indirect identifiers.\n"
            f"- **{_format_integer(action_required_columns)} columns** have a "
            "recommended action other than keep."
        )
    else:
        st.markdown(
            f"- O ativo atual possui **{_format_integer(len(df))} registros** e "
            f"**{_format_integer(len(df.columns))} colunas catalogadas**.\n"
            f"- **{_format_integer(personal_data_columns)} colunas** estão "
            "classificadas como dados pessoais.\n"
            f"- **{_format_integer(indirect_identifier_columns)} colunas** são "
            "identificadores indiretos.\n"
            f"- **{_format_integer(action_required_columns)} colunas** possuem ação "
            "recomendada diferente de manter."
        )

    st.caption(
        "LGPD classification indicates how the governance rule characterizes the "
        "column. The recommended action represents the treatment suggested by the "
        "classifier and is not a publication decision."
        if is_en
        else "Classificação LGPD indica como a regra de governança caracteriza a "
        "coluna. A ação recomendada representa o tratamento sugerido pelo "
        "classificador e não é uma decisão de publicação."
    )

    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        search = st.text_input(
            "Buscar coluna" if not is_en else "Search column",
            placeholder=(
                "Ex.: customer_unique_id"
                if not is_en
                else "E.g. customer_unique_id"
            ),
            help=(
                "Pesquisa apenas pelo nome técnico da coluna."
                if not is_en
                else "Searches only the technical column name."
            ),
            key="catalog_search",
        )
    with filter_col2:
        all_classifications = sorted(
            catalog_df["lgpd_classification"].dropna().unique().tolist()
        )
        selected_classifications = st.multiselect(
            "Classificação LGPD" if not is_en else "LGPD classification",
            options=all_classifications,
            default=[],
            key="catalog_lgpd_filter",
            format_func=lambda value: classification_labels.get(value, value),
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

    executive_table = filtered.copy()
    executive_table["null_pct"] = executive_table["null_pct"].map(
        _format_percentage
    )
    executive_table["distinct_values"] = executive_table["distinct_values"].map(
        _format_integer
    )
    executive_table["lgpd_classification"] = executive_table[
        "lgpd_classification"
    ].map(lambda value: classification_labels.get(value, value))
    executive_table["recommended_action"] = executive_table[
        "recommended_action"
    ].map(lambda value: action_labels.get(value, value))
    executive_table = executive_table.rename(
        columns={
            "column_name": "Column" if is_en else "Coluna",
            "dtype": "Type" if is_en else "Tipo",
            "null_pct": "Nulls" if is_en else "Nulos",
            "distinct_values": (
                "Distinct values" if is_en else "Valores distintos"
            ),
            "lgpd_classification": (
                "LGPD classification" if is_en else "Classificação LGPD"
            ),
            "recommended_action": (
                "Recommended action" if is_en else "Ação recomendada"
            ),
        }
    )

    st.dataframe(executive_table, width="stretch", hide_index=True)

    with st.expander(
        "Technical catalog details" if is_en else "Detalhes técnicos do catálogo",
        expanded=False,
    ):
        st.caption(
            "The values below preserve the technical identifiers and enums used by "
            "governance rules."
            if is_en
            else "Os valores abaixo preservam os identificadores e enums técnicos "
            "utilizados pelas regras de governança."
        )
        st.dataframe(filtered.copy(), width="stretch", hide_index=True)
