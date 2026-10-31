from __future__ import annotations

import pandas as pd
import streamlit as st

from src.snowflake_connector import (
    SnowflakeConfig,
    _is_write_query,
    get_snowflake_connector,
)


def render_snowflake_explorer(locale: str) -> None:
    is_en = locale == "en-US"
    st.title("Snowflake Integration" if is_en else "Integração Snowflake")
    st.markdown(
        "On-demand operational exploration for querying metadata and results in a "
        "configured Snowflake environment."
        if is_en
        else "Exploração operacional sob demanda para consultar metadados e "
        "resultados em um ambiente Snowflake configurado."
    )
    st.caption(
        "No connection is opened automatically when this page loads. External "
        "operations occur only when the corresponding controls are activated."
        if is_en
        else "Nenhuma conexão é aberta automaticamente ao carregar esta página. "
        "As operações externas ocorrem somente quando os controles correspondentes "
        "são acionados."
    )

    st.markdown(
        "### How to interpret this page"
        if is_en
        else "### Como interpretar esta página"
    )
    st.write(
        "The displayed configuration only indicates that the required parameters "
        "were found in the environment. It does not prove connectivity, object "
        "existence, or warehouse availability."
        if is_en
        else "A configuração apresentada indica somente que os parâmetros "
        "necessários foram encontrados no ambiente. Isso não comprova "
        "conectividade, existência dos objetos ou disponibilidade do warehouse."
    )
    st.warning(
        "On-demand operations — 'Refresh' and 'Run' may open a real external "
        "connection to Snowflake."
        if is_en
        else "Operações sob demanda — 'Atualizar' e 'Executar' podem abrir uma "
        "conexão externa real com Snowflake."
    )
    st.caption(
        "None of these operations is executed automatically by Streamlit."
        if is_en
        else "Nenhuma dessas operações é executada automaticamente pelo Streamlit."
    )

    try:
        config = SnowflakeConfig.from_env()
    except EnvironmentError as exc:
        st.markdown("## Overview" if is_en else "## Visão geral")
        overview_columns = st.columns(3)
        overview_columns[0].metric(
            "Configuration" if is_en else "Configuração",
            "Incomplete" if is_en else "Incompleta",
        )
        overview_columns[1].metric(
            "Connection" if is_en else "Conexão",
            "Not verified" if is_en else "Não verificada",
        )
        overview_columns[2].metric(
            "Execution" if is_en else "Execução",
            "Only by user action" if is_en else "Somente por ação do usuário",
        )
        st.markdown("## Configuration" if is_en else "## Configuração")
        st.error(
            "Snowflake configuration is incomplete in this environment."
            if is_en
            else "Configuração Snowflake incompleta neste ambiente."
        )
        st.info(
            "The required parameters must be available before a connection can be "
            "started."
            if is_en
            else "Os parâmetros obrigatórios precisam estar disponíveis antes que "
            "uma conexão possa ser iniciada."
        )
        st.markdown(
            "## Technical details" if is_en else "## Detalhes técnicos"
        )
        with st.expander(
            "Integration technical details"
            if is_en
            else "Detalhes técnicos da integração"
        ):
            st.caption(
                "Required environment variables:"
                if is_en
                else "Variáveis de ambiente obrigatórias:"
            )
            st.code(
                "SNOWFLAKE_ACCOUNT\n"
                "SNOWFLAKE_USER\n"
                "SNOWFLAKE_PASSWORD\n"
                "SNOWFLAKE_WAREHOUSE\n"
                "SNOWFLAKE_DATABASE\n"
                "SNOWFLAKE_SCHEMA"
            )
            st.caption("Original technical error:" if is_en else "Erro técnico original:")
            st.code(str(exc))
            st.caption(
                "No secret value is displayed."
                if is_en
                else "Nenhum valor secreto é exibido."
            )
        return

    st.markdown("## Overview" if is_en else "## Visão geral")
    overview_columns = st.columns(3)
    overview_columns[0].metric(
        "Configuration" if is_en else "Configuração",
        "Detected" if is_en else "Detectada",
    )
    overview_columns[1].metric(
        "Connection" if is_en else "Conexão",
        "Not verified in this rendering"
        if is_en
        else "Não verificada nesta renderização",
    )
    overview_columns[2].metric(
        "Execution" if is_en else "Execução",
        "Only by user action" if is_en else "Somente por ação do usuário",
    )

    st.markdown("## Configuration" if is_en else "## Configuração")
    st.info(
        "Required parameters were found in the environment. Connection has not "
        "been verified."
        if is_en
        else "Parâmetros obrigatórios encontrados no ambiente. A conexão não foi "
        "verificada."
    )
    config_columns = st.columns(4)
    config_columns[0].caption("Database")
    config_columns[0].markdown(f"`{config.database}`")
    config_columns[1].caption("Schema")
    config_columns[1].markdown(f"`{config.schema}`")
    config_columns[2].caption("Warehouse")
    config_columns[2].markdown(f"`{config.warehouse}`")
    config_columns[3].caption("Role")
    config_columns[3].markdown(f"`{config.role}`")

    technical_errors: list[str] = []

    st.markdown("## Tables" if is_en else "## Tabelas")
    st.caption(
        "This action queries the configured Snowflake environment and may perform "
        "an external metadata operation."
        if is_en
        else "Esta ação consulta o Snowflake configurado e pode executar uma "
        "operação externa de metadados."
    )
    if st.button("Refresh" if is_en else "Atualizar"):
        try:
            with get_snowflake_connector() as conn:
                tables = conn.list_tables()
            if tables:
                tables_df = pd.DataFrame(tables)
                presentation_df = tables_df.copy()
                if not is_en:
                    presentation_df = presentation_df.rename(
                        columns={
                            "table": "Tabela",
                            "database": "Database",
                            "schema": "Schema",
                        }
                    )
                st.dataframe(
                    presentation_df,
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.info(
                    "No tables found."
                    if is_en
                    else "Nenhuma tabela encontrada."
                )
        except Exception as exc:
            st.error(
                "Tables could not be listed."
                if is_en
                else "Não foi possível listar as tabelas."
            )
            technical_errors.append(f"Failed to list tables: {exc}")

    st.markdown("## SQL query" if is_en else "## Consulta SQL")
    st.caption(
        "The query is sent to Snowflake only when 'Run' is activated."
        if is_en
        else "A consulta somente é enviada ao Snowflake quando 'Executar' é "
        "acionado."
    )
    st.info(
        "A local validation blocks some write prefixes before the connection. This "
        "local validation does not replace permissions, policies, or access controls "
        "configured in Snowflake."
        if is_en
        else "Existe uma validação local que bloqueia alguns prefixos de escrita "
        "antes da conexão. Essa validação local não substitui permissões, políticas "
        "ou controles de acesso configurados no Snowflake."
    )
    sql = st.text_area(
        "SQL",
        value="SELECT CURRENT_DATE()",
        height=120,
    )
    if st.button("Run" if is_en else "Executar"):
        if _is_write_query(sql):
            st.error(
                "The query was blocked by the local write-prefix validation."
                if is_en
                else "A consulta foi bloqueada pela validação local de prefixos "
                "de escrita."
            )
        else:
            try:
                with get_snowflake_connector() as conn:
                    df = conn.query(sql)
                st.dataframe(
                    df.copy(),
                    width="stretch",
                    hide_index=True,
                )
                st.caption(
                    "Result returned by the query executed on demand."
                    if is_en
                    else "Resultado retornado pela consulta executada sob demanda."
                )
                st.caption(
                    f"{len(df):,} rows returned"
                    if is_en
                    else f"{len(df):,} linhas retornadas"
                )
            except Exception as exc:
                st.error(
                    "The query could not be executed."
                    if is_en
                    else "Não foi possível executar a consulta."
                )
                technical_errors.append(f"Query failed: {exc}")

    st.markdown(
        "## Limitations and security"
        if is_en
        else "## Limitações e segurança"
    )
    limitations = (
        (
            "No connection or health check is performed automatically.",
            "Detected configuration does not mean validated connectivity.",
            "SQL validation is local and limited; actual authorization depends on "
            "Snowflake permissions.",
            "Passwords are not displayed.",
            "Query results are not written locally or persisted in a history.",
            "This page does not execute dbt or a data pipeline.",
        )
        if is_en
        else (
            "Nenhuma conexão ou health check é executado automaticamente.",
            "Configuração detectada não significa conectividade validada.",
            "A validação de SQL é local e limitada; a autorização real depende "
            "das permissões do Snowflake.",
            "Nenhuma senha é exibida.",
            "Os resultados não são escritos localmente nem persistidos em histórico.",
            "A página não executa dbt nem pipeline de dados.",
        )
    )
    for limitation in limitations:
        st.write(f"- {limitation}")

    st.markdown("## Technical details" if is_en else "## Detalhes técnicos")
    with st.expander(
        "Integration technical details"
        if is_en
        else "Detalhes técnicos da integração"
    ):
        st.caption("Configured account:" if is_en else "Account configurada:")
        st.code(config.account)
        st.caption("Database / Schema / Warehouse / Role")
        st.code(
            f"{config.database}\n{config.schema}\n{config.warehouse}\n{config.role}"
        )
        st.caption(
            "Required environment variable names:"
            if is_en
            else "Nomes das variáveis de ambiente obrigatórias:"
        )
        st.code(
            "SNOWFLAKE_ACCOUNT\n"
            "SNOWFLAKE_USER\n"
            "SNOWFLAKE_PASSWORD\n"
            "SNOWFLAKE_WAREHOUSE\n"
            "SNOWFLAKE_DATABASE\n"
            "SNOWFLAKE_SCHEMA"
        )
        st.caption("Default SQL:" if is_en else "SQL default:")
        st.code("SELECT CURRENT_DATE()", language="sql")
        st.write(
            "Table inspection uses SHOW TABLES through snowflake.connector."
            if is_en
            else "A inspeção de tabelas usa SHOW TABLES por meio de "
            "snowflake.connector."
        )
        st.caption(
            "Technical table columns: table, database, schema"
            if is_en
            else "Colunas técnicas da tabela: table, database, schema"
        )
        if technical_errors:
            st.markdown(
                "**Original technical errors**"
                if is_en
                else "**Erros técnicos originais**"
            )
            for technical_error in technical_errors:
                st.code(technical_error)
