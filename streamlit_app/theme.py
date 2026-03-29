from __future__ import annotations

import streamlit as st

APP_FONT = "IBM Plex Sans"

COLORS = {
    "bg": "#F5F7FA",
    "surface": "#FFFFFF",
    "text": "#111827",
    "muted": "#4B5563",
    "border": "#D1D5DB",
    "primary": "#1F4E79",
    "secondary": "#3B82F6",
    "teal": "#0F766E",
    "highlight": "#B45309",
    "success": "#15803D",
    "danger": "#B91C1C",
    "grid": "#E5E7EB",
}

MONTH_NAME_MAP = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}

WEEKDAY_MAP = {
    0: "Seg",
    1: "Ter",
    2: "Qua",
    3: "Qui",
    4: "Sex",
    5: "Sab",
    6: "Dom",
}

NAVIGATION_OPTIONS = [
    ("Visão completa", "Visão"),
    ("Contexto", "Contexto"),
    ("KPIs", "KPIs"),
    ("Tempo", "Tempo"),
    ("Categorias", "Categorias"),
    ("Regional", "Regional"),
    ("Operação", "Operação"),
    ("Saúde", "Saúde"),
    ("Semântica", "Semântica"),
    ("Insights", "Insights"),
]


def set_navigation(target: str) -> None:
    st.session_state["dashboard_section_nav"] = target


def render_story_nav() -> str:
    current = st.session_state.get("dashboard_section_nav", "Visão completa")
    st.markdown("<div class='section-shell' style='padding:0.75rem 1rem 0.9rem 1rem;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-eyebrow'>Navegação</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-copy' style='margin:0.15rem 0 0.7rem 0;'>Use a barra abaixo para navegar entre os blocos principais da leitura executiva.</p>",
        unsafe_allow_html=True,
    )

    nav_columns = st.columns(len(NAVIGATION_OPTIONS), gap="small")
    for idx, (value, label) in enumerate(NAVIGATION_OPTIONS):
        with nav_columns[idx]:
            st.button(
                label,
                key=f"nav_{value}",
                use_container_width=True,
                type="primary" if current == value else "secondary",
                on_click=set_navigation,
                args=(value,),
            )
    st.markdown("</div>", unsafe_allow_html=True)
    return st.session_state.get("dashboard_section_nav", "Visão completa")


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] {{
            font-family: '{APP_FONT}', sans-serif;
        }}
        .stApp {{
            background: {COLORS["bg"]};
            color: {COLORS["text"]};
        }}
        .block-container {{
            max-width: 1440px;
            padding-top: 1.4rem;
            padding-bottom: 2.2rem;
        }}
        div[data-testid="stVerticalBlock"] > div:has(> div.section-shell) {{
            margin-top: 0.2rem;
        }}
        [data-testid="stSidebar"] {{
            background: #EEF2F7;
            border-right: 1px solid {COLORS["border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS["text"]};
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] .filter-note,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{
            color: {COLORS["muted"]} !important;
        }}
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stCheckbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stDateInput label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label {{
            font-weight: 600;
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] * {{
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] .stSlider [role="slider"] {{
            background: {COLORS["primary"]} !important;
            border-color: {COLORS["primary"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="input"] {{
            background: #FFFFFF !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 14px !important;
        }}
        [data-testid="stSidebar"] .stDateInput > div,
        [data-testid="stSidebar"] .stDateInput > div > div,
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"],
        [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"] {{
            background: #FFFFFF !important;
            color: {COLORS["text"]} !important;
            border-color: {COLORS["border"]} !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="input"] input {{
            background: transparent !important;
            color: {COLORS["text"]} !important;
            -webkit-text-fill-color: {COLORS["text"]} !important;
            opacity: 1 !important;
        }}
        [data-testid="stSidebar"] .stDateInput input {{
            background: transparent !important;
            color: {COLORS["text"]} !important;
            -webkit-text-fill-color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 16px;
            background: #FFFFFF;
            overflow: hidden;
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] details,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
            background: #FFFFFF !important;
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{
            background: #F8FBFF !important;
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * {{
            color: {COLORS["text"]} !important;
            fill: {COLORS["muted"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] {{
            background: #FFFFFF !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 14px !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #FFFFFF !important;
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: #FEE2E2 !important;
            color: {COLORS["danger"]} !important;
            border-radius: 10px !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="tag"] * {{
            color: {COLORS["danger"]} !important;
            fill: {COLORS["danger"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="popover"],
        [data-testid="stSidebar"] [role="listbox"] {{
            background: #FFFFFF !important;
            color: {COLORS["text"]} !important;
            border: 1px solid {COLORS["border"]} !important;
        }}
        [data-testid="stSidebar"] [role="option"] {{
            background: #FFFFFF !important;
            color: {COLORS["text"]} !important;
        }}
        [data-testid="stSidebar"] [role="option"]:hover {{
            background: #EFF6FF !important;
            color: {COLORS["primary"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="input"] input::placeholder {{
            color: {COLORS["muted"]} !important;
            -webkit-text-fill-color: {COLORS["muted"]} !important;
            opacity: 1 !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="input"] svg {{
            fill: {COLORS["muted"]} !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLORS["muted"]};
            font-size: 0.9rem;
            font-weight: 600;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 700;
            color: {COLORS["text"]};
        }}
        [data-testid="stMetricDelta"] {{
            color: {COLORS["success"]};
            font-size: 0.86rem;
            font-weight: 600;
        }}
        div[data-testid="metric-container"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 22px;
            padding: 1rem 1rem 0.95rem 1rem;
            box-shadow: 0 8px 18px rgba(17, 24, 39, 0.04);
            position: relative;
            overflow: hidden;
        }}
        div[data-testid="metric-container"]::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: {COLORS["primary"]};
        }}
        .hero-shell {{
            background: {COLORS["surface"]};
            border-radius: 28px;
            padding: 1.65rem 1.8rem;
            border: 1px solid {COLORS["border"]};
            box-shadow: 0 12px 26px rgba(17, 24, 39, 0.05);
            margin-bottom: 1rem;
            color: {COLORS["text"]};
        }}
        .hero-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .hero-badge {{
            display: inline-block;
            padding: 0.42rem 0.75rem;
            border-radius: 999px;
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: {COLORS["primary"]};
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }}
        .hero-title {{
            font-size: 2.15rem;
            line-height: 1.08;
            margin: 0.55rem 0 0.45rem 0;
            font-weight: 700;
        }}
        .hero-subtitle {{
            color: {COLORS["muted"]};
            max-width: 920px;
            font-size: 1rem;
            line-height: 1.55;
            margin: 0;
        }}
        .hero-dataset {{
            margin-top: 1rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.8rem;
        }}
        .hero-stat {{
            background: #F9FAFB;
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }}
        .hero-stat strong {{
            display: block;
            color: {COLORS["text"]};
            margin-bottom: 0.2rem;
            font-size: 0.95rem;
        }}
        .section-shell {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 26px;
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.04);
            padding: 1.15rem 1.2rem 0.8rem 1.2rem;
            margin-bottom: 1.15rem;
        }}
        .kpi-shell {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 26px;
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.04);
            padding: 1.05rem 1.1rem 1.15rem 1.1rem;
            margin-bottom: 1rem;
        }}
        .section-eyebrow {{
            display: inline-block;
            padding: 0.30rem 0.65rem;
            border-radius: 999px;
            background: #EEF2FF;
            color: {COLORS["primary"]};
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }}
        .section-title {{
            margin: 0;
            font-size: 1.3rem;
            color: {COLORS["text"]};
            font-weight: 700;
        }}
        .section-copy {{
            margin: 0.3rem 0 0.9rem 0;
            color: {COLORS["muted"]};
            font-size: 0.95rem;
            line-height: 1.55;
        }}
        .copilot-shell {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 26px;
            padding: 1.25rem 1.3rem;
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.04);
            margin-bottom: 1.15rem;
        }}
        .copilot-grid, .insight-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.85rem;
            margin-top: 0.9rem;
        }}
        .copilot-chip, .insight-card {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 0.95rem 1rem;
        }}
        .copilot-chip strong, .insight-card h4 {{
            display: block;
            color: {COLORS["text"]};
            margin: 0 0 0.2rem 0;
            font-size: 0.98rem;
        }}
        .insight-card p {{
            color: {COLORS["muted"]};
            font-size: 0.94rem;
            line-height: 1.55;
            margin: 0;
        }}
        .divider-label {{
            margin: 1rem 0 0.6rem 0;
            color: {COLORS["muted"]};
            font-size: 0.83rem;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            font-weight: 700;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.45rem;
            margin-bottom: 0.5rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 999px;
            padding: 0.55rem 0.95rem;
            color: {COLORS["muted"]} !important;
            font-weight: 600;
        }}
        .stTabs [data-baseweb="tab"] * {{
            color: inherit !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: #EFF6FF;
            color: {COLORS["primary"]} !important;
            border-color: #BFDBFE;
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid {COLORS["border"]};
            background: #FFFFFF;
            color: {COLORS["text"]} !important;
            font-weight: 600;
            padding: 0.52rem 0.8rem;
            min-height: 2.5rem;
            font-size: 0.92rem;
            letter-spacing: 0.01em;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            border-color: #BFDBFE;
            color: {COLORS["primary"]} !important;
            background: #F8FBFF;
        }}
        .stButton > button[kind="primary"] {{
            background: #EFF6FF;
            border-color: #BFDBFE;
            color: {COLORS["primary"]} !important;
            box-shadow: inset 0 0 0 1px #BFDBFE;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #DBEAFE;
            border-color: #93C5FD;
            color: {COLORS["primary"]} !important;
        }}
        .stButton > button *, .stDownloadButton > button * {{
            color: inherit !important;
        }}
        div[data-testid="stPlotlyChart"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 22px;
            padding: 0.3rem 0.35rem 0.2rem 0.35rem;
            box-shadow: none;
        }}
        [data-testid="stCaptionContainer"] {{
            padding: 0.15rem 0.2rem 0.4rem 0.2rem;
        }}
        .regional-kpi {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
        }}
        .regional-kpi strong {{
            display: block;
            color: {COLORS["muted"]};
            font-size: 0.84rem;
            margin-bottom: 0.22rem;
        }}
        .regional-kpi span {{
            color: {COLORS["text"]};
            font-size: 1.25rem;
            font-weight: 700;
        }}
        .filter-note, .footer-note {{
            color: {COLORS["muted"]};
            font-size: 0.88rem;
            line-height: 1.5;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
