from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

import streamlit as st
from streamlit.navigation.page import StreamlitPage

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.context import GovernanceAppContext, build_context  # noqa: E402
from app.components.ui import inject_base_styles  # noqa: E402
from app.i18n import build_locale_selector  # noqa: E402
from app.pages.data_catalog import render_data_catalog  # noqa: E402
from app.pages.data_quality import render_data_quality  # noqa: E402
from app.pages.cohort_retention import render_cohort_retention  # noqa: E402
from app.pages.eda import render_eda  # noqa: E402
from app.pages.executive_overview import render_executive_overview  # noqa: E402
from app.pages.governance_control_center import (
    render_governance_control_center,  # noqa: E402
)
from app.pages.governance_report import render_governance_report  # noqa: E402
from app.pages.snowflake_explorer import render_snowflake_explorer  # noqa: E402
from app.pages.genai_insights import render_genai_insights  # noqa: E402
from app.pages.governance_assistant import render_governance_assistant  # noqa: E402
from app.pages.lgpd_privacy_risk import render_lgpd_privacy_risk  # noqa: E402
from app.pages.n8n_automation import render_n8n_automation  # noqa: E402
from app.pages.publication_governance import (  # noqa: E402
    render_publication_governance,
)
from app.pages.revenue_analytics import render_revenue_analytics  # noqa: E402
from app.pages.seller_performance import render_seller_performance  # noqa: E402
from src.duckdb_engine import get_duckdb_version  # noqa: E402

st.set_page_config(
    page_title="Governed Analytics Platform",
    page_icon=":material/policy:",
    layout="wide",
)


def _render_executive_page(
    context: GovernanceAppContext,
    locale: str,
    business_page: StreamlitPage | None = None,
    governance_page: StreamlitPage | None = None,
    quick_pages: dict[str, StreamlitPage] | None = None,
) -> None:
    render_executive_overview(
        context.df,
        context.classification_df,
        context.risk_result,
        context.quality_results,
        locale,
        business_page=business_page,
        governance_page=governance_page,
        quick_pages=quick_pages,
        duckdb_version=get_duckdb_version(),
        uses_persisted_governance=context.uses_persisted_governance,
    )


def _render_catalog_page(context: GovernanceAppContext, locale: str) -> None:
    render_data_catalog(context.df, context.classification_df, locale)


def _render_lgpd_page(context: GovernanceAppContext, locale: str) -> None:
    render_lgpd_privacy_risk(
        context.df, context.classification_df, context.risk_result, locale
    )


def _render_quality_page(context: GovernanceAppContext, locale: str) -> None:
    render_data_quality(context.quality_results, context.quality_table, locale)


def _render_eda_page(context: GovernanceAppContext, locale: str) -> None:
    render_eda(context.df, locale)


def _render_report_page(context: GovernanceAppContext, locale: str) -> None:
    render_governance_report(context.report_paths, locale)


def _render_revenue_page(context: GovernanceAppContext, locale: str) -> None:
    render_revenue_analytics(context.df, locale)


def _render_seller_performance_page(
    _context: GovernanceAppContext, locale: str
) -> None:
    render_seller_performance(locale)


def _render_cohort_retention_page(_context: GovernanceAppContext, locale: str) -> None:
    render_cohort_retention(locale)


def _render_genai_page(_context: GovernanceAppContext, locale: str) -> None:
    render_genai_insights(locale)


def _render_assistant_page(_context: GovernanceAppContext, locale: str) -> None:
    render_governance_assistant(locale)


def _render_control_center_page(context: GovernanceAppContext, locale: str) -> None:
    render_governance_control_center(
        context.df,
        context.classification_df,
        context.risk_result,
        context.quality_results,
        locale,
    )


def _render_snowflake_page(_context: GovernanceAppContext, locale: str) -> None:
    render_snowflake_explorer(locale)


def _render_n8n_automation_page(
    _context: GovernanceAppContext, _locale: str
) -> None:
    render_n8n_automation()


def _render_publication_governance_page(
    _context: GovernanceAppContext, _locale: str
) -> None:
    render_publication_governance()


def main() -> None:
    locale = build_locale_selector()
    inject_base_styles()
    context = build_context(locale)

    is_en = locale == "en-US"

    revenue_page = st.Page(
        lambda: _render_revenue_page(context, locale),
        title=("Business KPIs" if is_en else "Indicadores anal\u00edticos"),
        icon=":material/paid:",
        url_path="revenue-analytics",
    )
    publication_page = st.Page(
        lambda: _render_publication_governance_page(context, locale),
        title=("Publication Gate" if is_en else "Publication Gate"),
        icon=":material/account_tree:",
        url_path="publication-governance",
    )
    overview_page = st.Page(
        lambda: _render_executive_page(
            context,
            locale,
            business_page=revenue_page,
            governance_page=publication_page,
            quick_pages={
                "data_quality": quality_page,
                "data_catalog": catalog_page,
                "lgpd_privacy": privacy_page,
                "control_center": control_center_page,
            },
        ),
        title="Overview",
        icon=":material/dashboard:",
        url_path="executive-overview",
    )
    privacy_page = st.Page(
        lambda: _render_lgpd_page(context, locale),
        title=("LGPD & Privacy" if is_en else "LGPD e Privacidade"),
        icon=":material/policy:",
        url_path="lgpd-privacy-risk",
    )
    quality_page = st.Page(
        lambda: _render_quality_page(context, locale),
        title=("Data Quality" if is_en else "Data Quality"),
        icon=":material/check_circle:",
        url_path="data-quality",
    )
    seller_page = st.Page(
        lambda: _render_seller_performance_page(context, locale),
        title=("Seller Performance" if is_en else "Seller Performance"),
        icon=":material/storefront:",
        url_path="seller-performance",
    )
    cohort_page = st.Page(
        lambda: _render_cohort_retention_page(context, locale),
        title=("Cohort Retention" if is_en else "Cohort Retention"),
        icon=":material/grid_view:",
        url_path="cohort-retention",
    )
    catalog_page = st.Page(
        lambda: _render_catalog_page(context, locale),
        title=("Data Contracts & Catalog" if is_en else "Contratos e Cat\u00e1logo"),
        icon=":material/table_view:",
        url_path="data-catalog",
    )
    eda_page = st.Page(
        lambda: _render_eda_page(context, locale),
        title=("Exploratory Analysis" if is_en else "An\u00e1lise Explorat\u00f3ria"),
        icon=":material/monitoring:",
        url_path="technical-analysis",
    )
    evidence_page = st.Page(
        lambda: _render_report_page(context, locale),
        title=("Evidence & Traceability" if is_en else "Evid\u00eancias e rastreabilidade"),
        icon=":material/description:",
        url_path="governance-report",
    )
    control_center_page = st.Page(
        lambda: _render_control_center_page(context, locale),
        title=("Control Center" if is_en else "Central de Controles"),
        icon=":material/admin_panel_settings:",
        url_path="governance-control-center",
    )
    n8n_page = st.Page(
        lambda: _render_n8n_automation_page(context, locale),
        title=("n8n Automation" if is_en else "n8n Automation"),
        icon=":material/account_tree:",
        url_path="n8n-automation",
    )
    genai_page = st.Page(
        lambda: _render_genai_page(context, locale),
        title=("GenAI Insights" if is_en else "GenAI Insights"),
        icon=":material/auto_awesome:",
        url_path="genai-insights",
    )
    assistant_page = st.Page(
        lambda: _render_assistant_page(context, locale),
        title=("RAG Assistant" if is_en else "Assistente RAG"),
        icon=":material/forum:",
        url_path="governance-assistant",
    )
    snowflake_page = st.Page(
        lambda: _render_snowflake_page(context, locale),
        title=("Snowflake Explorer" if is_en else "Snowflake Explorer"),
        icon=":material/database:",
        url_path="snowflake-explorer",
    )

    sections: dict[str, list[StreamlitPage]]
    if is_en:
        sections = {
            "Executive View": [overview_page],
            "Quality & Governance": [quality_page, catalog_page, privacy_page, control_center_page],
            "Analytics": [revenue_page, seller_page, cohort_page, eda_page],
            "Automation & AI": [n8n_page, genai_page, assistant_page, snowflake_page],
            "Observability": [publication_page, evidence_page],
        }
    else:
        sections = {
            "Vis\u00e3o Executiva": [overview_page],
            "Qualidade e Governan\u00e7a": [quality_page, catalog_page, privacy_page, control_center_page],
            "Analytics": [revenue_page, seller_page, cohort_page, eda_page],
            "Automa\u00e7\u00e3o e IA": [n8n_page, genai_page, assistant_page, snowflake_page],
            "Observabilidade": [publication_page, evidence_page],
        }

    navigation = st.navigation(pages=sections, position="sidebar", expanded=True)
    navigation.run()


if __name__ == "__main__":
    main()
