from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src.config import PUBLISHED_DASHBOARD_DIR
from streamlit_app.theme import MONTH_NAME_MAP, WEEKDAY_MAP


FACT_PARQUET_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
FACT_CSV_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.csv"


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


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if FACT_PARQUET_PATH.exists():
        df = pd.read_parquet(FACT_PARQUET_PATH)
    elif FACT_CSV_PATH.exists():
        df = pd.read_csv(FACT_CSV_PATH)
    else:
        raise FileNotFoundError(
            f"Arquivo não encontrado: {FACT_PARQUET_PATH} nem {FACT_CSV_PATH}"
        )

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
    min_price = float(df["price"].fillna(0).min())
    max_price = float(df["price"].fillna(0).max())
    min_freight = float(df["freight_value"].fillna(0).min())
    max_freight = float(df["freight_value"].fillna(0).max())
    defaults = {
        "flt_date_range": (min_date, max_date),
        "flt_category_mode": "Todas as categorias",
        "flt_category_value": "Todas as categorias",
        "flt_state_mode": "Todos os estados",
        "flt_state_value": "Todos os estados",
        "flt_status_mode": "Todos os status",
        "flt_status_value": "Todos os status",
        "flt_payment_mode": "Todos os meios",
        "flt_payment_value": "Todos os meios",
        "flt_price_range": (min_price, max_price),
        "flt_freight_range": (min_freight, max_freight),
        "flt_geography_mode": "Cliente",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_filters() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("flt_"):
            del st.session_state[key]
    st.rerun()


def resolve_single_or_all(mode_value: str, selected_value: str, full_options: list[str], all_label: str) -> list[str]:
    if mode_value == all_label or selected_value == all_label:
        return full_options
    return [selected_value]


def build_select_filter(
    *,
    label: str,
    mode_key: str,
    value_key: str,
    all_label: str,
    focus_label: str,
    options: list[str],
) -> list[str]:
    mode = st.sidebar.selectbox(
        label,
        options=[all_label, focus_label],
        key=mode_key,
    )
    if mode == all_label:
        st.sidebar.caption(f"{len(options)} opções consideradas neste filtro.")
        st.session_state[value_key] = all_label
        return options

    selected = st.sidebar.selectbox(
        f"Selecionar {label.lower()}",
        options=options,
        key=value_key,
    )
    st.sidebar.caption(f"Filtro aplicado em {label.lower()}: {selected}.")
    return [selected]


def build_sidebar_filters(df: pd.DataFrame) -> FilterState:
    build_default_filter_state(df)

    category_options = sorted(df["category_label"].dropna().unique())
    state_options = sorted(set(df["customer_state"].dropna().unique()).union(set(df["seller_state"].dropna().unique())))
    status_options = sorted(df["order_status"].dropna().unique())
    payment_options = sorted(df["payment_type_mode"].dropna().unique())

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

    categories = build_select_filter(
        label="Categoria de produto",
        mode_key="flt_category_mode",
        value_key="flt_category_value",
        all_label="Todas as categorias",
        focus_label="Categoria específica",
        options=category_options,
    )
    states = build_select_filter(
        label="Estado do cliente ou seller",
        mode_key="flt_state_mode",
        value_key="flt_state_value",
        all_label="Todos os estados",
        focus_label="UF específica",
        options=state_options,
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
        max_value=float(df["price"].fillna(0).max()),
        value=st.session_state["flt_price_range"],
        key="flt_price_range",
    )
    freight_range = st.sidebar.slider(
        "Faixa de frete",
        min_value=float(df["freight_value"].fillna(0).min()),
        max_value=float(df["freight_value"].fillna(0).max()),
        value=st.session_state["flt_freight_range"],
        key="flt_freight_range",
    )
    order_status = build_select_filter(
        label="Status do pedido",
        mode_key="flt_status_mode",
        value_key="flt_status_value",
        all_label="Todos os status",
        focus_label="Status específico",
        options=status_options,
    )
    payment_types = build_select_filter(
        label="Tipo de pagamento",
        mode_key="flt_payment_mode",
        value_key="flt_payment_value",
        all_label="Todos os meios",
        focus_label="Meio específico",
        options=payment_options,
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
    return st.sidebar.toggle(
        "Modo apresentação",
        value=False,
        help="Simplifica a tela para leitura executiva, ocultando contexto detalhado, navegação secundária e tabelas auxiliares.",
    )


def filter_dataframe(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    geography_col = "customer_state" if filters.geography_mode == "Cliente" else "seller_state"
    end_exclusive = filters.end_date + pd.Timedelta(days=1)
    mask = (
        (df["order_purchase_timestamp"] >= filters.start_date)
        & (df["order_purchase_timestamp"] < end_exclusive)
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
