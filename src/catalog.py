from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import (
    ANALYTICS_DIR,
    CATALOG_DIR,
    DOCS_DIR,
    LANDING_DIR,
    PUBLISHED_DASHBOARD_DIR,
    PROFILING_DIR,
    QUALITY_DIR,
    QUERY_RESULTS_DIR,
    SCREENSHOTS_DIR,
    SQL_DIR,
    STANDARDIZED_DIR,
)
from src.ingest import configure_logging
from src.utils import ensure_directory


LOGGER = logging.getLogger(__name__)
PROJECT_NAME = "samuelmaia_DDF_032026"
COLLECTION_ID = "olist_analytics_case_collection"
COLLECTION_PATH = CATALOG_DIR / "dadosfera_collection.json"
ASSET_INVENTORY_PATH = CATALOG_DIR / "collection_assets_inventory.csv"
REPORT_PATH = DOCS_DIR / "collection_catalog.md"


@dataclass(frozen=True)
class CatalogAsset:
    asset_name: str
    zone: str
    asset_type: str
    relative_path: str
    file_format: str
    description: str
    grain: str
    primary_key: str
    source_assets: str
    record_count: int | None
    column_count: int | None
    publication_ready: bool


def detect_file_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".parquet":
        return "parquet"
    if suffix == ".png":
        return "png"
    if suffix == ".sql":
        return "sql"
    if suffix == ".md":
        return "markdown"
    if suffix == ".json":
        return "json"
    return suffix.lstrip(".") or "unknown"


def load_tabular_metadata(path: Path) -> tuple[int | None, int | None]:
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
            return len(df), len(df.columns)
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
            return len(df), len(df.columns)
    except Exception as exc:  # pragma: no cover - defensive fallback
        LOGGER.warning("Falha ao ler metadados de %s: %s", path, exc)
    return None, None


def build_asset(
    *,
    path: Path,
    zone: str,
    asset_type: str,
    description: str,
    grain: str,
    primary_key: str,
    source_assets: str,
    publication_ready: bool,
) -> CatalogAsset:
    record_count, column_count = load_tabular_metadata(path)
    return CatalogAsset(
        asset_name=path.stem,
        zone=zone,
        asset_type=asset_type,
        relative_path=path.relative_to(Path(__file__).resolve().parent.parent).as_posix(),
        file_format=detect_file_format(path),
        description=description,
        grain=grain,
        primary_key=primary_key,
        source_assets=source_assets,
        record_count=record_count,
        column_count=column_count,
        publication_ready=publication_ready,
    )


def collect_assets() -> list[CatalogAsset]:
    root_dir = Path(__file__).resolve().parent.parent
    assets: list[CatalogAsset] = []

    for path in sorted((LANDING_DIR / "olist").glob("*.csv")):
        assets.append(
            build_asset(
                path=path,
                zone="raw_landing",
                asset_type="source_table",
                description="Arquivo bruto do dataset Olist recebido sem transformação.",
                grain="depende da tabela de origem",
                primary_key="não aplicável na landing",
                source_assets="dataset_olist_kaggle",
                publication_ready=False,
            )
        )

    for path in sorted((STANDARDIZED_DIR / "olist").glob("*.parquet")):
        assets.append(
            build_asset(
                path=path,
                zone="standardized",
                asset_type="standardized_table",
                description="Tabela padronizada em parquet para reuso técnico nas próximas etapas do pipeline.",
                grain="mantém a granularidade da origem",
                primary_key="mesma chave da origem quando aplicável",
                source_assets="raw_landing/olist",
                publication_ready=False,
            )
        )

    curated_specs = [
        (
            ANALYTICS_DIR / "fact_orders_enriched.parquet",
            "curated_analytics",
            "analytics_fact",
            "Tabela analítica principal interna do case, pronta para SQL, qualidade e processamento analítico.",
            "1 linha por item de pedido",
            "order_id + order_item_id + product_id + seller_id",
            "olist_orders, olist_order_items, olist_products, olist_customers, olist_sellers, olist_order_payments, olist_order_reviews, product_category_name_translation",
            False,
        ),
        (
            QUALITY_DIR / "fact_orders_enriched_quality_checks.csv",
            "curated_quality",
            "quality_report_table",
            "Resultado estruturado dos testes de qualidade da camada analítica.",
            "1 linha por check",
            "check_name",
            "fact_orders_enriched",
            True,
        ),
    ]
    for path, zone, asset_type, description, grain, primary_key, source_assets, publication_ready in curated_specs:
        if path.exists():
            assets.append(
                build_asset(
                    path=path,
                    zone=zone,
                    asset_type=asset_type,
                    description=description,
                    grain=grain,
                    primary_key=primary_key,
                    source_assets=source_assets,
                    publication_ready=publication_ready,
                )
            )

    published_specs = [
        (
            PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet",
            "published_dashboard",
            "published_analytics_table",
            "Camada publicada e minimizada para consumo do dashboard Streamlit, com identificadores pseudonimizados.",
            "1 linha por item de pedido",
            "order_id + order_item_id",
            "fact_orders_enriched",
            True,
        ),
    ]
    for path, zone, asset_type, description, grain, primary_key, source_assets, publication_ready in published_specs:
        if path.exists():
            assets.append(
                build_asset(
                    path=path,
                    zone=zone,
                    asset_type=asset_type,
                    description=description,
                    grain=grain,
                    primary_key=primary_key,
                    source_assets=source_assets,
                    publication_ready=publication_ready,
                )
            )

    for path in sorted(QUERY_RESULTS_DIR.glob("*.csv")):
        assets.append(
            build_asset(
                path=path,
                zone="curated_query_results",
                asset_type="query_result",
                description="Resultado materializado de query SQL do case para documentação e leitura executiva.",
                grain="depende da query",
                primary_key="não aplicável",
                source_assets="fact_orders_enriched",
                publication_ready=True,
            )
        )

    for path in sorted(PROFILING_DIR.glob("*.csv")):
        assets.append(
            build_asset(
                path=path,
                zone="staging_profiling",
                asset_type="profiling_asset",
                description="Artefato intermediário de profiling e análise exploratória.",
                grain="depende do ativo de profiling",
                primary_key="não aplicável",
                source_assets="raw_landing/olist",
                publication_ready=False,
            )
        )

    docs_to_catalog = [
        DOCS_DIR / "data_dictionary.md",
        DOCS_DIR / "data_classification.md",
        DOCS_DIR / "architecture.md",
        DOCS_DIR / "case_answers.md",
        DOCS_DIR / "about_dadosfera.md",
        DOCS_DIR / "genai_bonus.md",
        DOCS_DIR / "privacy_governance.md",
        DOCS_DIR / "governance_policy.md",
        DOCS_DIR / "schema_contract_report.md",
        REPORT_PATH,
    ]
    for path in docs_to_catalog:
        if path.exists():
            assets.append(
                build_asset(
                    path=path,
                    zone="documentation",
                    asset_type="documentation_asset",
                    description="Documento de apoio para catálogo, arquitetura, case e bônus.",
                    grain="não aplicável",
                    primary_key="não aplicável",
                    source_assets="documentacao_do_projeto",
                    publication_ready=True,
                )
            )

    classification_inventory_path = CATALOG_DIR / "data_classification_inventory.csv"
    if classification_inventory_path.exists():
        assets.append(
            build_asset(
                path=classification_inventory_path,
                zone="documentation",
                asset_type="classification_inventory",
                description="Inventário de classificação de dados com foco em sensibilidade, risco e ação por coluna.",
                grain="1 linha por coluna classificada",
                primary_key="asset + column",
                source_assets="governance_policy, privacy_governance, fact_orders_enriched, fact_orders_dashboard",
                publication_ready=True,
            )
        )

    schema_contract_results_path = QUALITY_DIR / "schema_contract_results.csv"
    if schema_contract_results_path.exists():
        assets.append(
            build_asset(
                path=schema_contract_results_path,
                zone="curated_quality",
                asset_type="schema_contract_results",
                description="Resultado estruturado da validacao dos contratos simples de schema.",
                grain="1 linha por check de contrato",
                primary_key="dataset_name + check_name",
                source_assets="contracts/curated, contracts/published",
                publication_ready=True,
            )
        )

    for path in sorted(SQL_DIR.joinpath("analytics").glob("*.sql")):
        assets.append(
            build_asset(
                path=path,
                zone="analytics_sql",
                asset_type="sql_query",
                description="Consulta analítica versionada para responder perguntas do case.",
                grain="depende da query",
                primary_key="não aplicável",
                source_assets="fact_orders_enriched",
                publication_ready=True,
            )
        )

    for path in sorted(SCREENSHOTS_DIR.joinpath("query_results").glob("*.png")):
        assets.append(
            build_asset(
                path=path,
                zone="documentation_media",
                asset_type="query_screenshot",
                description="Print tabular das queries do case para uso em markdown e revisão.",
                grain="não aplicável",
                primary_key="não aplicável",
                source_assets="curated_query_results",
                publication_ready=True,
            )
        )

    LOGGER.info("Catálogo consolidado com %s ativos.", len(assets))
    return assets


def build_collection_payload(assets: list[CatalogAsset]) -> dict[str, object]:
    publishable_assets = [asset for asset in assets if asset.publication_ready]
    return {
        "collection_id": COLLECTION_ID,
        "collection_name": "Olist Analytics Case Collection",
        "project_name": PROJECT_NAME,
        "description": (
            "Coleção de ativos do case técnico com dados do Olist, "
            "organizada em zonas de Data Lake e pronta para catalogação/publicação."
        ),
        "owner": "samuelmaia-analytics",
        "domains": ["e-commerce", "analytics-engineering", "data-apps"],
        "zones": ["raw_landing", "standardized", "staging_profiling", "curated_analytics", "curated_quality", "curated_query_results", "published_dashboard"],
        "publication_summary": {
            "total_assets": len(assets),
            "publishable_assets": len(publishable_assets),
            "core_asset": "fact_orders_enriched",
            "dashboard_consumer": "data/published/dashboard/fact_orders_dashboard.parquet",
            "catalog_version": "1.0.0",
        },
        "assets": [asdict(asset) for asset in assets],
    }


def save_outputs(assets: list[CatalogAsset]) -> tuple[Path, Path]:
    ensure_directory(CATALOG_DIR)
    assets_df = pd.DataFrame(asdict(asset) for asset in assets)
    assets_df.to_csv(ASSET_INVENTORY_PATH, index=False)

    collection_payload = build_collection_payload(assets)
    COLLECTION_PATH.write_text(json.dumps(collection_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Manifesto de coleção salvo em %s", COLLECTION_PATH)
    LOGGER.info("Inventário de ativos salvo em %s", ASSET_INVENTORY_PATH)
    return COLLECTION_PATH, ASSET_INVENTORY_PATH


def render_report(assets: list[CatalogAsset]) -> str:
    assets_df = pd.DataFrame(asdict(asset) for asset in assets)
    zone_summary = (
        assets_df.groupby("zone", as_index=False)
        .agg(total_assets=("asset_name", "count"), publishable_assets=("publication_ready", "sum"))
        .sort_values("zone")
    )

    lines = [
        "# Coleção e Catálogo de Ativos",
        "",
        "Este documento materializa a coleção do case em formato versionável, pronta para publicação e catalogação.",
        "",
        "## Objetivo",
        "",
        "- consolidar os ativos do projeto em um inventário único e rastreável",
        "- explicitar quais ativos estão prontos para publicação/consumo",
        "- demonstrar uma representação concreta da coleção exigida pelo case",
        "",
        "## Artefatos Gerados",
        "",
        f"- Manifesto JSON da coleção: `{COLLECTION_PATH.relative_to(Path(__file__).resolve().parent.parent).as_posix()}`",
        f"- Inventário tabular dos ativos: `{ASSET_INVENTORY_PATH.relative_to(Path(__file__).resolve().parent.parent).as_posix()}`",
        "",
        "## Resumo por Zona",
        "",
        "| Zona | Total de ativos | Ativos publicáveis |",
        "| --- | ---: | ---: |",
    ]
    for row in zone_summary.itertuples(index=False):
        lines.append(f"| `{row.zone}` | {int(row.total_assets)} | {int(row.publishable_assets)} |")

    core_assets = assets_df[assets_df["publication_ready"]].sort_values(["zone", "asset_name"])
    lines.extend(
        [
            "",
            "## Ativos Publicáveis da Coleção",
            "",
            "| Ativo | Zona | Tipo | Caminho |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in core_assets.itertuples(index=False):
        lines.append(f"| `{row.asset_name}` | `{row.zone}` | `{row.asset_type}` | `{row.relative_path}` |")

    lines.extend(
        [
            "",
            "## Uso no Case",
            "",
            "- `fact_orders_enriched` é o ativo analítico interno principal da coleção.",
            "- `fact_orders_dashboard` é a camada publicada e minimizada usada pelo Streamlit.",
            "- os resultados de qualidade, queries SQL e documentação derivada compõem a camada de evidência técnica do case.",
            "- o manifesto JSON pode ser usado como payload base para publicação ou integração futura com uma API de catálogo.",
            "",
            "## Observação",
            "",
            "- esta implementação representa uma coleção operacional em nível de projeto, adequada para prova de conceito local.",
            "- uma integração nativa com uma plataforma externa exigiria autenticação, endpoint e contrato específicos, que não foram fornecidos no enunciado.",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(assets: list[CatalogAsset]) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(assets), encoding="utf-8")
    LOGGER.info("Documentação da coleção salva em %s", REPORT_PATH)
    return REPORT_PATH


def main() -> None:
    configure_logging()
    assets = collect_assets()
    save_outputs(assets)
    save_report(assets)


if __name__ == "__main__":
    main()
