from __future__ import annotations

import pandas as pd
import streamlit as st

from src.snowflake_connector import (
    SnowflakeConfig,
    _is_write_query,
    get_snowflake_connector,
)


def render_snowflake_explorer(locale: str) -> None:
    st.header("Snowflake Explorer" if locale == "en-US" else "Explorador Snowflake")

    try:
        config = SnowflakeConfig.from_env()
    except EnvironmentError as exc:
        st.error(str(exc))
        st.info(
            "Set `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, "
            "`SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, and `SNOWFLAKE_SCHEMA` "
            "in your `.env` file."
        )
        return

    st.success(
        f"Account: `{config.account}` | Database: `{config.database}` | Schema: `{config.schema}`"
    )

    tab_tables, tab_query = st.tabs(
        ["Tables", "Query Runner"]
        if locale == "en-US"
        else ["Tabelas", "Consultas SQL"]
    )

    with tab_tables:
        if st.button("Refresh" if locale == "en-US" else "Atualizar"):
            try:
                with get_snowflake_connector() as conn:
                    tables = conn.list_tables()
                if tables:
                    st.dataframe(pd.DataFrame(tables), width="stretch")
                else:
                    st.info(
                        "No tables found."
                        if locale == "en-US"
                        else "Nenhuma tabela encontrada."
                    )
            except Exception as exc:
                st.error(f"Failed to list tables: {exc}")

    with tab_query:
        sql = st.text_area(
            "SQL (SELECT only)" if locale == "en-US" else "SQL (somente SELECT)",
            value="SELECT CURRENT_DATE()",
            height=120,
        )
        if st.button("Run" if locale == "en-US" else "Executar"):
            if _is_write_query(sql):
                st.error(
                    "Only SELECT queries are allowed."
                    if locale == "en-US"
                    else "Apenas consultas SELECT são permitidas."
                )
            else:
                try:
                    with get_snowflake_connector() as conn:
                        df = conn.query(sql)
                    st.dataframe(df, width="stretch")
                    st.caption(
                        f"{len(df):,} rows returned"
                        if locale == "en-US"
                        else f"{len(df):,} linhas retornadas"
                    )
                except Exception as exc:
                    st.error(f"Query failed: {exc}")
