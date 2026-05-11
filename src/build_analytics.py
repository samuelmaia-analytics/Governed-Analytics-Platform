from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ANALYTICS_DIR, DOCS_DIR, LANDING_DIR, STANDARDIZED_DIR
from src.ingest import configure_logging, load_csv
from src.quality import validate_not_empty
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
OLIST_LANDING_DIR = LANDING_DIR / "olist"
STANDARDIZED_OLIST_DIR = STANDARDIZED_DIR / "olist"
FACT_PARQUET_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
FACT_CSV_PATH = ANALYTICS_DIR / "fact_orders_enriched.csv"
REPORT_PATH = DOCS_DIR / "fact_orders_enriched.md"


@dataclass
class BuildArtifacts:
    fact_table: pd.DataFrame
    parquet_path: Path
    csv_path: Path
    report_path: Path


def to_snake_case(value: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", value.strip())
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").lower()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={column: to_snake_case(column) for column in df.columns})


def read_olist_table(file_name: str) -> pd.DataFrame:
    standardized_path = STANDARDIZED_OLIST_DIR / f"{Path(file_name).stem}.parquet"
    if standardized_path.exists():
        df = pd.read_parquet(standardized_path)
        LOGGER.info(
            "Tabela carregada da camada standardized: %s | shape=(%s, %s)",
            standardized_path.name,
            *df.shape,
        )
        return standardize_columns(df)

    landing_path = OLIST_LANDING_DIR / file_name
    if not landing_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado em standardized nem landing: {standardized_path} | {landing_path}"
        )

    df, _, _ = load_csv(landing_path)
    df = standardize_columns(df)
    LOGGER.warning(
        "Leitura realizada direto da landing para %s. Execute `python src/preprocess.py` para promover a camada standardized.",
        file_name,
    )
    LOGGER.info("Tabela carregada: %s | shape=(%s, %s)", file_name, *df.shape)
    return df


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    converted = df.copy()
    for column in converted.columns:
        if "date" in column or "timestamp" in column or column.endswith("_at"):
            converted[column] = pd.to_datetime(converted[column], errors="coerce")
    return converted


def deduplicate(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset, keep="first").copy()


def build_payments_agg(payments: pd.DataFrame) -> pd.DataFrame:
    payments = deduplicate(payments)
    aggregated = (
        payments.groupby("order_id", dropna=False)
        .agg(
            payment_count=("payment_sequential", "count"),
            total_payment_value=("payment_value", "sum"),
            max_payment_installments=("payment_installments", "max"),
            payment_type_mode=(
                "payment_type",
                lambda series: (
                    series.mode().iloc[0] if not series.mode().empty else pd.NA
                ),
            ),
        )
        .reset_index()
    )
    return aggregated


def build_reviews_agg(reviews: pd.DataFrame) -> pd.DataFrame:
    reviews = deduplicate(reviews)
    aggregated = (
        reviews.groupby("order_id", dropna=False)
        .agg(
            review_count=("review_id", "count"),
            review_score_mean=("review_score", "mean"),
            review_score_max=("review_score", "max"),
            review_score_min=("review_score", "min"),
            latest_review_creation_date=("review_creation_date", "max"),
            latest_review_answer_timestamp=("review_answer_timestamp", "max"),
            has_review_comment=(
                "review_comment_message",
                lambda s: int(s.fillna("").str.strip().ne("").any()),
            ),
        )
        .reset_index()
    )
    return aggregated


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = convert_datetime_columns(deduplicate(orders, subset=["order_id"]))
    return orders[orders["order_id"].notna() & orders["customer_id"].notna()].copy()


def clean_order_items(order_items: pd.DataFrame) -> pd.DataFrame:
    order_items = convert_datetime_columns(deduplicate(order_items))
    order_items = order_items[
        order_items["order_id"].notna()
        & order_items["order_item_id"].notna()
        & order_items["product_id"].notna()
        & order_items["seller_id"].notna()
    ].copy()
    order_items = order_items[
        (order_items["price"].fillna(0) >= 0)
        & (order_items["freight_value"].fillna(0) >= 0)
    ].copy()
    return order_items


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    customers = deduplicate(customers, subset=["customer_id"])
    return customers[customers["customer_id"].notna()].copy()


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    products = deduplicate(products, subset=["product_id"])
    return products[products["product_id"].notna()].copy()


def clean_sellers(sellers: pd.DataFrame) -> pd.DataFrame:
    sellers = deduplicate(sellers, subset=["seller_id"])
    return sellers[sellers["seller_id"].notna()].copy()


def clean_translation(translation: pd.DataFrame) -> pd.DataFrame:
    translation = deduplicate(translation, subset=["product_category_name"])
    return translation[translation["product_category_name"].notna()].copy()


def derive_columns(fact_table: pd.DataFrame) -> pd.DataFrame:
    enriched = fact_table.copy()

    enriched["order_date"] = enriched["order_purchase_timestamp"].dt.date
    enriched["order_year"] = enriched["order_purchase_timestamp"].dt.year
    enriched["order_month"] = enriched["order_purchase_timestamp"].dt.month
    enriched["purchase_cohort_month"] = (
        enriched["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )
    enriched["delivery_time_days"] = (
        enriched["order_delivered_customer_date"] - enriched["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    enriched["estimated_delay_days"] = (
        enriched["order_delivered_customer_date"]
        - enriched["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    enriched["is_delayed"] = (
        enriched["order_delivered_customer_date"].notna()
        & enriched["order_estimated_delivery_date"].notna()
        & (
            enriched["order_delivered_customer_date"]
            > enriched["order_estimated_delivery_date"]
        )
    )
    enriched["total_item_value"] = enriched["price"].fillna(0) + enriched[
        "freight_value"
    ].fillna(0)
    enriched["freight_to_price_ratio"] = (
        enriched["freight_value"]
        .where(enriched["price"].fillna(0) > 0)
        .div(enriched["price"].where(enriched["price"].fillna(0) > 0))
    )
    enriched["seller_dispatch_time_days"] = (
        enriched["order_delivered_carrier_date"] - enriched["order_approved_at"]
    ).dt.total_seconds() / 86400
    enriched["carrier_delivery_time_days"] = (
        enriched["order_delivered_customer_date"]
        - enriched["order_delivered_carrier_date"]
    ).dt.total_seconds() / 86400

    first_purchase_ts = enriched.groupby("customer_unique_id")[
        "order_purchase_timestamp"
    ].transform("min")
    enriched["customer_first_purchase_timestamp"] = first_purchase_ts
    enriched["cohort_order_month_number"] = (
        enriched["order_purchase_timestamp"].dt.year - first_purchase_ts.dt.year
    ) * 12 + (
        enriched["order_purchase_timestamp"].dt.month - first_purchase_ts.dt.month
    )
    order_rank = (
        enriched.groupby(["customer_unique_id", "order_id"], dropna=False)[
            "order_purchase_timestamp"
        ]
        .transform("min")
        .groupby(enriched["customer_unique_id"], dropna=False)
        .rank(method="dense")
    )
    enriched["customer_order_sequence"] = order_rank.astype("Int64")
    enriched["is_first_order"] = enriched["customer_order_sequence"] == 1

    seller_order_count = enriched.groupby("seller_id")["order_id"].transform("nunique")
    enriched["seller_order_count"] = seller_order_count.astype("Int64")
    enriched["seller_avg_delivery_days"] = enriched.groupby("seller_id")[
        "delivery_time_days"
    ].transform("mean")
    enriched["seller_delay_rate"] = enriched.groupby("seller_id")[
        "is_delayed"
    ].transform("mean")
    enriched["seller_volume_tier"] = pd.cut(
        seller_order_count,
        bins=[-1, 25, 100, 500, float("inf")],
        labels=["long_tail", "scaled", "core", "strategic"],
    ).astype("string")

    return enriched


def remove_obvious_inconsistencies(fact_table: pd.DataFrame) -> pd.DataFrame:
    cleaned = fact_table.copy()
    cleaned = cleaned[cleaned["order_purchase_timestamp"].notna()].copy()
    cleaned = cleaned[cleaned["price"].fillna(0) >= 0].copy()
    cleaned = cleaned[cleaned["freight_value"].fillna(0) >= 0].copy()
    cleaned = cleaned[
        cleaned["delivery_time_days"].isna() | (cleaned["delivery_time_days"] >= 0)
    ].copy()
    cleaned = deduplicate(
        cleaned, subset=["order_id", "order_item_id", "product_id", "seller_id"]
    )
    return cleaned


def build_join_health_summary(fact_table: pd.DataFrame) -> dict[str, float]:
    metrics = {}
    for column in [
        "customer_unique_id",
        "customer_state",
        "seller_state",
        "payment_type_mode",
        "product_category_name",
        "product_category_name_english",
    ]:
        if column in fact_table.columns:
            metrics[column] = round(float(fact_table[column].isna().mean() * 100), 2)
    return metrics


def build_payment_reconciliation_summary(fact_table: pd.DataFrame) -> dict[str, float]:
    order_reconciliation = (
        fact_table.groupby("order_id", as_index=False)
        .agg(
            order_items_total=("total_item_value", "sum"),
            order_payment_total=("total_payment_value", "max"),
        )
        .assign(
            order_payment_total=lambda df_: df_["order_payment_total"].fillna(0),
            abs_gap=lambda df_: (
                df_["order_items_total"] - df_["order_payment_total"]
            ).abs(),
        )
    )
    order_reconciliation["gap_gt_1_real"] = order_reconciliation["abs_gap"] > 1.0
    return {
        "orders_reconciled": int(len(order_reconciliation)),
        "avg_abs_gap": round(float(order_reconciliation["abs_gap"].mean()), 4),
        "max_abs_gap": round(float(order_reconciliation["abs_gap"].max()), 4),
        "orders_gap_gt_1_real_pct": round(
            float(order_reconciliation["gap_gt_1_real"].mean() * 100), 2
        ),
    }


def select_output_columns(fact_table: pd.DataFrame) -> pd.DataFrame:
    preferred_order = [
        "order_id",
        "order_item_id",
        "customer_id",
        "customer_unique_id",
        "product_id",
        "seller_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "shipping_limit_date",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "order_date",
        "order_year",
        "order_month",
        "purchase_cohort_month",
        "customer_first_purchase_timestamp",
        "cohort_order_month_number",
        "customer_order_sequence",
        "is_first_order",
        "delivery_time_days",
        "seller_dispatch_time_days",
        "carrier_delivery_time_days",
        "estimated_delay_days",
        "is_delayed",
        "price",
        "freight_value",
        "freight_to_price_ratio",
        "total_item_value",
        "payment_count",
        "total_payment_value",
        "max_payment_installments",
        "payment_type_mode",
        "review_count",
        "review_score_mean",
        "review_score_max",
        "review_score_min",
        "has_review_comment",
        "product_category_name",
        "product_category_name_english",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
        "seller_order_count",
        "seller_avg_delivery_days",
        "seller_delay_rate",
        "seller_volume_tier",
        "latest_review_creation_date",
        "latest_review_answer_timestamp",
    ]
    existing = [column for column in preferred_order if column in fact_table.columns]
    remaining = [column for column in fact_table.columns if column not in existing]
    return fact_table[existing + remaining].copy()


def build_fact_orders_enriched() -> pd.DataFrame:
    orders = clean_orders(read_olist_table("olist_orders_dataset.csv"))
    order_items = clean_order_items(read_olist_table("olist_order_items_dataset.csv"))
    customers = clean_customers(read_olist_table("olist_customers_dataset.csv"))
    products = clean_products(read_olist_table("olist_products_dataset.csv"))
    sellers = clean_sellers(read_olist_table("olist_sellers_dataset.csv"))
    payments = build_payments_agg(
        convert_datetime_columns(read_olist_table("olist_order_payments_dataset.csv"))
    )
    reviews = build_reviews_agg(
        convert_datetime_columns(read_olist_table("olist_order_reviews_dataset.csv"))
    )
    translation = clean_translation(
        read_olist_table("product_category_name_translation.csv")
    )

    fact_table = order_items.merge(
        orders, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        customers, on="customer_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        products, on="product_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        sellers, on="seller_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        payments, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        reviews, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        translation,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )

    fact_table = derive_columns(fact_table)
    fact_table = remove_obvious_inconsistencies(fact_table)
    fact_table = select_output_columns(fact_table)

    validate_not_empty(fact_table, "fact_orders_enriched")
    if len(fact_table) <= 100_000:
        raise ValueError(
            f"fact_orders_enriched precisa ter mais de 100.000 registros, mas possui {len(fact_table)}."
        )

    LOGGER.info("Tabela analítica final pronta | shape=(%s, %s)", *fact_table.shape)
    return fact_table


def save_outputs(fact_table: pd.DataFrame) -> tuple[Path, Path]:
    ensure_directory(ANALYTICS_DIR)
    fact_table.to_parquet(FACT_PARQUET_PATH, index=False)
    fact_table.to_csv(FACT_CSV_PATH, index=False)
    LOGGER.info("Saidas salvas em %s e %s", FACT_PARQUET_PATH, FACT_CSV_PATH)
    return FACT_PARQUET_PATH, FACT_CSV_PATH


def render_report(fact_table: pd.DataFrame) -> str:
    join_health = build_join_health_summary(fact_table)
    reconciliation = build_payment_reconciliation_summary(fact_table)
    lines = [
        "# fact_orders_enriched",
        "",
        "Tabela analítica principal derivada do dataset Olist com granularidade por item de pedido.",
        "",
        "## Resumo",
        "",
        f"- Total de registros: **{len(fact_table):,}**",
        f"- Total de colunas: **{fact_table.shape[1]}**",
        "",
        "## Regras de Negócio",
        "",
        "- A tabela base parte de `order_items`, preservando uma linha por item de pedido.",
        "- `orders`, `customers`, `products`, `sellers` e `translation` entram por joins dimensionais `many_to_one`.",
        "- `payments` e `reviews` são agregados por `order_id` antes do join para evitar duplicação artificial de itens.",
        "- `total_item_value` é calculado como `price + freight_value` no nível do item.",
        "- `delivery_time_days` mede o tempo entre compra e entrega ao cliente.",
        "- `seller_dispatch_time_days` mede o tempo entre aprovacao e despacho para a transportadora.",
        "- `carrier_delivery_time_days` mede o trecho transportadora -> cliente quando a origem traz os timestamps.",
        "- `estimated_delay_days` mede a diferença entre a entrega real e a data estimada; permanece nulo quando não há entrega registrada.",
        "- `is_delayed` sinaliza pedidos entregues após a data estimada.",
        "- `purchase_cohort_month`, `customer_order_sequence` e `cohort_order_month_number` habilitam analise de cohort e recorrencia.",
        "- `seller_order_count`, `seller_avg_delivery_days`, `seller_delay_rate` e `seller_volume_tier` habilitam recortes semanticos de seller.",
        "- `freight_to_price_ratio` qualifica o peso relativo do frete sobre o item vendido.",
        "- Registros com chaves essenciais ausentes, valores monetários negativos ou entrega anterior à compra são removidos.",
        "",
        "## Cobertura de Enriquecimento",
        "",
        "| Atributo | Percentual ausente |",
        "| --- | ---: |",
    ]
    for column, missing_pct in join_health.items():
        lines.append(f"| `{column}` | {missing_pct:.2f}% |")

    lines.extend(
        [
            "",
            "## Reconciliação Financeira em Nível de Pedido",
            "",
            f"- Pedidos reconciliados: **{reconciliation['orders_reconciled']:,}**",
            f"- Gap absoluto médio entre `sum(total_item_value)` e `total_payment_value`: **{reconciliation['avg_abs_gap']:.4f}**",
            f"- Gap absoluto máximo observado: **{reconciliation['max_abs_gap']:.4f}**",
            f"- Percentual de pedidos com gap acima de R$ 1,00: **{reconciliation['orders_gap_gt_1_real_pct']:.2f}%**",
            "",
            "## Decisão de Granularidade",
            "",
            "- A granularidade escolhida é `order_id + order_item_id + product_id + seller_id`.",
            "- Essa decisão preserva a análise por item vendido, seller e produto, sem perder contexto de pedido, cliente, pagamento e review.",
            "",
            "## Principais Limitações",
            "",
            "- `payments` e `reviews` são resumidos ao nível do pedido, portanto distribuições internas por item não existem na fonte final.",
            "- Algumas colunas de data do dataset original possuem ausências; nesses casos, as métricas derivadas podem ficar nulas ou simplificadas.",
            "- A regra de inconsistência é propositalmente conservadora e remove apenas anomalias óbvias.",
            "- O campo `order_approved_at` pode permanecer nulo ou texto convertido para `NaT` quando a origem estiver incompleta.",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(fact_table: pd.DataFrame) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(fact_table), encoding="utf-8")
    LOGGER.info("Relatório salvo em %s", REPORT_PATH)
    return REPORT_PATH


def run_build() -> BuildArtifacts:
    fact_table = build_fact_orders_enriched()
    parquet_path, csv_path = save_outputs(fact_table)
    report_path = save_report(fact_table)
    return BuildArtifacts(
        fact_table=fact_table,
        parquet_path=parquet_path,
        csv_path=csv_path,
        report_path=report_path,
    )


if __name__ == "__main__":
    configure_logging()
    run_build()
