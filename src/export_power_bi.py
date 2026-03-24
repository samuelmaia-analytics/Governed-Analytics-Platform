from __future__ import annotations

import logging
from dataclasses import dataclass
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
CSV_SEPARATOR = ","
CSV_ENCODING = "utf-8"

REQUIRED_SOURCE_COLUMNS = {
    "order_id",
    "order_item_id",
    "order_date",
    "customer_id",
    "customer_unique_id",
    "customer_state",
    "product_id",
    "product_category_name",
    "product_category_name_english",
    "seller_id",
    "seller_state",
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
    "delivery_time_days",
    "estimated_delay_days",
    "is_delayed",
}

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "latest_review_creation_date",
    "latest_review_answer_timestamp",
    "order_date",
]


@dataclass(frozen=True)
class ExportArtifact:
    file_name: str
    path: Path
    rows: int
    columns: int
    primary_key: str


@dataclass(frozen=True)
class ExportBundle:
    fact_sales: pd.DataFrame
    dim_date: pd.DataFrame
    dim_product: pd.DataFrame
    dim_payment: pd.DataFrame
    dim_order_status: pd.DataFrame
    dim_customer: pd.DataFrame
    dim_seller: pd.DataFrame


def load_fact() -> pd.DataFrame:
    if not FACT_SOURCE_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {FACT_SOURCE_PATH}")

    df = pd.read_parquet(FACT_SOURCE_PATH)
    missing = sorted(REQUIRED_SOURCE_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes na camada analitica: {', '.join(missing)}")

    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    df["category_label"] = (
        df["product_category_name_english"]
        .fillna(df["product_category_name"])
        .fillna("unknown")
        .astype(str)
        .str.strip()
    )
    df["payment_type_mode"] = df["payment_type_mode"].fillna("unknown").astype(str).str.strip()
    df["order_status"] = df["order_status"].fillna("unknown").astype(str).str.strip()
    df["customer_state"] = df["customer_state"].fillna("NA").astype(str).str.strip()
    df["seller_state"] = df["seller_state"].fillna("NA").astype(str).str.strip()
    df["is_delayed"] = df["is_delayed"].fillna(False).astype(bool)
    return df


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    order_dates = pd.to_datetime(df["order_date"], errors="coerce").dropna().drop_duplicates().sort_values()
    dim_date = pd.DataFrame({"order_date": order_dates.dt.normalize()})
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
    ].reset_index(drop=True)


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["product_key"] = dim["product_id"].map(lambda value: pseudonymize(value, "product_id"))
    dim_product = dim[
        [
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
    ].drop_duplicates(subset=["product_key"])
    return dim_product.sort_values("product_key").reset_index(drop=True)


def build_dim_payment(df: pd.DataFrame) -> pd.DataFrame:
    dim_payment = pd.DataFrame({"payment_type": sorted(df["payment_type_mode"].drop_duplicates())})
    dim_payment["payment_key"] = pd.RangeIndex(start=1, stop=len(dim_payment) + 1, step=1)
    dim_payment["payment_group"] = dim_payment["payment_type"].replace(
        {"credit_card": "Card", "debit_card": "Card", "voucher": "Voucher", "boleto": "Boleto"}
    )
    dim_payment.loc[~dim_payment["payment_group"].isin(["Card", "Voucher", "Boleto"]), "payment_group"] = "Other"
    dim_payment["payment_description"] = dim_payment["payment_type"].str.replace("_", " ").str.title()
    return dim_payment[["payment_key", "payment_type", "payment_group", "payment_description"]]


def build_dim_order_status(df: pd.DataFrame) -> pd.DataFrame:
    dim_status = pd.DataFrame({"order_status": sorted(df["order_status"].drop_duplicates())})
    dim_status["order_status_key"] = pd.RangeIndex(start=1, stop=len(dim_status) + 1, step=1)
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
    dim_status["status_description"] = dim_status["order_status"].str.replace("_", " ").str.title()
    return dim_status[["order_status_key", "order_status", "status_group", "status_description"]]


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["customer_key"] = dim["customer_id"].map(lambda value: pseudonymize(value, "customer_id"))
    dim["customer_master_key"] = dim["customer_unique_id"].map(lambda value: pseudonymize(value, "customer_unique_id"))
    dim_customer = dim[["customer_key", "customer_master_key", "customer_state"]].drop_duplicates(subset=["customer_key"])
    return dim_customer.sort_values("customer_key").reset_index(drop=True)


def build_dim_seller(df: pd.DataFrame) -> pd.DataFrame:
    dim = df.copy()
    dim["seller_key"] = dim["seller_id"].map(lambda value: pseudonymize(value, "seller_id"))
    dim_seller = dim[["seller_key", "seller_state"]].drop_duplicates(subset=["seller_key"])
    return dim_seller.sort_values("seller_key").reset_index(drop=True)


def build_fact_sales(
    df: pd.DataFrame,
    dim_payment: pd.DataFrame,
    dim_order_status: pd.DataFrame,
) -> pd.DataFrame:
    fact = df.copy()
    fact["order_key"] = fact["order_id"].map(lambda value: pseudonymize(value, "order_id"))
    fact["customer_key"] = fact["customer_id"].map(lambda value: pseudonymize(value, "customer_id"))
    fact["product_key"] = fact["product_id"].map(lambda value: pseudonymize(value, "product_id"))
    fact["seller_key"] = fact["seller_id"].map(lambda value: pseudonymize(value, "seller_id"))
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype("Int64")
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

    payment_map = dim_payment.set_index("payment_type")["payment_key"]
    status_map = dim_order_status.set_index("order_status")["order_status_key"]
    fact["payment_key"] = fact["payment_type_mode"].map(payment_map).astype("Int64")
    fact["order_status_key"] = fact["order_status"].map(status_map).astype("Int64")

    return fact[
        [
            "order_item_key",
            "order_key",
            "order_item_id",
            "date_key",
            "product_key",
            "payment_key",
            "order_status_key",
            "customer_key",
            "seller_key",
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
    ].copy()


def validate_no_generic_headers(df: pd.DataFrame, file_name: str) -> None:
    generic_headers = [column for column in df.columns if column.lower().startswith("column")]
    if generic_headers:
        raise ValueError(f"{file_name} contem cabecalhos genericos invalidos: {', '.join(generic_headers)}")


def validate_unique_primary_key(df: pd.DataFrame, primary_key: str, file_name: str) -> None:
    if df[primary_key].isna().any():
        raise ValueError(f"{file_name} contem nulos na chave primaria {primary_key}")
    if df[primary_key].duplicated().any():
        raise ValueError(f"{file_name} contem duplicidade na chave primaria {primary_key}")


def validate_foreign_keys(fact_df: pd.DataFrame, fk_name: str, dim_df: pd.DataFrame, pk_name: str) -> None:
    invalid_keys = fact_df.loc[~fact_df[fk_name].isin(dim_df[pk_name]), fk_name].dropna().unique()
    if len(invalid_keys) > 0:
        raise ValueError(f"A fato contem chaves invalidas em {fk_name} sem correspondencia em {pk_name}")


def validate_export_bundle(bundle: ExportBundle) -> None:
    artifacts_with_pk = [
        (bundle.fact_sales, "order_item_key", "fact_sales_power_bi.csv"),
        (bundle.dim_date, "date_key", "dim_date.csv"),
        (bundle.dim_product, "product_key", "dim_product.csv"),
        (bundle.dim_payment, "payment_key", "dim_payment.csv"),
        (bundle.dim_order_status, "order_status_key", "dim_order_status.csv"),
        (bundle.dim_customer, "customer_key", "dim_customer.csv"),
        (bundle.dim_seller, "seller_key", "dim_seller.csv"),
    ]

    for df, primary_key, file_name in artifacts_with_pk:
        validate_no_generic_headers(df, file_name)
        validate_unique_primary_key(df, primary_key, file_name)

    required_fact_columns = {
        "date_key",
        "product_key",
        "payment_key",
        "order_status_key",
        "customer_key",
        "seller_key",
    }
    missing_fact_columns = sorted(required_fact_columns.difference(bundle.fact_sales.columns))
    if missing_fact_columns:
        raise ValueError(f"fact_sales_power_bi.csv nao contem as foreign keys esperadas: {', '.join(missing_fact_columns)}")

    validate_foreign_keys(bundle.fact_sales, "date_key", bundle.dim_date, "date_key")
    validate_foreign_keys(bundle.fact_sales, "product_key", bundle.dim_product, "product_key")
    validate_foreign_keys(bundle.fact_sales, "payment_key", bundle.dim_payment, "payment_key")
    validate_foreign_keys(bundle.fact_sales, "order_status_key", bundle.dim_order_status, "order_status_key")
    validate_foreign_keys(bundle.fact_sales, "customer_key", bundle.dim_customer, "customer_key")
    validate_foreign_keys(bundle.fact_sales, "seller_key", bundle.dim_seller, "seller_key")

    if bundle.dim_date["order_date"].isna().any():
        raise ValueError("dim_date.csv contem datas nulas")
    if not bundle.dim_date["order_date"].is_monotonic_increasing:
        raise ValueError("dim_date.csv nao esta ordenada por data")


def export_csv(df: pd.DataFrame, file_name: str) -> ExportArtifact:
    ensure_directory(BI_EXPORT_DIR)
    output_path = BI_EXPORT_DIR / file_name
    df.to_csv(output_path, sep=CSV_SEPARATOR, encoding=CSV_ENCODING, index=False, header=True)
    LOGGER.info("Arquivo BI exportado: %s | shape=(%s, %s)", output_path.name, df.shape[0], df.shape[1])
    return ExportArtifact(
        file_name=file_name,
        path=output_path,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        primary_key="",
    )


def build_export_bundle(df: pd.DataFrame) -> ExportBundle:
    dim_date = build_dim_date(df)
    dim_product = build_dim_product(df)
    dim_payment = build_dim_payment(df)
    dim_order_status = build_dim_order_status(df)
    dim_customer = build_dim_customer(df)
    dim_seller = build_dim_seller(df)
    fact_sales = build_fact_sales(df, dim_payment, dim_order_status)
    return ExportBundle(
        fact_sales=fact_sales,
        dim_date=dim_date,
        dim_product=dim_product,
        dim_payment=dim_payment,
        dim_order_status=dim_order_status,
        dim_customer=dim_customer,
        dim_seller=dim_seller,
    )


def print_manifest(artifacts: list[ExportArtifact]) -> None:
    primary_keys = {
        "dim_date.csv": "date_key",
        "dim_product.csv": "product_key",
        "dim_payment.csv": "payment_key",
        "dim_order_status.csv": "order_status_key",
        "dim_customer.csv": "customer_key",
        "dim_seller.csv": "seller_key",
    }
    foreign_keys = ["date_key", "product_key", "payment_key", "order_status_key", "customer_key", "seller_key"]

    print("")
    print("Manifesto de saida Power BI")
    print("===========================")
    for artifact in artifacts:
        pk_name = primary_keys.get(artifact.file_name, "order_item_key")
        print(f"- {artifact.file_name}")
        print(f"  caminho: {artifact.path}")
        print(f"  linhas x colunas: {artifact.rows} x {artifact.columns}")
        print(f"  chave primaria: {pk_name}")
    print("- fact_sales_power_bi.csv")
    print(f"  foreign keys: {', '.join(foreign_keys)}")
    print("  status: sucesso")


def run_export() -> list[ExportArtifact]:
    df = load_fact()
    bundle = build_export_bundle(df)
    validate_export_bundle(bundle)

    exports = [
        ("fact_sales_power_bi.csv", bundle.fact_sales),
        ("dim_date.csv", bundle.dim_date),
        ("dim_product.csv", bundle.dim_product),
        ("dim_payment.csv", bundle.dim_payment),
        ("dim_order_status.csv", bundle.dim_order_status),
        ("dim_customer.csv", bundle.dim_customer),
        ("dim_seller.csv", bundle.dim_seller),
    ]
    artifacts = [export_csv(export_df, file_name) for file_name, export_df in exports]
    print_manifest(artifacts)
    return artifacts


if __name__ == "__main__":
    configure_logging()
    run_export()
