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
) -> None:
    render_executive_overview(
        context.df,
        context.classification_df,
        context.risk_result,
        context.quality_results,
        locale,
        business_page=business_page,
        governance_page=governance_page,
        duckdb_version=get_duckdb_version(),
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
    context = build_context(locale)

    business_page = st.Page(
        lambda: _render_revenue_page(context, locale),
        title="Business Insights",
        icon=":material/paid:",
        url_path="revenue-analytics",
    )
    governance_page = st.Page(
        lambda: _render_publication_governance_page(context, locale),
        title="Publication Governance",
        icon=":material/account_tree:",
        url_path="publication-governance",
    )
    pages = [
        st.Page(
            lambda: _render_executive_page(
                context,
                locale,
                business_page=business_page,
                governance_page=governance_page,
            ),
            title="Portfolio Overview",
            icon=":material/dashboard:",
            url_path="executive-overview",
        ),
        business_page,
        governance_page,
        st.Page(
            lambda: _render_lgpd_page(context, locale),
            title="Privacy & LGPD Controls",
            icon=":material/policy:",
            url_path="lgpd-privacy-risk",
        ),
        st.Page(
            lambda: _render_quality_page(context, locale),
            title="Data Quality",
            icon=":material/check_circle:",
            url_path="data-quality",
        ),
        st.Page(
            lambda: _render_seller_performance_page(context, locale),
            title="Seller Performance",
            icon=":material/storefront:",
            url_path="seller-performance",
        ),
        st.Page(
            lambda: _render_cohort_retention_page(context, locale),
            title="Customer Retention",
            icon=":material/grid_view:",
            url_path="cohort-retention",
        ),
        st.Page(
            lambda: _render_catalog_page(context, locale),
            title="Data Catalog",
            icon=":material/table_view:",
            url_path="data-catalog",
        ),
        st.Page(
            lambda: _render_eda_page(context, locale),
            title="Technical Analysis",
            icon=":material/monitoring:",
            url_path="eda",
        ),
        st.Page(
            lambda: _render_report_page(context, locale),
            title="Governance Evidence",
            icon=":material/description:",
            url_path="governance-report",
        ),
        st.Page(
            lambda: _render_control_center_page(context, locale),
            title="Governance Lab",
            icon=":material/admin_panel_settings:",
            url_path="governance-control-center",
        ),
        st.Page(
            lambda: _render_n8n_automation_page(context, locale),
            title="Automation & Orchestration",
            icon=":material/account_tree:",
            url_path="n8n-automation",
        ),
        st.Page(
            lambda: _render_genai_page(context, locale),
            title="GenAI Experiment",
            icon=":material/auto_awesome:",
            url_path="genai-insights",
        ),
        st.Page(
            lambda: _render_snowflake_page(context, locale),
            title="Snowflake Integration",
            icon=":material/database:",
            url_path="snowflake-explorer",
        ),
    ]
    navigation = st.navigation(pages=pages, position="top")
    navigation.run()


if __name__ == "__main__":
    main()
