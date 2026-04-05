from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, PUBLISHED_DASHBOARD_DIR, PUBLISHED_SEMANTIC_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
PUBLISHED_SOURCE_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
LOGISTICS_PATH = PUBLISHED_SEMANTIC_DIR / "logistics_slice.parquet"
SELLER_PATH = PUBLISHED_SEMANTIC_DIR / "seller_slice.parquet"
COHORT_PATH = PUBLISHED_SEMANTIC_DIR / "cohort_slice.parquet"
CATEGORY_PATH = PUBLISHED_SEMANTIC_DIR / "category_slice.parquet"
STATE_PATH = PUBLISHED_SEMANTIC_DIR / "state_performance_slice.parquet"
EXECUTIVE_KPI_PATH = PUBLISHED_SEMANTIC_DIR / "executive_kpis_slice.parquet"
REPORT_PATH = DOCS_DIR / "semantic_layer.md"


@dataclass(frozen=True)
class SemanticArtifacts:
    logistics_path: Path
    seller_path: Path
    cohort_path: Path
    category_path: Path
    state_path: Path
    executive_kpi_path: Path


def load_published_table() -> pd.DataFrame:
    if not PUBLISHED_SOURCE_PATH.exists():
        raise FileNotFoundError(f"Camada publicada nao encontrada para expansao semantica: {PUBLISHED_SOURCE_PATH}")
    return pd.read_parquet(PUBLISHED_SOURCE_PATH)


def build_logistics_slice(df: pd.DataFrame) -> pd.DataFrame:
    logistics = (
        df.groupby(["order_year", "order_month", "customer_state", "seller_state"], dropna=False)
        .agg(
            total_items=("order_item_id", "count"),
            delayed_rate=("is_delayed", "mean"),
            avg_delivery_time_days=("delivery_time_days", "mean"),
            avg_dispatch_time_days=("seller_dispatch_time_days", "mean"),
            avg_carrier_time_days=("carrier_delivery_time_days", "mean"),
            avg_freight_to_price_ratio=("freight_to_price_ratio", "mean"),
        )
        .reset_index()
    )
    return logistics.sort_values(["order_year", "order_month", "customer_state", "seller_state"]).reset_index(drop=True)


def build_seller_slice(df: pd.DataFrame) -> pd.DataFrame:
    seller = (
        df.groupby(["seller_key", "seller_state", "seller_volume_tier"], dropna=False)
        .agg(
            total_items=("order_item_id", "count"),
            seller_order_count=("seller_order_count", "max"),
            avg_ticket=("total_item_value", "mean"),
            avg_delivery_time_days=("seller_avg_delivery_days", "max"),
            delay_rate=("seller_delay_rate", "max"),
            avg_review_score=("review_score_mean", "mean"),
        )
        .reset_index()
    )
    return seller.sort_values(["seller_volume_tier", "seller_key"]).reset_index(drop=True)


def build_cohort_slice(df: pd.DataFrame) -> pd.DataFrame:
    cohort = (
        df.groupby(["purchase_cohort_month", "cohort_order_month_number"], dropna=False)
        .agg(
            customers=("customer_unique_id", "nunique"),
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            avg_ticket=("total_item_value", "mean"),
            delayed_rate=("is_delayed", "mean"),
        )
        .reset_index()
    )
    return cohort.sort_values(["purchase_cohort_month", "cohort_order_month_number"]).reset_index(drop=True)


def build_category_slice(df: pd.DataFrame) -> pd.DataFrame:
    category = (
        df.groupby(
            ["order_year", "order_month", "product_category_name_english", "payment_type_mode"],
            dropna=False,
        )
        .agg(
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            revenue=("total_item_value", "sum"),
            avg_ticket=("total_item_value", "mean"),
            delayed_rate=("is_delayed", "mean"),
            avg_review_score=("review_score_mean", "mean"),
            avg_freight_to_price_ratio=("freight_to_price_ratio", "mean"),
        )
        .reset_index()
    )
    return category.sort_values(
        ["order_year", "order_month", "product_category_name_english", "payment_type_mode"]
    ).reset_index(drop=True)


def build_state_performance_slice(df: pd.DataFrame) -> pd.DataFrame:
    state = (
        df.groupby(["order_year", "order_month", "customer_state"], dropna=False)
        .agg(
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            active_sellers=("seller_key", "nunique"),
            revenue=("total_item_value", "sum"),
            avg_ticket=("total_item_value", "mean"),
            delayed_rate=("is_delayed", "mean"),
            avg_delivery_time_days=("delivery_time_days", "mean"),
            avg_review_score=("review_score_mean", "mean"),
        )
        .reset_index()
    )
    return state.sort_values(["order_year", "order_month", "customer_state"]).reset_index(drop=True)


def build_executive_kpis_slice(df: pd.DataFrame) -> pd.DataFrame:
    def metric_series(column: str, frame: pd.DataFrame) -> pd.Series:
        if column in frame.columns:
            return pd.to_numeric(frame[column], errors="coerce")
        return pd.Series([0.0] * len(frame), index=frame.index, dtype="float64")

    order_level = df.copy()
    if "order_purchase_timestamp" in order_level.columns:
        order_level = order_level.sort_values("order_purchase_timestamp")
    order_level = order_level.drop_duplicates(subset=["order_id"], keep="last").copy()
    if "order_delivered_customer_date" in order_level.columns:
        delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()
    else:
        delivered = order_level.copy()
    total_item_value = metric_series("total_item_value", df)
    delivery_time_days = metric_series("delivery_time_days", delivered)
    review_score_mean = metric_series("review_score_mean", order_level)
    freight_value = metric_series("freight_value", df)
    kpis = pd.DataFrame(
        [
            {
                "metric_id": "revenue_gross",
                "metric_label": "Receita Total",
                "metric_group": "commercial",
                "metric_value": float(total_item_value.sum()),
                "metric_unit": "currency",
            },
            {
                "metric_id": "orders",
                "metric_label": "Total de Pedidos",
                "metric_group": "commercial",
                "metric_value": float(order_level["order_id"].nunique()),
                "metric_unit": "count",
            },
            {
                "metric_id": "customers",
                "metric_label": "Total de Clientes",
                "metric_group": "commercial",
                "metric_value": float(order_level["customer_unique_id"].nunique()),
                "metric_unit": "count",
            },
            {
                "metric_id": "avg_ticket",
                "metric_label": "Ticket Médio",
                "metric_group": "commercial",
                "metric_value": float(total_item_value.sum()) / float(order_level["order_id"].nunique())
                if order_level["order_id"].nunique()
                else 0.0,
                "metric_unit": "currency",
            },
            {
                "metric_id": "avg_delivery_time_days",
                "metric_label": "Prazo Médio",
                "metric_group": "operations",
                "metric_value": float(delivery_time_days.mean()) if not delivered.empty else 0.0,
                "metric_unit": "days",
            },
            {
                "metric_id": "delay_rate",
                "metric_label": "Taxa de Atraso",
                "metric_group": "operations",
                "metric_value": float(delivered["is_delayed"].mean()) if not delivered.empty else 0.0,
                "metric_unit": "ratio",
            },
            {
                "metric_id": "avg_review_score",
                "metric_label": "Nota Média",
                "metric_group": "experience",
                "metric_value": float(review_score_mean.mean()) if not order_level.empty else 0.0,
                "metric_unit": "score",
            },
            {
                "metric_id": "avg_freight_per_item",
                "metric_label": "Frete Médio por Item",
                "metric_group": "operations",
                "metric_value": float(freight_value.mean()) if not df.empty else 0.0,
                "metric_unit": "currency",
            },
        ]
    )
    return kpis.sort_values(["metric_group", "metric_id"]).reset_index(drop=True)


def save_dataset(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)
    df.to_csv(path.with_suffix(".csv"), index=False)


def render_report(
    logistics: pd.DataFrame,
    seller: pd.DataFrame,
    cohort: pd.DataFrame,
    category: pd.DataFrame,
    state: pd.DataFrame,
    executive_kpis: pd.DataFrame,
) -> str:
    lines = [
        "# Camada Semantica Expandida",
        "",
        "A camada published passa a expor marts operacionais e executivos para recortes de logistica, seller, cohort, categoria e geografia.",
        "",
        "## Ativos Gerados",
        "",
        f"- `logistics_slice`: **{len(logistics):,}** linhas",
        f"- `seller_slice`: **{len(seller):,}** linhas",
        f"- `cohort_slice`: **{len(cohort):,}** linhas",
        f"- `category_slice`: **{len(category):,}** linhas",
        f"- `state_performance_slice`: **{len(state):,}** linhas",
        f"- `executive_kpis_slice`: **{len(executive_kpis):,}** linhas",
        "",
        "## Recortes Disponiveis",
        "",
        "- Logistica: tempo medio de entrega, despacho, transporte e peso relativo do frete por UF origem/destino e mes.",
        "- Seller: tier de volume, atraso medio, entrega media, ticket medio e satisfacao por seller pseudonimizado.",
        "- Cohort: comportamento por cohort de compra e maturacao mensal da base de clientes.",
        "- Categoria: receita, ticket, atraso, review e meio de pagamento por categoria e mes.",
        "- Geografia executiva: receita, sellers ativos, atraso e satisfacao por UF e mes.",
        "- KPIs executivos: receita, pedidos, clientes, ticket, prazo, atraso, review e frete medio em um ativo resumido e reutilizavel.",
        "",
    ]
    return "\n".join(lines)


def run_semantic_layer() -> SemanticArtifacts:
    ensure_directory(PUBLISHED_SEMANTIC_DIR)
    ensure_directory(DOCS_DIR)
    published = load_published_table()
    logistics = build_logistics_slice(published)
    seller = build_seller_slice(published)
    cohort = build_cohort_slice(published)
    category = build_category_slice(published)
    state = build_state_performance_slice(published)
    executive_kpis = build_executive_kpis_slice(published)
    save_dataset(logistics, LOGISTICS_PATH)
    save_dataset(seller, SELLER_PATH)
    save_dataset(cohort, COHORT_PATH)
    save_dataset(category, CATEGORY_PATH)
    save_dataset(state, STATE_PATH)
    save_dataset(executive_kpis, EXECUTIVE_KPI_PATH)
    REPORT_PATH.write_text(render_report(logistics, seller, cohort, category, state, executive_kpis), encoding="utf-8")
    LOGGER.info("Camada semantica expandida materializada em %s", PUBLISHED_SEMANTIC_DIR)
    return SemanticArtifacts(
        logistics_path=LOGISTICS_PATH,
        seller_path=SELLER_PATH,
        cohort_path=COHORT_PATH,
        category_path=CATEGORY_PATH,
        state_path=STATE_PATH,
        executive_kpi_path=EXECUTIVE_KPI_PATH,
    )


if __name__ == "__main__":
    configure_logging()
    run_semantic_layer()
