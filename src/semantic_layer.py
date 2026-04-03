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
REPORT_PATH = DOCS_DIR / "semantic_layer.md"


@dataclass(frozen=True)
class SemanticArtifacts:
    logistics_path: Path
    seller_path: Path
    cohort_path: Path
    category_path: Path
    state_path: Path


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


def save_dataset(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)
    df.to_csv(path.with_suffix(".csv"), index=False)


def render_report(
    logistics: pd.DataFrame,
    seller: pd.DataFrame,
    cohort: pd.DataFrame,
    category: pd.DataFrame,
    state: pd.DataFrame,
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
        "",
        "## Recortes Disponiveis",
        "",
        "- Logistica: tempo medio de entrega, despacho, transporte e peso relativo do frete por UF origem/destino e mes.",
        "- Seller: tier de volume, atraso medio, entrega media, ticket medio e satisfacao por seller pseudonimizado.",
        "- Cohort: comportamento por cohort de compra e maturacao mensal da base de clientes.",
        "- Categoria: receita, ticket, atraso, review e meio de pagamento por categoria e mes.",
        "- Geografia executiva: receita, sellers ativos, atraso e satisfacao por UF e mes.",
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
    save_dataset(logistics, LOGISTICS_PATH)
    save_dataset(seller, SELLER_PATH)
    save_dataset(cohort, COHORT_PATH)
    save_dataset(category, CATEGORY_PATH)
    save_dataset(state, STATE_PATH)
    REPORT_PATH.write_text(render_report(logistics, seller, cohort, category, state), encoding="utf-8")
    LOGGER.info("Camada semantica expandida materializada em %s", PUBLISHED_SEMANTIC_DIR)
    return SemanticArtifacts(
        logistics_path=LOGISTICS_PATH,
        seller_path=SELLER_PATH,
        cohort_path=COHORT_PATH,
        category_path=CATEGORY_PATH,
        state_path=STATE_PATH,
    )


if __name__ == "__main__":
    configure_logging()
    run_semantic_layer()
