from __future__ import annotations

import hashlib
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ANALYTICS_DIR, DOCS_DIR, PUBLISHED_DASHBOARD_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
SOURCE_FACT_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
PUBLISHED_PARQUET_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
PUBLISHED_CSV_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.csv"
REPORT_PATH = DOCS_DIR / "privacy_governance.md"

PSEUDONYMIZED_COLUMNS = {
    "order_id": "order_id",
    "customer_unique_id": "customer_unique_id",
}

PUBLISHED_COLUMNS = [
    "order_id",
    "order_item_id",
    "customer_unique_id",
    "order_status",
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "order_date",
    "order_year",
    "order_month",
    "purchase_cohort_month",
    "cohort_order_month_number",
    "customer_order_sequence",
    "is_first_order",
    "seller_key",
    "seller_volume_tier",
    "seller_order_count",
    "seller_avg_delivery_days",
    "seller_delay_rate",
    "delivery_time_days",
    "seller_dispatch_time_days",
    "carrier_delivery_time_days",
    "estimated_delay_days",
    "is_delayed",
    "price",
    "freight_value",
    "freight_to_price_ratio",
    "total_item_value",
    "payment_type_mode",
    "review_score_mean",
    "product_category_name",
    "product_category_name_english",
    "customer_state",
    "seller_state",
]

REMOVED_SENSITIVE_COLUMNS = [
    "customer_id",
    "product_id",
    "seller_id",
    "customer_zip_code_prefix",
    "customer_city",
    "seller_zip_code_prefix",
    "seller_city",
    "latest_review_creation_date",
    "latest_review_answer_timestamp",
    "shipping_limit_date",
    "order_delivered_carrier_date",
    "order_approved_at",
    "payment_count",
    "total_payment_value",
    "max_payment_installments",
    "review_count",
    "review_score_max",
    "review_score_min",
    "has_review_comment",
]


@dataclass(frozen=True)
class PublishedArtifacts:
    parquet_path: Path
    csv_path: Path
    rows: int
    columns: int


def to_project_relative_path(path: Path) -> str:
    project_root = Path(__file__).resolve().parent.parent
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def pseudonymize(value: object, prefix: str) -> str | pd.NA:
    if pd.isna(value):
        return pd.NA
    digest = hashlib.sha256(f"{prefix}:{value}".encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def load_internal_fact() -> pd.DataFrame:
    if not SOURCE_FACT_PATH.exists():
        raise FileNotFoundError(f"Tabela analítica interna não encontrada: {SOURCE_FACT_PATH}")
    df = pd.read_parquet(SOURCE_FACT_PATH)
    LOGGER.info("Tabela interna carregada para publicação segura | shape=(%s, %s)", *df.shape)
    return df


def build_published_dashboard_table(df: pd.DataFrame) -> pd.DataFrame:
    published = df.copy()

    for source_column, prefix in PSEUDONYMIZED_COLUMNS.items():
        published[source_column] = published[source_column].map(lambda value: pseudonymize(value, prefix))
    if "seller_id" in published.columns:
        published["seller_key"] = published["seller_id"].map(lambda value: pseudonymize(value, "seller_id"))

    existing_columns = [column for column in PUBLISHED_COLUMNS if column in published.columns]
    published = published[existing_columns].copy()

    published["customer_state"] = published["customer_state"].fillna("NA")
    published["seller_state"] = published["seller_state"].fillna("NA")
    published["order_status"] = published["order_status"].fillna("unknown")
    published["payment_type_mode"] = published["payment_type_mode"].fillna("unknown")
    if "seller_volume_tier" in published.columns:
        published["seller_volume_tier"] = published["seller_volume_tier"].fillna("long_tail")

    return published


def save_outputs(df: pd.DataFrame) -> PublishedArtifacts:
    ensure_directory(PUBLISHED_DASHBOARD_DIR)
    df.to_parquet(PUBLISHED_PARQUET_PATH, index=False)
    df.to_csv(PUBLISHED_CSV_PATH, index=False)
    LOGGER.info("Camada publicada do dashboard salva em %s e %s", PUBLISHED_PARQUET_PATH, PUBLISHED_CSV_PATH)
    return PublishedArtifacts(
        parquet_path=PUBLISHED_PARQUET_PATH,
        csv_path=PUBLISHED_CSV_PATH,
        rows=len(df),
        columns=df.shape[1],
    )


def render_report(artifacts: PublishedArtifacts) -> str:
    lines = [
        "# Privacidade, LGPD e Governança",
        "",
        "Este documento registra as decisões de privacidade por design e governança aplicadas ao projeto.",
        "",
        "## Camadas de Exposição",
        "",
        "- `data/raw/landing/`: dados brutos recebidos sem transformação.",
        "- `data/standardized/`: dados padronizados para reuso técnico.",
        "- `data/curated/analytics/`: tabela analítica interna com granularidade por item, usada para processamento, SQL e qualidade.",
        "- `data/published/dashboard/`: camada publicada e minimizada para consumo do Streamlit.",
        "",
        "## Medidas Aplicadas na Camada Publicada",
        "",
        "- pseudonimização não reversível de `order_id` e `customer_unique_id` antes do consumo pelo dashboard.",
        "- pseudonimização não reversível de `seller_id` em `seller_key` para permitir recortes por seller sem expor o identificador bruto.",
        "- remoção de identificadores desnecessários para apresentação, como `customer_id`, `seller_id` e `product_id`.",
        "- remoção de quase-identificadores mais sensíveis na camada publicada, como cidade e prefixo de CEP.",
        "- manutenção apenas de atributos necessários para responder às perguntas do projeto: tempo, categoria, UF, pagamento, valor, atraso, seller, logística e cohort.",
        "- preservação da camada analítica interna para engenharia e auditoria, separada da camada publicada.",
        "",
        "## Colunas Removidas da Camada Publicada",
        "",
        "| Coluna removida | Motivo principal |",
        "| --- | --- |",
    ]
    for column in REMOVED_SENSITIVE_COLUMNS:
        lines.append(f"| `{column}` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |")

    lines.extend(
        [
            "",
            "## Resultado da Publicação Segura",
            "",
            f"- Arquivo publicado para o app: `{to_project_relative_path(PUBLISHED_PARQUET_PATH)}`",
            f"- Arquivo publicado para upload manual: `{to_project_relative_path(PUBLISHED_CSV_PATH)}`",
            f"- Registros publicados: **{artifacts.rows:,}**",
            f"- Colunas publicadas: **{artifacts.columns}**",
            "",
            "## Política de Uso",
            "",
            "- o dashboard deve consumir exclusivamente a camada `published/dashboard`.",
            "- a camada `curated/analytics` permanece interna ao pipeline e não deve ser tratada como camada de exposição.",
            "- tabelas detalhadas do app devem exibir apenas chaves pseudonimizadas e dimensões agregadas necessárias ao projeto.",
            "- uploads manuais em plataforma devem usar preferencialmente o CSV da camada publicada.",
            "",
            "## Limitações e Escopo",
            "",
            "- o dataset Olist é público e anonimizado, mas o projeto adota privacidade por design para refletir prática corporativa.",
            "- esta camada não substitui controles organizacionais de acesso, mas reduz exposição desnecessária no produto analítico publicado.",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(artifacts: PublishedArtifacts) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(artifacts), encoding="utf-8")
    LOGGER.info("Documentação de privacidade salva em %s", REPORT_PATH)
    return REPORT_PATH


def run_publish_dashboard() -> PublishedArtifacts:
    internal_df = load_internal_fact()
    published_df = build_published_dashboard_table(internal_df)
    artifacts = save_outputs(published_df)
    save_report(artifacts)
    return artifacts


if __name__ == "__main__":
    configure_logging()
    run_publish_dashboard()
