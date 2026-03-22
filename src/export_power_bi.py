from __future__ import annotations

import logging
from pathlib import Path
import sys

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR
from src.ingest import configure_logging
from src.publish_dashboard import pseudonymize
from src.utils import ensure_directory


LOGGER = logging.getLogger(__name__)
FACT_SOURCE_PATH = DATA_DIR / "curated" / "analytics" / "fact_orders_enriched.parquet"
BI_EXPORT_DIR = DATA_DIR / "processed" / "bi_exports"


def load_fact() -> pd.DataFrame:
    if not FACT_SOURCE_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {FACT_SOURCE_PATH}")

    df = pd.read_parquet(FACT_SOURCE_PATH)
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "latest_review_creation_date",
        "latest_review_answer_timestamp",
    ]
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["category_label"] = df["product_category_name_english"].fillna(df["product_category_name"]).fillna("unknown")
    return df


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    dim_date = pd.DataFrame({"order_date": pd.to_datetime(df["order_date"]).dropna().drop_duplicates().sort_values()})
    dim_date["date_key"] = dim_date["order_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["order_date"].dt.year
    dim_date["quarter"] = "Q" + dim_date["order_date"].dt.quarter.astype(str)
    dim_date["month"] = dim_date["order_date"].dt.month
    dim_date["month_name"] = dim_date["order_date"].dt.strftime("%b")
    dim_date["year_month"] = dim_date["order_date"].dt.strftime("%Y-%m")
    dim_date["week_of_year"] = dim_date["order_date"].dt.isocalendar().week.astype(int)
    dim_date["day"] = dim_date["order_date"].dt.day
    dim_date["weekday_name"] = dim_date["order_date"].dt.strftime("%A")
    return dim_date[
        ["date_key", "order_date", "year", "quarter", "month", "month_name", "year_month", "week_of_year", "day", "weekday_name"]
    ]


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["product_key"] = dim["product_id"].map(lambda value: pseudonymize(value, "product_id"))
    columns = [
        "product_key",
        "product_category_name",
        "product_category_name_english",
        "category_label",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    return dim[columns].drop_duplicates(subset=["product_key"]).sort_values("product_key").reset_index(drop=True)


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["customer_key"] = dim["customer_id"].map(lambda value: pseudonymize(value, "customer_id"))
    dim["customer_master_key"] = dim["customer_unique_id"].map(lambda value: pseudonymize(value, "customer_unique_id"))
    columns = ["customer_key", "customer_master_key", "customer_state"]
    return dim[columns].drop_duplicates(subset=["customer_key"]).sort_values("customer_key").reset_index(drop=True)


def build_dim_seller(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["seller_key"] = dim["seller_id"].map(lambda value: pseudonymize(value, "seller_id"))
    columns = ["seller_key", "seller_state"]
    return dim[columns].drop_duplicates(subset=["seller_key"]).sort_values("seller_key").reset_index(drop=True)


def build_dim_payment(df: pd.DataFrame) -> pd.DataFrame:
    dim_payment = pd.DataFrame({"payment_type_mode": sorted(df["payment_type_mode"].fillna("unknown").drop_duplicates())})
    dim_payment["payment_group"] = dim_payment["payment_type_mode"].replace(
        {"credit_card": "Card", "debit_card": "Card", "voucher": "Voucher", "boleto": "Boleto"}
    )
    dim_payment.loc[~dim_payment["payment_group"].isin(["Card", "Voucher", "Boleto"]), "payment_group"] = "Other"
    return dim_payment


def build_dim_order_status(df: pd.DataFrame) -> pd.DataFrame:
    dim_status = pd.DataFrame({"order_status": sorted(df["order_status"].fillna("unknown").drop_duplicates())})
    dim_status["status_group"] = dim_status["order_status"].replace(
        {
            "delivered": "Closed",
            "shipped": "In Fulfillment",
            "invoiced": "In Fulfillment",
            "processing": "In Fulfillment",
            "approved": "In Fulfillment",
            "created": "Open",
            "unavailable": "Exception",
            "canceled": "Exception",
        }
    )
    dim_status.loc[~dim_status["status_group"].isin(["Closed", "In Fulfillment", "Open", "Exception"]), "status_group"] = "Other"
    return dim_status


def build_fact_sales(df: pd.DataFrame) -> pd.DataFrame:
    fact = df.copy()
    fact["order_key"] = fact["order_id"].map(lambda value: pseudonymize(value, "order_id"))
    fact["customer_key"] = fact["customer_id"].map(lambda value: pseudonymize(value, "customer_id"))
    fact["product_key"] = fact["product_id"].map(lambda value: pseudonymize(value, "product_id"))
    fact["seller_key"] = fact["seller_id"].map(lambda value: pseudonymize(value, "seller_id"))
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d")
    fact.loc[fact["order_date"].isna(), "date_key"] = pd.NA
    fact["date_key"] = fact["date_key"].astype("Int64")
    fact["order_item_key"] = (
        fact["order_key"].astype(str)
        + "_"
        + fact["order_item_id"].astype(str)
        + "_"
        + fact["product_key"].astype(str)
        + "_"
        + fact["seller_key"].astype(str)
    )
    fact["review_available"] = fact["review_score_mean"].notna().astype(int)
    fact["delivered_flag"] = fact["order_delivered_customer_date"].notna().astype(int)

    columns = [
        "order_item_key",
        "order_key",
        "order_item_id",
        "date_key",
        "customer_key",
        "product_key",
        "seller_key",
        "payment_type_mode",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "price",
        "freight_value",
        "total_item_value",
        "payment_count",
        "total_payment_value",
        "max_payment_installments",
        "review_count",
        "review_score_mean",
        "review_available",
        "delivery_time_days",
        "estimated_delay_days",
        "is_delayed",
        "delivered_flag",
    ]
    return fact[columns].copy()


def export_csv(df: pd.DataFrame, file_name: str) -> None:
    ensure_directory(BI_EXPORT_DIR)
    output_path = BI_EXPORT_DIR / file_name
    df.to_csv(output_path, index=False)
    LOGGER.info("Arquivo BI exportado: %s | shape=(%s, %s)", output_path.name, df.shape[0], df.shape[1])


def run_export() -> None:
    df = load_fact()

    export_csv(build_fact_sales(df), "fact_sales_power_bi.csv")
    export_csv(build_dim_date(df), "dim_date.csv")
    export_csv(build_dim_product(df), "dim_product.csv")
    export_csv(build_dim_customer(df), "dim_customer.csv")
    export_csv(build_dim_seller(df), "dim_seller.csv")
    export_csv(build_dim_payment(df), "dim_payment.csv")
    export_csv(build_dim_order_status(df), "dim_order_status.csv")


if __name__ == "__main__":
    configure_logging()
    run_export()
