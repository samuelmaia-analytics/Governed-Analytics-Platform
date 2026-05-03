from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.context import GovernanceAppContext, build_context  # noqa: E402
from app.i18n import build_locale_selector, t  # noqa: E402
from app.pages.data_catalog import render_data_catalog  # noqa: E402
from app.pages.data_quality import render_data_quality  # noqa: E402
from app.pages.eda import render_eda  # noqa: E402
from app.pages.executive_overview import render_executive_overview  # noqa: E402
from app.pages.governance_control_center import (
    render_governance_control_center,  # noqa: E402
)
from app.pages.governance_report import render_governance_report  # noqa: E402
from app.pages.lgpd_privacy_risk import render_lgpd_privacy_risk  # noqa: E402

st.set_page_config(
    page_title="Governed Analytics Platform",
    page_icon=":material/policy:",
    layout="wide",
)


def _render_executive_page(context: GovernanceAppContext, locale: str) -> None:
    render_executive_overview(
        context.df,
        context.classification_df,
        context.risk_result,
        context.quality_results,
        locale,
    )


def _render_catalog_page(context: GovernanceAppContext, locale: str) -> None:
    render_data_catalog(context.df, context.classification_df, locale)


def _render_lgpd_page(context: GovernanceAppContext, locale: str) -> None:
    render_lgpd_privacy_risk(context.df, context.classification_df, context.risk_result, locale)


def _render_quality_page(context: GovernanceAppContext, locale: str) -> None:
    render_data_quality(context.quality_results, context.quality_table, locale)


def _render_eda_page(context: GovernanceAppContext, locale: str) -> None:
    render_eda(context.df, locale)


def _render_report_page(context: GovernanceAppContext, locale: str) -> None:
    render_governance_report(context.report_paths, locale)


def _render_control_center_page(context: GovernanceAppContext, locale: str) -> None:
    render_governance_control_center(
        context.df,
        context.classification_df,
        context.risk_result,
        context.quality_results,
        locale,
    )


def main() -> None:
    locale = build_locale_selector()
    st.title(t("app_title", locale))
    st.caption(t("app_caption", locale))
    st.caption("Language: English (US)" if locale == "en-US" else "Idioma: Português (Brasil)")

    context = build_context(locale)

    pages = [
        st.Page(
            lambda: _render_executive_page(context, locale),
            title=t("nav_executive", locale),
            icon=":material/dashboard:",
            url_path="executive-overview",
        ),
        st.Page(
            lambda: _render_catalog_page(context, locale),
            title=t("nav_catalog", locale),
            icon=":material/table_view:",
            url_path="data-catalog",
        ),
        st.Page(
            lambda: _render_lgpd_page(context, locale),
            title=t("nav_lgpd", locale),
            icon=":material/policy:",
            url_path="lgpd-privacy-risk",
        ),
        st.Page(
            lambda: _render_quality_page(context, locale),
            title=t("nav_quality", locale),
            icon=":material/check_circle:",
            url_path="data-quality",
        ),
        st.Page(
            lambda: _render_eda_page(context, locale),
            title=t("nav_eda", locale),
            icon=":material/monitoring:",
            url_path="eda",
        ),
        st.Page(
            lambda: _render_report_page(context, locale),
            title=t("nav_report", locale),
            icon=":material/description:",
            url_path="governance-report",
        ),
        st.Page(
            lambda: _render_control_center_page(context, locale),
            title=t("nav_control_center", locale),
            icon=":material/admin_panel_settings:",
            url_path="governance-control-center",
        ),
    ]
    navigation = st.navigation(pages=pages, position="top")
    navigation.run()


if __name__ == "__main__":
    main()
