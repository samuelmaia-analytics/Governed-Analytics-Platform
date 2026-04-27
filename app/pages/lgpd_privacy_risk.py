from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import PrivacyRiskResult


def render_lgpd_privacy_risk(classification_df: pd.DataFrame, risk_result: PrivacyRiskResult, locale: Locale) -> None:
    st.subheader("LGPD & Privacy Risk" if locale == LOCALE_EN_US else "LGPD e Risco de Privacidade")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Privacy Risk Score" if locale == LOCALE_EN_US else "Score de Risco de Privacidade", f"{risk_result['score']} / 100")
    with col2:
        st.metric("Risk Level" if locale == LOCALE_EN_US else "Nível de Risco", str(risk_result["risk_level"]).upper())

    class_counts = classification_df["lgpd_classification"].value_counts().reset_index()
    class_counts.columns = ["classification", "count"]
    st.bar_chart(class_counts.set_index("classification"))
    st.dataframe(classification_df, width="stretch")
    st.markdown("**Recommendations**" if locale == LOCALE_EN_US else "**Recomendações**")
    for recommendation in risk_result["recommendations"]:
        st.write(f"- {recommendation}")
