from __future__ import annotations

import streamlit as st

Locale = str

LOCALE_PT_BR = "pt-BR"
LOCALE_EN_US = "en-US"

_TRANSLATIONS: dict[str, dict[Locale, str]] = {
    "app_title": {
        LOCALE_PT_BR: "Governed Analytics Platform",
        LOCALE_EN_US: "Governed Analytics Platform",
    },
    "app_caption": {
        LOCALE_PT_BR: "Analytics Engineering, Data Governance, Data Quality, LGPD e EDA em uma interface executiva.",
        LOCALE_EN_US: "Analytics Engineering, Data Governance, Data Quality, LGPD, and EDA in an executive interface.",
    },
    "language_header": {
        LOCALE_PT_BR: "Idioma",
        LOCALE_EN_US: "Language",
    },
    "language_label": {
        LOCALE_PT_BR: "Selecione o idioma",
        LOCALE_EN_US: "Select language",
    },
    "data_source_header": {
        LOCALE_PT_BR: "Fonte de Dados",
        LOCALE_EN_US: "Data Source",
    },
    "upload_label": {
        LOCALE_PT_BR: "Upload CSV ou Parquet",
        LOCALE_EN_US: "Upload CSV or Parquet",
    },
    "use_sample_toggle": {
        LOCALE_PT_BR: "Usar dataset sintético de exemplo",
        LOCALE_EN_US: "Use synthetic sample dataset",
    },
    "nav_executive": {
        LOCALE_PT_BR: "Visão Executiva",
        LOCALE_EN_US: "Executive Overview",
    },
    "nav_catalog": {
        LOCALE_PT_BR: "Catálogo de Dados",
        LOCALE_EN_US: "Data Catalog",
    },
    "nav_lgpd": {
        LOCALE_PT_BR: "LGPD e Risco de Privacidade",
        LOCALE_EN_US: "LGPD & Privacy Risk",
    },
    "nav_quality": {
        LOCALE_PT_BR: "Qualidade de Dados",
        LOCALE_EN_US: "Data Quality",
    },
    "nav_eda": {
        LOCALE_PT_BR: "EDA",
        LOCALE_EN_US: "EDA",
    },
    "nav_report": {
        LOCALE_PT_BR: "Relatório de Governança",
        LOCALE_EN_US: "Governance Report",
    },
    "nav_control_center": {
        LOCALE_PT_BR: "Central de Controles",
        LOCALE_EN_US: "Control Center",
    },
}


def t(key: str, locale: Locale) -> str:
    if key in _TRANSLATIONS and locale in _TRANSLATIONS[key]:
        return _TRANSLATIONS[key][locale]
    return key


def build_locale_selector() -> Locale:
    st.sidebar.header(t("language_header", LOCALE_PT_BR))
    selected = st.sidebar.selectbox(
        t("language_label", LOCALE_PT_BR),
        options=["Português (Brasil)", "English (US)"],
        key="governance_app_locale",
    )
    if selected == "English (US)":
        return LOCALE_EN_US
    return LOCALE_PT_BR
