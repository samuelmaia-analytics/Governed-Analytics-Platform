from __future__ import annotations

import streamlit as st

_BASE_CSS = """
<style>
:root {
  --gap-radius: 14px;
  --gap-bg: rgba(255, 255, 255, 0.78);
  --gap-border: rgba(49, 51, 63, 0.14);
  --gap-muted: rgba(49, 51, 63, 0.65);
}

@media (prefers-color-scheme: dark) {
  :root {
    --gap-bg: rgba(20, 22, 26, 0.72);
    --gap-border: rgba(255, 255, 255, 0.12);
    --gap-muted: rgba(255, 255, 255, 0.70);
  }
}

.gap-hero-title {
  font-size: 34px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: 0.01em;
  margin: 0;
}

.gap-hero-subtitle {
  font-size: 16px;
  color: var(--gap-muted);
  margin-top: 6px;
}

.gap-card {
  background: var(--gap-bg);
  border: 1px solid var(--gap-border);
  border-radius: var(--gap-radius);
  padding: 14px 16px;
}

.gap-card-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--gap-muted);
  margin-bottom: 8px;
}

.gap-card-value {
  font-size: 22px;
  font-weight: 650;
  line-height: 1.2;
  margin: 0;
}

.gap-card-delta {
  font-size: 12px;
  color: var(--gap-muted);
  margin-top: 6px;
}

.gap-section-title {
  font-size: 18px;
  font-weight: 650;
  margin: 18px 0 10px 0;
}

.gap-footer {
  margin-top: 34px;
  padding: 16px 0 6px 0;
  border-top: 1px solid var(--gap-border);
  color: var(--gap-muted);
  font-size: 12px;
}

.gap-footer a { color: inherit; }
</style>
"""


def inject_base_styles() -> None:
    """Inject theme-aware CSS without Streamlit internal selectors."""

    if st.session_state.get("_gap_base_styles", False):
        return
    st.markdown(_BASE_CSS, unsafe_allow_html=True)
    st.session_state["_gap_base_styles"] = True


def render_section_title(title: str) -> None:
    st.markdown(
        f'<div class="gap-section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def render_footer(*, locale: str) -> None:
    is_en = locale == "en-US"
    label = (
        "Personal portfolio project - Samuel Maia"
        if is_en
        else "Projeto pessoal de portf\u00f3lio - Samuel Maia"
    )
    st.markdown(
        """
<div class="gap-footer">
  <div>{label}</div>
  <div>
    <a href="https://github.com/samuelmaia-analytics/Governed-Analytics-Platform" target="_blank" rel="noreferrer">GitHub</a>
    . <a href="https://samuelmaia-analytics.github.io/samuelmaia-analytics/" target="_blank" rel="noreferrer">Portf\u00f3lio</a>
    . <a href="https://www.linkedin.com/in/samuelmaia-analytics/" target="_blank" rel="noreferrer">LinkedIn</a>
  </div>
</div>
        """.format(label=label),
        unsafe_allow_html=True,
    )
