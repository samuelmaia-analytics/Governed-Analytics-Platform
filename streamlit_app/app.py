from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ANALYTICS_DIR


st.set_page_config(
    page_title="samuelmaia_DDF_032026 | Executive Commerce Analytics",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)

FACT_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
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


@dataclass(frozen=True)
class FilterState:
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    categories: list[str]
    states: list[str]
    price_range: tuple[float, float]
    freight_range: tuple[float, float]
    order_status: list[str]
    payment_types: list[str]
    geography_mode: str


def render_story_nav() -> None:
    st.markdown(
        """
        <div class="section-shell" style="padding:0.75rem 1rem 0.8rem 1rem;">
            <div class="section-eyebrow">Navegação</div>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
                <span class="hero-badge">1. Contexto</span>
                <span class="hero-badge">2. KPIs</span>
                <span class="hero-badge">3. Tempo</span>
                <span class="hero-badge">4. Categorias</span>
                <span class="hero-badge">5. Regional</span>
                <span class="hero-badge">6. Operação</span>
                <span class="hero-badge">7. Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
            color: {COLORS["muted"]};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background: #EFF6FF;
            color: {COLORS["primary"]};
            border-color: #BFDBFE;
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 14px;
            border: 1px solid {COLORS["border"]};
            background: #FFFFFF;
            color: {COLORS["text"]};
            font-weight: 600;
            padding: 0.6rem 0.9rem;
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


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not FACT_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {FACT_PATH}")

    df = pd.read_parquet(FACT_PATH)
    datetime_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "shipping_limit_date",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "latest_review_creation_date",
        "latest_review_answer_timestamp",
    ]
    for column in datetime_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    df["order_date"] = pd.to_datetime(df.get("order_date", df["order_purchase_timestamp"]), errors="coerce")
    for column in ["review_score_mean", "delivery_time_days", "estimated_delay_days", "total_item_value", "price", "freight_value"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["category_label"] = (
        df["product_category_name_english"]
        .fillna(df["product_category_name"])
        .fillna("unknown")
        .astype(str)
        .str.replace("_", " ")
        .str.title()
    )
    df["customer_state"] = df["customer_state"].fillna("NA")
    df["seller_state"] = df["seller_state"].fillna("NA")
    df["order_status"] = df["order_status"].fillna("unknown").astype(str)
    df["payment_type_mode"] = df["payment_type_mode"].fillna("unknown").astype(str)
    df["is_delayed"] = df["is_delayed"].fillna(False).astype(bool)
    df["month_start"] = df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    df["month_name"] = df["order_purchase_timestamp"].dt.month.map(MONTH_NAME_MAP)
    df["weekday_name"] = df["order_purchase_timestamp"].dt.weekday.map(WEEKDAY_MAP)
    df["quarter_label"] = (
        df["order_purchase_timestamp"].dt.year.astype("Int64").astype(str)
        + " Q"
        + df["order_purchase_timestamp"].dt.quarter.astype("Int64").astype(str)
    )
    return df


def build_default_filter_state(df: pd.DataFrame) -> None:
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()
    all_states = sorted(set(df["customer_state"].dropna().unique()).union(set(df["seller_state"].dropna().unique())))
    defaults = {
        "flt_date_range": (min_date, max_date),
        "flt_categories": sorted(df["category_label"].dropna().unique().tolist()),
        "flt_states": all_states,
        "flt_price_range": (float(df["price"].fillna(0).min()), float(df["price"].fillna(0).quantile(0.99))),
        "flt_freight_range": (float(df["freight_value"].fillna(0).min()), float(df["freight_value"].fillna(0).quantile(0.99))),
        "flt_status": sorted(df["order_status"].dropna().unique().tolist()),
        "flt_payment": sorted(df["payment_type_mode"].dropna().unique().tolist()),
        "flt_geography_mode": "Cliente",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_filters() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("flt_"):
            del st.session_state[key]
    st.rerun()


def build_sidebar_filters(df: pd.DataFrame) -> FilterState:
    build_default_filter_state(df)

    st.sidebar.markdown("### Filtros Globais")
    st.sidebar.markdown(
        "<div class='filter-note'>Os filtros afetam todo o dashboard, incluindo KPIs, gráficos, tabelas e insights.</div>",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Resetar filtros", use_container_width=True):
        reset_filters()

    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()
    date_value = st.sidebar.date_input(
        "Intervalo de datas",
        value=st.session_state["flt_date_range"],
        min_value=min_date,
        max_value=max_date,
        key="flt_date_range",
    )
    if isinstance(date_value, tuple) and len(date_value) == 2:
        start_date, end_date = date_value
    else:
        start_date = end_date = min_date

    categories = st.sidebar.multiselect(
        "Categoria de produto",
        options=sorted(df["category_label"].dropna().unique()),
        default=st.session_state["flt_categories"],
        key="flt_categories",
    )
    states = st.sidebar.multiselect(
        "Estado do cliente ou seller",
        options=sorted(set(df["customer_state"].dropna().unique()).union(set(df["seller_state"].dropna().unique()))),
        default=st.session_state["flt_states"],
        key="flt_states",
    )
    geography_mode = st.sidebar.radio(
        "Dimensão geográfica",
        options=["Cliente", "Seller"],
        horizontal=True,
        key="flt_geography_mode",
    )
    price_range = st.sidebar.slider(
        "Faixa de preço",
        min_value=float(df["price"].fillna(0).min()),
        max_value=float(df["price"].fillna(0).quantile(0.99)),
        value=st.session_state["flt_price_range"],
        key="flt_price_range",
    )
    freight_range = st.sidebar.slider(
        "Faixa de frete",
        min_value=float(df["freight_value"].fillna(0).min()),
        max_value=float(df["freight_value"].fillna(0).quantile(0.99)),
        value=st.session_state["flt_freight_range"],
        key="flt_freight_range",
    )
    order_status = st.sidebar.multiselect(
        "Status do pedido",
        options=sorted(df["order_status"].dropna().unique()),
        default=st.session_state["flt_status"],
        key="flt_status",
    )
    payment_types = st.sidebar.multiselect(
        "Tipo de pagamento",
        options=sorted(df["payment_type_mode"].dropna().unique()),
        default=st.session_state["flt_payment"],
        key="flt_payment",
    )

    return FilterState(
        start_date=pd.Timestamp(start_date),
        end_date=pd.Timestamp(end_date),
        categories=categories,
        states=states,
        price_range=(float(price_range[0]), float(price_range[1])),
        freight_range=(float(freight_range[0]), float(freight_range[1])),
        order_status=order_status,
        payment_types=payment_types,
        geography_mode=geography_mode,
    )


def build_app_mode() -> bool:
    st.sidebar.markdown("### Modo de Uso")
    presentation_mode = st.sidebar.toggle(
        "Modo apresentação",
        value=False,
        help="Oculta blocos secundários e deixa a leitura mais direta para banca, recrutador ou apresentação executiva.",
    )
    return presentation_mode


def filter_dataframe(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    geography_col = "customer_state" if filters.geography_mode == "Cliente" else "seller_state"
    mask = (
        df["order_purchase_timestamp"].between(filters.start_date, filters.end_date + pd.Timedelta(days=1))
        & df["category_label"].isin(filters.categories)
        & df[geography_col].isin(filters.states)
        & df["price"].fillna(0).between(filters.price_range[0], filters.price_range[1])
        & df["freight_value"].fillna(0).between(filters.freight_range[0], filters.freight_range[1])
        & df["order_status"].isin(filters.order_status)
        & df["payment_type_mode"].isin(filters.payment_types)
    )
    filtered = df.loc[mask].copy()
    filtered["selected_state"] = filtered[geography_col]
    return filtered


def get_previous_period_df(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    window_days = max((filters.end_date - filters.start_date).days + 1, 1)
    previous_end = filters.start_date - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=window_days - 1)
    previous_filters = FilterState(
        start_date=previous_start,
        end_date=previous_end,
        categories=filters.categories,
        states=filters.states,
        price_range=filters.price_range,
        freight_range=filters.freight_range,
        order_status=filters.order_status,
        payment_types=filters.payment_types,
        geography_mode=filters.geography_mode,
    )
    return filter_dataframe(df, previous_filters)


def to_order_level(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("order_purchase_timestamp").drop_duplicates(subset=["order_id"], keep="last").copy()


def format_currency(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def format_currency_compact(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.1f}K"
    return f"R$ {value:.0f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


def calc_delta(current: float, previous: float) -> str:
    if previous in (0, None) or pd.isna(previous):
        return "Sem base anterior"
    delta = ((current / previous) - 1) * 100
    prefix = "+" if delta >= 0 else ""
    return f"{prefix}{delta:.1f}% vs. período anterior"


def metric_card(label: str, value: str, delta: str, help_text: str) -> None:
    st.metric(label=label, value=value, delta=delta, help=help_text)


def build_metrics(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> list[dict[str, str]]:
    current_orders = to_order_level(current_df)
    previous_orders = to_order_level(previous_df)
    current_delivered = current_orders[current_orders["order_delivered_customer_date"].notna()].copy()
    previous_delivered = previous_orders[previous_orders["order_delivered_customer_date"].notna()].copy()

    revenue = float(current_df["total_item_value"].sum())
    revenue_prev = float(previous_df["total_item_value"].sum())
    total_orders = float(current_orders["order_id"].nunique())
    total_orders_prev = float(previous_orders["order_id"].nunique())
    avg_ticket = revenue / total_orders if total_orders else 0.0
    avg_ticket_prev = revenue_prev / total_orders_prev if total_orders_prev else 0.0
    customers = float(current_orders["customer_unique_id"].nunique())
    customers_prev = float(previous_orders["customer_unique_id"].nunique())
    avg_delivery = float(current_delivered["delivery_time_days"].mean()) if len(current_delivered) else 0.0
    avg_delivery_prev = float(previous_delivered["delivery_time_days"].mean()) if len(previous_delivered) else 0.0
    delay_rate = float(current_delivered["is_delayed"].mean() * 100) if len(current_delivered) else 0.0
    delay_rate_prev = float(previous_delivered["is_delayed"].mean() * 100) if len(previous_delivered) else 0.0
    avg_review = float(current_orders["review_score_mean"].mean()) if len(current_orders) else 0.0
    avg_review_prev = float(previous_orders["review_score_mean"].mean()) if len(previous_orders) else 0.0
    avg_freight = float(current_df["freight_value"].mean()) if len(current_df) else 0.0
    avg_freight_prev = float(previous_df["freight_value"].mean()) if len(previous_df) else 0.0

    return [
        {"label": "Receita total", "value": format_currency_compact(revenue), "delta": calc_delta(revenue, revenue_prev), "help": "Soma de item e frete no recorte filtrado."},
        {"label": "Total de pedidos", "value": format_number(total_orders), "delta": calc_delta(total_orders, total_orders_prev), "help": "Quantidade única de pedidos no período."},
        {"label": "Ticket médio", "value": format_currency(avg_ticket), "delta": calc_delta(avg_ticket, avg_ticket_prev), "help": "Receita total dividida pelo número de pedidos."},
        {"label": "Total de clientes", "value": format_number(customers), "delta": calc_delta(customers, customers_prev), "help": "Clientes únicos no recorte filtrado."},
        {"label": "Prazo médio", "value": f"{avg_delivery:.1f} dias" if avg_delivery else "N/A", "delta": calc_delta(avg_delivery, avg_delivery_prev), "help": "Tempo médio entre compra e entrega para pedidos entregues."},
        {"label": "Taxa de atraso", "value": format_pct(delay_rate), "delta": calc_delta(delay_rate, delay_rate_prev), "help": "Percentual de pedidos entregues após a data estimada."},
        {"label": "Nota média", "value": f"{avg_review:.2f}" if avg_review else "N/A", "delta": calc_delta(avg_review, avg_review_prev), "help": "Média de review em nível de pedido."},
        {"label": "Frete médio", "value": format_currency(avg_freight), "delta": calc_delta(avg_freight, avg_freight_prev), "help": "Valor médio de frete por item vendido."},
    ]


def render_header(df: pd.DataFrame, filters: FilterState) -> None:
    period_text = f"{filters.start_date:%d/%m/%Y} a {filters.end_date:%d/%m/%Y}"
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-top">
                <div>
                    <span class="hero-badge">samuelmaia_DDF_032026</span>
                    <h1 class="hero-title">Executive Commerce Analytics</h1>
                    <p class="hero-subtitle">
                        Painel executivo para leitura rápida de receita, categorias, operação e experiência do cliente,
                        transformando o dataset Olist em uma camada analítica pronta para decisão.
                    </p>
                </div>
                <div class="hero-badge">Dataset Olist | Brazilian E-Commerce Public Dataset</div>
            </div>
            <div class="hero-dataset">
                <div class="hero-stat">
                    <strong>Objetivo analítico</strong>
                    Entender onde o negócio cresce, onde perde eficiência e onde estão as prioridades operacionais.
                </div>
                <div class="hero-stat">
                    <strong>Leitura atual</strong>
                    Recorte ativo de {period_text}, com filtros globais refletidos em indicadores, visuais e insights.
                </div>
                <div class="hero-stat">
                    <strong>Base do dashboard</strong>
                    Tabela <code>fact_orders_enriched</code> em parquet, modelada para consumo analítico e dashboard executivo.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, copy: str) -> None:
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-eyebrow'>{eyebrow}</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section-title'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='section-copy'>{copy}</p>", unsafe_allow_html=True)


def close_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def base_layout(fig: go.Figure, *, show_legend: bool = False) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family=APP_FONT, size=13, color=COLORS["text"]),
        title_font=dict(size=18, color=COLORS["text"]),
        margin=dict(l=24, r=20, t=62, b=24),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"], font=dict(family=APP_FONT, color=COLORS["text"])),
        height=375,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]))
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]))
    return fig


def render_kpi_row(metrics: list[dict[str, str]]) -> None:
    st.markdown(
        """
        <div class="kpi-shell">
            <div class="section-eyebrow">KPI Layer</div>
            <h2 class="section-title">Indicadores principais do recorte</h2>
            <p class="section-copy">
                Os KPIs abaixo resumem escala comercial, monetização, satisfação e eficiência operacional,
                com comparação contra o período imediatamente anterior quando houver base.
            </p>
        """,
        unsafe_allow_html=True,
    )
    row1 = st.columns(4, gap="medium")
    row2 = st.columns(4, gap="medium")
    for idx, metric in enumerate(metrics[:4]):
        with row1[idx]:
            metric_card(metric["label"], metric["value"], metric["delta"], metric["help"])
    for idx, metric in enumerate(metrics[4:8]):
        with row2[idx]:
            metric_card(metric["label"], metric["value"], metric["delta"], metric["help"])
    st.markdown("</div>", unsafe_allow_html=True)


def build_smart_summary(df: pd.DataFrame) -> dict[str, object]:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()
    category_perf = (
        df.groupby("category_label", as_index=False)
        .agg(revenue=("total_item_value", "sum"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    top_category = category_perf.iloc[0] if not category_perf.empty else None

    monthly = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    trend_text = "Série temporal insuficiente para leitura de tendência."
    if len(monthly) >= 2:
        latest = float(monthly.iloc[-1]["revenue"])
        previous = float(monthly.iloc[-2]["revenue"])
        delta = ((latest / previous) - 1) * 100 if previous else 0
        if delta > 5:
            trend_text = f"A receita no fim do recorte acelera {delta:.1f}% frente ao mês anterior."
        elif delta < -5:
            trend_text = f"A receita no fim do recorte recua {abs(delta):.1f}% frente ao mês anterior."
        else:
            trend_text = f"A receita no fim do recorte permanece estável, com variação de {delta:.1f}%."

    state_perf = (
        df.groupby("selected_state", as_index=False)
        .agg(revenue=("total_item_value", "sum"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    top_state = state_perf.iloc[0] if not state_perf.empty else None

    logistics = (
        delivered.groupby("category_label", as_index=False)
        .agg(delayed_pct=("is_delayed", "mean"), avg_delivery_time=("delivery_time_days", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 30")
        .sort_values(["delayed_pct", "avg_delivery_time"], ascending=[False, False])
    )
    top_logistics = logistics.iloc[0] if not logistics.empty else None

    recommendations: list[str] = []
    if top_category is not None:
        recommendations.append(
            f"Proteger {top_category['category_label']} com revisão de estoque, preço e disponibilidade, porque ela lidera a geração de receita."
        )
    if top_state is not None:
        recommendations.append(
            f"Priorizar a operação em {top_state['selected_state']}, principal praça comercial do recorte, com revisão de frete e SLA."
        )
    if top_logistics is not None and float(top_logistics["delayed_pct"]) * 100 > 12:
        recommendations.append(
            f"Abrir diagnóstico logístico em {top_logistics['category_label']}, que concentra o maior alerta de atraso."
        )
    avg_review = float(order_level["review_score_mean"].mean()) if len(order_level) else 0
    if avg_review and avg_review < 4.0:
        recommendations.append(
            "Cruzar reviews, atraso e status de pedido para identificar a principal causa de deterioração da satisfação."
        )
    if not recommendations:
        recommendations.append(
            "O recorte atual está equilibrado; a melhor oportunidade é aprofundar segmentações por estado, categoria e pagamento."
        )

    return {
        "summary": " ".join(
            [
                f"A categoria líder é {top_category['category_label']}, com {format_currency(float(top_category['revenue']))}." if top_category is not None else "Sem categoria líder disponível.",
                trend_text,
                f"A praça mais forte é {top_state['selected_state']}, concentrando {format_currency(float(top_state['revenue']))}." if top_state is not None else "Sem destaque geográfico disponível.",
                f"O principal gargalo logístico está em {top_logistics['category_label']}, com {format_pct(float(top_logistics['delayed_pct']) * 100)} de atraso." if top_logistics is not None else "Sem alerta logístico relevante no recorte.",
            ]
        ),
        "chips": [
            {"label": "Top categoria", "value": f"{top_category['category_label']} • {format_currency(float(top_category['revenue']))}" if top_category is not None else "N/A"},
            {"label": "Tendência temporal", "value": trend_text},
            {"label": "Região mais forte", "value": f"{top_state['selected_state']} • {format_currency(float(top_state['revenue']))}" if top_state is not None else "N/A"},
            {"label": "Alerta logístico", "value": f"{top_logistics['category_label']} • {format_pct(float(top_logistics['delayed_pct']) * 100)}" if top_logistics is not None else "N/A"},
        ],
        "recommendations": recommendations[:4],
    }


def build_filter_context_summary(df: pd.DataFrame, filters: FilterState) -> list[tuple[str, str]]:
    orders = to_order_level(df)
    return [
        ("Período", f"{filters.start_date:%d/%m/%Y} a {filters.end_date:%d/%m/%Y}"),
        ("Categorias", format_number(len(filters.categories))),
        ("Estados", format_number(len(filters.states))),
        ("Pedidos no recorte", format_number(orders["order_id"].nunique())),
    ]


def render_context_bar(df: pd.DataFrame, filters: FilterState) -> None:
    items = build_filter_context_summary(df, filters)
    items_html = "".join(
        f"<div class='hero-stat'><strong>{label}</strong>{value}</div>" for label, value in items
    )
    st.markdown(
        f"""
        <div class="section-shell" style="padding:0.9rem 1rem 0.95rem 1rem;">
            <div class="section-eyebrow">Contexto do Recorte</div>
            <p class="section-copy" style="margin-bottom:0.35rem;">
                Resumo executivo dos filtros ativos para facilitar leitura rápida da sessão atual do dashboard.
            </p>
            <div class="hero-dataset" style="margin-top:0.35rem;">
                {items_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_smart_summary(df: pd.DataFrame) -> None:
    insights = build_smart_summary(df)
    chip_html = "".join(
        f"<div class='copilot-chip'><strong>{chip['label']}</strong><span>{chip['value']}</span></div>" for chip in insights["chips"]
    )
    rec_html = "".join(f"<li>{item}</li>" for item in insights["recommendations"])
    st.markdown(
        f"""
        <div class="copilot-shell">
            <div class="section-eyebrow">Insights Inteligentes</div>
            <h2 class="section-title" style="margin-top:0.15rem;">Copiloto analítico do recorte filtrado</h2>
            <p class="section-copy" style="margin-bottom:0.2rem;">{insights["summary"]}</p>
            <div class="copilot-grid">{chip_html}</div>
            <div class="divider-label">Recomendações automáticas</div>
            <ul style="margin:0.3rem 0 0.1rem 1.1rem; color:{COLORS["muted"]}; line-height:1.65;">
                {rec_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_revenue_line(df: pd.DataFrame) -> go.Figure:
    timeline = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    fig = px.line(timeline, x="month_start", y="revenue", title="Como a receita evolui ao longo do tempo", labels={"month_start": "Período", "revenue": "Receita"})
    fig.update_traces(line=dict(color=COLORS["primary"], width=3.5), marker=dict(size=7))
    return base_layout(fig)


def chart_orders_area(df: pd.DataFrame) -> go.Figure:
    timeline = df.groupby("month_start", as_index=False).agg(orders=("order_id", "nunique")).sort_values("month_start")
    fig = px.area(timeline, x="month_start", y="orders", title="Como o volume de pedidos varia no tempo", labels={"month_start": "Período", "orders": "Pedidos"})
    fig.update_traces(line=dict(color=COLORS["secondary"], width=2.8), fillcolor="rgba(59, 130, 246, 0.16)")
    return base_layout(fig)


def chart_seasonality_heatmap(df: pd.DataFrame) -> go.Figure:
    heatmap_df = (
        df.assign(month_num=df["order_purchase_timestamp"].dt.month, weekday_num=df["order_purchase_timestamp"].dt.weekday)
        .groupby(["weekday_num", "month_num"], as_index=False)
        .agg(revenue=("total_item_value", "sum"))
    )
    pivot_df = heatmap_df.pivot(index="weekday_num", columns="month_num", values="revenue").reindex(index=range(7), columns=range(1, 13)).fillna(0)
    fig = px.imshow(
        pivot_df,
        x=[MONTH_NAME_MAP[idx] for idx in pivot_df.columns],
        y=[WEEKDAY_MAP[idx] for idx in pivot_df.index],
        color_continuous_scale=[[0, "#EFF6FF"], [0.5, "#93C5FD"], [1, "#1D4ED8"]],
        title="Sazonalidade de receita por mês e dia da semana",
        labels=dict(x="Mês", y="Dia da semana", color="Receita"),
        aspect="auto",
    )
    fig.update_layout(height=405)
    return base_layout(fig)


def chart_delay_by_period(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    period_df = delivered.groupby("quarter_label", as_index=False).agg(delay_rate=("is_delayed", "mean")).sort_values("quarter_label")
    period_df["delay_rate"] = period_df["delay_rate"] * 100
    fig = px.bar(period_df, x="quarter_label", y="delay_rate", title="Quais períodos concentram pior desempenho operacional", labels={"quarter_label": "Trimestre", "delay_rate": "Taxa de atraso (%)"}, color_discrete_sequence=[COLORS["highlight"]])
    return base_layout(fig)


def chart_top_categories_revenue(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("revenue", ascending=False).head(12).sort_values("revenue")
    fig = px.bar(category_df, x="revenue", y="category_label", orientation="h", title="Quais categorias mais faturam", labels={"category_label": "Categoria", "revenue": "Receita"}, color_discrete_sequence=[COLORS["primary"]])
    return base_layout(fig)


def chart_top_categories_orders(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(orders=("order_id", "nunique")).sort_values("orders", ascending=False).head(10)
    fig = px.bar(category_df, x="category_label", y="orders", title="Quais categorias mais vendem", labels={"category_label": "Categoria", "orders": "Pedidos"}, color_discrete_sequence=[COLORS["secondary"]])
    fig.update_xaxes(tickangle=-28)
    return base_layout(fig)


def chart_category_share_donut(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("revenue", ascending=False)
    top_df = category_df.head(7).copy()
    others_revenue = category_df.iloc[7:]["revenue"].sum()
    if others_revenue > 0:
        top_df = pd.concat([top_df, pd.DataFrame([{"category_label": "Outras", "revenue": others_revenue}])], ignore_index=True)

    fig = px.pie(
        top_df,
        names="category_label",
        values="revenue",
        hole=0.58,
        title="Participação de receita por categoria",
        color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], "#93C5FD", "#BFDBFE", "#DBEAFE", COLORS["teal"], "#9CA3AF", "#E5E7EB"],
    )
    return base_layout(fig, show_legend=True)


def chart_category_value_vs_satisfaction(df: pd.DataFrame) -> go.Figure:
    category_df = (
        df.groupby("category_label", as_index=False)
        .agg(avg_price=("price", "mean"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"), revenue=("total_item_value", "sum"))
        .query("orders >= 40")
    )
    fig = px.scatter(
        category_df,
        x="avg_price",
        y="avg_review",
        size="orders",
        color="revenue",
        hover_name="category_label",
        title="Onde alto volume encontra baixa satisfação",
        labels={"avg_price": "Preço médio", "avg_review": "Nota média", "revenue": "Receita"},
        color_continuous_scale=[[0, "#DBEAFE"], [0.5, "#93C5FD"], [1, COLORS["primary"]]],
    )
    return base_layout(fig)


def build_state_table(df: pd.DataFrame) -> pd.DataFrame:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()
    state_df = (
        df.groupby("selected_state", as_index=False)
        .agg(receita=("total_item_value", "sum"), pedidos=("order_id", "nunique"), clientes=("customer_unique_id", "nunique"), frete_medio=("freight_value", "mean"))
        .merge(
            delivered.groupby("selected_state", as_index=False).agg(prazo_medio=("delivery_time_days", "mean"), atraso_pct=("is_delayed", "mean"), review_medio=("review_score_mean", "mean")),
            on="selected_state",
            how="left",
        )
        .sort_values("receita", ascending=False)
    )
    state_df["atraso_pct"] = state_df["atraso_pct"] * 100
    state_df["ticket_medio"] = state_df["receita"] / state_df["pedidos"].replace(0, pd.NA)
    return state_df.rename(columns={"selected_state": "uf"})


def render_regional_kpi(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="regional-kpi">
            <strong>{label}</strong>
            <span>{value}</span>
            <div class="footer-note" style="margin-top:0.2rem;">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_regional_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    display_df = df.copy()
    return (
        display_df.style.format(
            {
                "receita": lambda x: format_currency(float(x)),
                "pedidos": lambda x: format_number(float(x)),
                "ticket_medio": lambda x: format_currency(float(x)) if pd.notna(x) else "N/A",
                "frete_medio": lambda x: format_currency(float(x)) if pd.notna(x) else "N/A",
                "prazo_medio": lambda x: f"{x:.1f} dias" if pd.notna(x) else "N/A",
                "atraso_pct": lambda x: format_pct(float(x)) if pd.notna(x) else "N/A",
                "review_medio": lambda x: f"{x:.2f}" if pd.notna(x) else "N/A",
            }
        )
        .background_gradient(subset=["receita"], cmap="Blues")
        .background_gradient(subset=["atraso_pct"], cmap="Reds")
        .background_gradient(subset=["review_medio"], cmap="BuGn")
    )


def build_regional_insights(df: pd.DataFrame) -> list[str]:
    state_df = build_state_table(df).query("pedidos >= 80").copy()
    insights: list[str] = []
    if state_df.empty:
        return ["O recorte filtrado não possui massa suficiente por UF para uma leitura regional robusta."]

    top_revenue = state_df.sort_values("receita", ascending=False).iloc[0]
    worst_delay = state_df.sort_values("atraso_pct", ascending=False).iloc[0]
    highest_freight = state_df.sort_values("frete_medio", ascending=False).iloc[0]
    lowest_review = state_df.sort_values("review_medio", ascending=True).iloc[0]

    insights.append(
        f"{top_revenue['uf']} lidera em receita e deve ser tratada como praça prioritária para captura de valor e eficiência comercial."
    )
    insights.append(
        f"{worst_delay['uf']} apresenta a pior taxa de atraso entre as principais UFs, sinalizando prioridade operacional imediata."
    )
    insights.append(
        f"{highest_freight['uf']} concentra o frete médio mais alto no recorte, o que pode pressionar margem e percepção de valor."
    )
    insights.append(
        f"{lowest_review['uf']} registra a menor satisfação média e merece investigação cruzando SLA, frete e status de pedido."
    )
    return insights


def chart_state_revenue(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).head(12).sort_values("receita")
    fig = px.bar(state_df, x="receita", y="uf", orientation="h", title="Quais estados geram mais receita", labels={"uf": "UF", "receita": "Receita"}, color_discrete_sequence=[COLORS["primary"]])
    return base_layout(fig)


def chart_state_delivery_time(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).query("pedidos >= 80").sort_values("prazo_medio", ascending=False).head(12).sort_values("prazo_medio")
    fig = px.bar(
        state_df,
        x="prazo_medio",
        y="uf",
        orientation="h",
        title="Quais estados têm pior prazo médio de entrega",
        labels={"uf": "UF", "prazo_medio": "Prazo médio (dias)"},
        color_discrete_sequence=[COLORS["highlight"]],
    )
    return base_layout(fig)


def chart_state_delay_rate(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).query("pedidos >= 80").sort_values("atraso_pct", ascending=False).head(12).sort_values("atraso_pct")
    fig = px.bar(
        state_df,
        x="atraso_pct",
        y="uf",
        orientation="h",
        title="Quais estados concentram maior taxa de atraso",
        labels={"uf": "UF", "atraso_pct": "Taxa de atraso (%)"},
        color_discrete_sequence=[COLORS["danger"]],
    )
    return base_layout(fig)


def chart_delivery_boxplot(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    fig = px.box(
        delivered,
        x="order_status",
        y="delivery_time_days",
        color="order_status",
        title="Qual a distribuição dos prazos de entrega",
        labels={"order_status": "Status do pedido", "delivery_time_days": "Prazo de entrega (dias)"},
    )
    fig.update_layout(showlegend=False)
    return base_layout(fig)


def chart_delay_by_category(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    category_df = (
        delivered.groupby("category_label", as_index=False)
        .agg(delay_rate=("is_delayed", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 50")
        .sort_values("delay_rate", ascending=False)
        .head(12)
        .sort_values("delay_rate")
    )
    category_df["delay_rate"] = category_df["delay_rate"] * 100
    fig = px.bar(category_df, x="delay_rate", y="category_label", orientation="h", title="Quais categorias concentram mais atrasos", labels={"delay_rate": "Taxa de atraso (%)", "category_label": "Categoria"}, color_discrete_sequence=[COLORS["highlight"]])
    return base_layout(fig)


def chart_delivery_vs_review(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    category_df = (
        delivered.groupby("category_label", as_index=False)
        .agg(avg_delivery=("delivery_time_days", "mean"), avg_review=("review_score_mean", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 40")
    )
    fig = px.scatter(
        category_df,
        x="avg_delivery",
        y="avg_review",
        size="orders",
        color="orders",
        hover_name="category_label",
        title="Existe relação entre atraso e avaliação",
        labels={"avg_delivery": "Prazo médio de entrega", "avg_review": "Nota média", "orders": "Pedidos"},
        color_continuous_scale=[[0, "#D1FAE5"], [0.5, "#6EE7B7"], [1, COLORS["teal"]]],
    )
    return base_layout(fig)


def render_chart(fig: go.Figure, insight: str) -> None:
    st.plotly_chart(fig, use_container_width=True)
    st.caption(insight)


def render_temporal_section(df: pd.DataFrame) -> None:
    render_section_header("Análise Temporal", "Tendência, sazonalidade e ritmo operacional", "Esta seção mostra quando o negócio acelera, onde a sazonalidade aparece e em quais janelas a operação parece mais pressionada.")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_revenue_line(df), "A curva de receita destaca aceleração, desaceleração e momentos em que o crescimento merece leitura conjunta com capacidade operacional.")
    with col2:
        render_chart(chart_orders_area(df), "O volume de pedidos ajuda a diferenciar crescimento de receita por demanda versus crescimento por ticket.")
    col3, col4 = st.columns(2, gap="large")
    with col3:
        render_chart(chart_seasonality_heatmap(df), "O heatmap localiza concentração de receita por combinação de mês e dia da semana, sinalizando sazonalidades acionáveis.")
    with col4:
        render_chart(chart_delay_by_period(df), "O atraso por período expõe janelas em que a expansão comercial pode ter tensionado a execução logística.")
    close_section()


def render_category_section(df: pd.DataFrame) -> None:
    render_section_header("Análise por Categoria", "Quais categorias sustentam resultado, risco e oportunidade", "A leitura por categoria conecta faturamento, volume, participação e satisfação para separar o que gera escala do que exige correção de rota.")
    top_row_left, top_row_right = st.columns(2, gap="large")
    with top_row_left:
        render_chart(chart_top_categories_revenue(df), "O ranking por receita revela os grupos com maior peso comercial e maior sensibilidade para preço, estoque e sortimento.")
    with top_row_right:
        render_chart(chart_top_categories_orders(df), "O ranking por pedidos mostra quais categorias sustentam volume transacional e ajudam a separar escala de monetização.")
    bottom_row_left, bottom_row_right = st.columns(2, gap="large")
    with bottom_row_left:
        render_chart(chart_category_share_donut(df), "A participação por categoria mostra o grau de concentração da receita e a dependência do negócio em poucos clusters.")
    with bottom_row_right:
        render_chart(chart_category_value_vs_satisfaction(df), "A dispersão cruza preço médio, escala e satisfação para destacar categorias com alto volume e percepção inferior à média.")
    close_section()


def render_geography_section(df: pd.DataFrame, geography_mode: str) -> None:
    geography_label = "cliente" if geography_mode == "Cliente" else "seller"
    render_section_header("Performance Regional e Gargalos Operacionais", f"Quais UFs geram mais valor e onde o desempenho perde eficiência ({geography_label})", "A leitura regional mostra quais estados concentram receita, onde o prazo se alonga e onde custo logístico e satisfação entram em tensão.")
    regional_df = build_state_table(df).query("pedidos >= 80").copy()
    if regional_df.empty:
        st.info("O recorte atual não possui massa suficiente para uma análise regional comparável por UF.")
        close_section()
        return

    best_revenue = regional_df.sort_values("receita", ascending=False).iloc[0]
    worst_delay = regional_df.sort_values("atraso_pct", ascending=False).iloc[0]

    top_kpi_left, top_kpi_right = st.columns(2, gap="large")
    with top_kpi_left:
        render_regional_kpi(
            "Melhor UF em receita",
            f"{best_revenue['uf']} • {format_currency(float(best_revenue['receita']))}",
            f"{format_number(float(best_revenue['pedidos']))} pedidos e ticket médio de {format_currency(float(best_revenue['ticket_medio']))}.",
        )
    with top_kpi_right:
        render_regional_kpi(
            "Pior UF em taxa de atraso",
            f"{worst_delay['uf']} • {format_pct(float(worst_delay['atraso_pct']))}",
            f"Prazo médio de {worst_delay['prazo_medio']:.1f} dias e review médio de {worst_delay['review_medio']:.2f}.",
        )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_state_revenue(df), "O ranking por UF mostra onde a operação concentra maior valor comercial e onde a priorização regional tende a gerar mais retorno.")
    with col2:
        render_chart(chart_state_delivery_time(df), "O prazo médio por UF torna explícito onde o serviço logístico está mais pressionado, mesmo em estados comercialmente relevantes.")

    col3, col4 = st.columns((1.15, 0.85), gap="large")
    with col3:
        table_df = regional_df[["uf", "receita", "pedidos", "ticket_medio", "frete_medio", "prazo_medio", "atraso_pct", "review_medio"]].sort_values("receita", ascending=False)
        st.dataframe(style_regional_table(table_df), use_container_width=True, height=420)
        st.caption("Tabela analítica por UF com foco em escala comercial, custo logístico e percepção de experiência.")
    with col4:
        render_chart(chart_state_delay_rate(df), "A taxa de atraso por UF ajuda a localizar gargalos operacionais persistentes e orientar revisão de SLA regional.")
        regional_insights_html = "".join(f"<li>{item}</li>" for item in build_regional_insights(df))
        st.markdown(
            f"""
            <div class="regional-kpi" style="margin-top:0.8rem;">
                <strong>Insights regionais</strong>
                <div class="footer-note" style="margin-top:0.35rem;">
                    <ul style="margin:0 0 0 1rem; padding:0; line-height:1.65;">
                        {regional_insights_html}
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    close_section()


def render_operations_section(df: pd.DataFrame) -> None:
    render_section_header("Operação e Logística", "Onde estão os gargalos que afetam SLA, satisfação e eficiência", "A leitura operacional conecta prazo, atraso e percepção do cliente para direcionar ações de SLA, transporte e jornada.")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_delivery_boxplot(df), "A distribuição de prazo mostra dispersão operacional e ajuda a separar rotinas estáveis de exceções severas.")
    with col2:
        render_chart(chart_delay_by_category(df), "Categorias com maior taxa de atraso são candidatas naturais para revisão de SLA, sellers e estratégia de fulfilment.")
    render_chart(chart_delivery_vs_review(df), "O relacionamento entre prazo médio e nota média indica em quais clusters a experiência do cliente é mais sensível à lentidão logística.")
    close_section()


def build_executive_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()

    category_summary = (
        df.groupby("category_label", as_index=False)
        .agg(revenue=("total_item_value", "sum"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    risky_category_df = category_summary.query("orders >= 40").sort_values(["avg_review", "revenue"], ascending=[True, False])
    risky_category = risky_category_df.iloc[0] if not risky_category_df.empty else None

    state_summary = (
        delivered.groupby("selected_state", as_index=False)
        .agg(revenue=("total_item_value", "sum"), avg_delivery=("delivery_time_days", "mean"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    slow_state_df = state_summary.query("revenue > 0").sort_values(["avg_delivery", "revenue"], ascending=[False, False])
    slow_state = slow_state_df.iloc[0] if not slow_state_df.empty else None

    pay_summary = df.groupby("payment_type_mode", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("revenue", ascending=False)
    top_payment = pay_summary.iloc[0] if not pay_summary.empty else None

    monthly = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    growth_text = "A série atual não tem massa suficiente para comparação temporal robusta."
    if len(monthly) >= 2:
        latest = float(monthly.iloc[-1]["revenue"])
        previous = float(monthly.iloc[-2]["revenue"])
        delta = ((latest / previous) - 1) * 100 if previous else 0
        if delta >= 5:
            growth_text = f"O recorte encerra com aceleração de {delta:.1f}% na receita frente ao mês anterior."
        elif delta <= -5:
            growth_text = f"O recorte encerra com retração de {abs(delta):.1f}% na receita frente ao mês anterior."
        else:
            growth_text = f"O recorte encerra com estabilidade relativa, variando {delta:.1f}% na receita."

    return [
        {"title": "Sinal comercial", "text": growth_text},
        {"title": "Risco por categoria", "text": f"{risky_category['category_label']} combina relevância comercial com satisfação abaixo da média e deve ser tratada como prioridade de experiência." if risky_category is not None else "Não houve categoria com volume suficiente para um alerta de risco consistente no recorte."},
        {"title": "Gargalo regional", "text": f"{slow_state['selected_state']} aparece como praça de alto peso com prazo médio elevado, sugerindo ganho operacional direto com revisão de SLA regional." if slow_state is not None else "Não houve concentração regional relevante para um alerta operacional claro."},
        {"title": "Dependência de pagamento", "text": f"{top_payment['payment_type_mode']} lidera a captura de receita, reforçando a importância de manter checkout, aprovação e conciliação sem fricção." if top_payment is not None else "Não foi possível identificar concentração relevante por meio de pagamento."},
    ]


def render_executive_insights(df: pd.DataFrame) -> None:
    render_section_header("Insights Executivos", "Síntese final para decisão de negócio", "Esta camada final resume o recorte em sinais de ação, destacando o que merece atenção imediata de negócio e operação.")
    cards_html = "".join(f"<div class='insight-card'><h4>{card['title']}</h4><p>{card['text']}</p></div>" for card in build_executive_insights(df))
    st.markdown(f"<div class='insight-grid'>{cards_html}</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='footer-note'>Leitura recomendada: primeiro validar tendência e concentração de receita, depois localizar gargalos regionais e, por fim, priorizar ações logísticas com maior impacto em valor e experiência.</p>",
        unsafe_allow_html=True,
    )
    close_section()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_support_tables(df: pd.DataFrame) -> None:
    render_section_header("Apoio Analítico", "Tabelas para exploração detalhada e exportação", "As tabelas abaixo complementam a leitura executiva com recortes prontos para inspeção, documentação e exportação local.")
    category_table = (
        df.groupby("category_label", as_index=False)
        .agg(receita=("total_item_value", "sum"), pedidos=("order_id", "nunique"), preco_medio=("price", "mean"), review_medio=("review_score_mean", "mean"), atraso_pct=("is_delayed", "mean"))
        .sort_values("receita", ascending=False)
        .head(20)
    )
    category_table["atraso_pct"] = category_table["atraso_pct"] * 100
    state_table = build_state_table(df)
    order_table = (
        df[["order_id", "order_status", "selected_state", "category_label", "payment_type_mode", "order_purchase_timestamp", "total_item_value", "delivery_time_days", "estimated_delay_days", "review_score_mean"]]
        .sort_values("order_purchase_timestamp", ascending=False)
        .head(250)
    )
    tabs = st.tabs(["Categorias", "Estados", "Pedidos"])
    for tab, table_name, table_df in [(tabs[0], "categorias", category_table), (tabs[1], "estados", state_table), (tabs[2], "pedidos", order_table)]:
        with tab:
            st.dataframe(table_df, use_container_width=True, height=380)
            st.download_button(label=f"Exportar tabela de {table_name}", data=to_csv_bytes(table_df), file_name=f"{table_name}_dashboard.csv", mime="text/csv", use_container_width=True)
    close_section()


def main() -> None:
    apply_theme()
    try:
        df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    filters = build_sidebar_filters(df)
    presentation_mode = build_app_mode()
    filtered_df = filter_dataframe(df, filters)
    previous_df = get_previous_period_df(df, filters)
    if filtered_df.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    st.sidebar.caption(f"Registros filtrados: {format_number(len(filtered_df))}")
    render_header(filtered_df, filters)
    render_story_nav()
    render_context_bar(filtered_df, filters)
    render_kpi_row(build_metrics(filtered_df, previous_df))
    st.markdown("<div style='height:0.95rem;'></div>", unsafe_allow_html=True)
    render_smart_summary(filtered_df)
    render_temporal_section(filtered_df)
    render_category_section(filtered_df)
    render_geography_section(filtered_df, filters.geography_mode)
    render_operations_section(filtered_df)
    render_executive_insights(filtered_df)
    if not presentation_mode:
        render_support_tables(filtered_df)


if __name__ == "__main__":
    main()
