from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import CATALOG_DIR, DOCS_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
CLASSIFICATION_PATH = CATALOG_DIR / "data_classification_inventory.csv"
REPORT_PATH = DOCS_DIR / "data_classification.md"


CLASSIFICATION_ROWS = [
    {
        "asset": "fact_orders_enriched",
        "column": "order_id",
        "layer": "curated_internal",
        "classification": "identificador_indireto",
        "risk_level": "medium",
        "published_action": "pseudonymize",
        "business_need": "deduplicação e agregação por pedido",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "customer_id",
        "layer": "curated_internal",
        "classification": "dado_pessoal_indireto",
        "risk_level": "high",
        "published_action": "remove",
        "business_need": "join técnico com cliente transacional",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "customer_unique_id",
        "layer": "curated_internal",
        "classification": "dado_pessoal_indireto",
        "risk_level": "high",
        "published_action": "pseudonymize",
        "business_need": "contagem de clientes únicos",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "customer_city",
        "layer": "curated_internal",
        "classification": "quase_identificador",
        "risk_level": "high",
        "published_action": "remove",
        "business_need": "análise geográfica fina opcional",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "customer_zip_code_prefix",
        "layer": "curated_internal",
        "classification": "quase_identificador",
        "risk_level": "high",
        "published_action": "remove",
        "business_need": "localização parcial",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "seller_id",
        "layer": "curated_internal",
        "classification": "identificador_comercial",
        "risk_level": "medium",
        "published_action": "remove",
        "business_need": "join técnico com seller",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "seller_city",
        "layer": "curated_internal",
        "classification": "quase_identificador",
        "risk_level": "medium",
        "published_action": "remove",
        "business_need": "geografia operacional detalhada",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "seller_zip_code_prefix",
        "layer": "curated_internal",
        "classification": "quase_identificador",
        "risk_level": "medium",
        "published_action": "remove",
        "business_need": "localização parcial do seller",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_enriched",
        "column": "review_comment_message",
        "layer": "source_only",
        "classification": "texto_livre_potencialmente_sensivel",
        "risk_level": "high",
        "published_action": "aggregate_or_remove",
        "business_need": "sinal de existência de comentário",
        "publication_allowed": False,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "order_id",
        "layer": "published_dashboard",
        "classification": "identificador_pseudonimizado",
        "risk_level": "low_medium",
        "published_action": "keep",
        "business_need": "contagem e drill-down controlado",
        "publication_allowed": True,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "customer_unique_id",
        "layer": "published_dashboard",
        "classification": "identificador_pseudonimizado",
        "risk_level": "low_medium",
        "published_action": "keep",
        "business_need": "clientes únicos",
        "publication_allowed": True,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "customer_state",
        "layer": "published_dashboard",
        "classification": "analitico_agregado",
        "risk_level": "low",
        "published_action": "keep",
        "business_need": "análise regional",
        "publication_allowed": True,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "seller_state",
        "layer": "published_dashboard",
        "classification": "analitico_agregado",
        "risk_level": "low",
        "published_action": "keep",
        "business_need": "análise regional por seller",
        "publication_allowed": True,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "total_item_value",
        "layer": "published_dashboard",
        "classification": "analitico_publico",
        "risk_level": "low",
        "published_action": "keep",
        "business_need": "receita e ticket",
        "publication_allowed": True,
    },
    {
        "asset": "fact_orders_dashboard",
        "column": "delivery_time_days",
        "layer": "published_dashboard",
        "classification": "analitico_publico",
        "risk_level": "low",
        "published_action": "keep",
        "business_need": "logística e SLA",
        "publication_allowed": True,
    },
]


def build_classification_inventory() -> pd.DataFrame:
    return pd.DataFrame(CLASSIFICATION_ROWS)


def save_inventory(df: pd.DataFrame) -> Path:
    ensure_directory(CATALOG_DIR)
    df.to_csv(CLASSIFICATION_PATH, index=False)
    LOGGER.info("Inventário de classificação salvo em %s", CLASSIFICATION_PATH)
    return CLASSIFICATION_PATH


def render_report(df: pd.DataFrame) -> str:
    lines = [
        "# Classificação de Dados",
        "",
        "Este documento materializa a classificação dos principais campos com impacto de privacidade e governança no projeto.",
        "",
        "## Critérios",
        "",
        "- `identificador_indireto`: chave transacional ou persistente que não identifica diretamente, mas permite rastreamento.",
        "- `quase_identificador`: atributo que, em combinação com outros, aumenta risco de reidentificação.",
        "- `identificador_pseudonimizado`: chave transformada para preservar uso analítico com menor exposição.",
        "- `analitico_publico` ou `analitico_agregado`: atributo adequado à camada publicada por ser necessário e de baixo risco.",
        "",
        "## Inventário",
        "",
        "| Asset | Coluna | Camada | Classificação | Risco | Ação na publicada | Publicável |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in df.itertuples(index=False):
        lines.append(
            f"| `{row.asset}` | `{row.column}` | `{row.layer}` | `{row.classification}` | `{row.risk_level}` | `{row.published_action}` | `{row.publication_allowed}` |"
        )
    return "\n".join(lines)


def save_report(df: pd.DataFrame) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(df), encoding="utf-8")
    LOGGER.info("Documentação de classificação salva em %s", REPORT_PATH)
    return REPORT_PATH


def main() -> None:
    configure_logging()
    df = build_classification_inventory()
    save_inventory(df)
    save_report(df)


if __name__ == "__main__":
    main()
