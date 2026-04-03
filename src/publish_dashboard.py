from __future__ import annotations

import hashlib
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import (
    ANALYTICS_DIR,
    DOCS_DIR,
    PUBLISHED_DASHBOARD_DIR,
    QUALITY_DIR,
    ROOT_DIR,
)
from src.data_classification import CLASSIFICATION_ROWS
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
SOURCE_FACT_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
PUBLISHED_PARQUET_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.parquet"
PUBLISHED_CSV_PATH = PUBLISHED_DASHBOARD_DIR / "fact_orders_dashboard.csv"
REPORT_PATH = DOCS_DIR / "privacy_governance.md"
PRIVACY_RESULTS_PATH = QUALITY_DIR / "privacy_governance_results.csv"
PRIVACY_CONTRACT_PATH = ROOT_DIR / "contracts" / "governance" / "privacy_governance.json"

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


@dataclass(frozen=True)
class PrivacyCheck:
    check_name: str
    status: str
    details: str


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


def load_privacy_contract(path: Path = PRIVACY_CONTRACT_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _validate_prefixed_tokens(series: pd.Series, prefix: str) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return True
    sample = non_null.head(100)
    return all(isinstance(value, str) and value.startswith(prefix) for value in sample)


def validate_privacy_controls(df: pd.DataFrame, contract: dict[str, object]) -> list[PrivacyCheck]:
    checks: list[PrivacyCheck] = []
    actual_columns = set(df.columns)
    required_columns = set(contract.get("required_columns", []))
    forbidden_columns = set(contract.get("forbidden_columns", []))
    unexpected_columns = sorted(actual_columns - required_columns)
    missing_columns = sorted(required_columns - actual_columns)
    forbidden_exposed = sorted(actual_columns & forbidden_columns)

    checks.append(
        PrivacyCheck(
            check_name="required_columns",
            status="PASS" if not missing_columns else "FAIL",
            details=f"Ausentes: {missing_columns if missing_columns else 'nenhuma'}",
        )
    )
    checks.append(
        PrivacyCheck(
            check_name="forbidden_columns_absent",
            status="PASS" if not forbidden_exposed else "FAIL",
            details=f"Presentes indevidas: {forbidden_exposed if forbidden_exposed else 'nenhuma'}",
        )
    )
    checks.append(
        PrivacyCheck(
            check_name="unexpected_columns",
            status="PASS" if not unexpected_columns else "FAIL",
            details=f"Inesperadas: {unexpected_columns if unexpected_columns else 'nenhuma'}",
        )
    )

    pseudonymized_columns = contract.get("pseudonymized_columns", {})
    if isinstance(pseudonymized_columns, dict):
        for column, prefix in pseudonymized_columns.items():
            if column not in df.columns:
                checks.append(PrivacyCheck(f"pseudonymized__{column}", "FAIL", "Coluna obrigatória ausente."))
                continue
            checks.append(
                PrivacyCheck(
                    check_name=f"pseudonymized__{column}",
                    status="PASS" if _validate_prefixed_tokens(df[column], str(prefix)) else "FAIL",
                    details=f"Prefixo esperado: `{prefix}`",
                )
            )

    default_fill_values = contract.get("default_fill_values", {})
    if isinstance(default_fill_values, dict):
        for column, default_value in default_fill_values.items():
            if column not in df.columns:
                checks.append(PrivacyCheck(f"default_fill__{column}", "FAIL", "Coluna obrigatória ausente."))
                continue
            null_count = int(df[column].isna().sum())
            has_default = bool((df[column] == default_value).any())
            checks.append(
                PrivacyCheck(
                    check_name=f"default_fill__{column}",
                    status="PASS" if null_count == 0 and has_default else "FAIL",
                    details=f"nulls={null_count} | default_observado={has_default}",
                )
            )

    protected_source_columns = sorted(
        row["column"]
        for row in CLASSIFICATION_ROWS
        if row.get("asset") == "fact_orders_enriched"
        and row.get("publication_allowed") is False
        and row.get("published_action") in {"remove", "aggregate_or_remove"}
    )
    leaked_columns = [column for column in protected_source_columns if column in actual_columns]
    checks.append(
        PrivacyCheck(
            check_name="classification_leakage",
            status="PASS" if not leaked_columns else "FAIL",
            details=f"Colunas sensíveis expostas: {leaked_columns if leaked_columns else 'nenhuma'}",
        )
    )

    return checks


def save_privacy_results(checks: list[PrivacyCheck]) -> Path:
    ensure_directory(QUALITY_DIR)
    pd.DataFrame(asdict(check) for check in checks).to_csv(PRIVACY_RESULTS_PATH, index=False)
    LOGGER.info("Resultados de privacidade salvos em %s", PRIVACY_RESULTS_PATH)
    return PRIVACY_RESULTS_PATH


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


def render_report(artifacts: PublishedArtifacts, contract: dict[str, object], checks: list[PrivacyCheck]) -> str:
    principles = contract.get("lgpd_principles", [])
    validation_summary = "PASS" if all(check.status == "PASS" for check in checks) else "FAIL"
    lines = [
        "# Privacidade, LGPD e Governança",
        "",
        "Este documento registra as decisões de privacidade por design e governança aplicadas ao projeto.",
        "",
        "## Controles Alinhados à LGPD",
        "",
        "O projeto usa o dataset público da Olist como caso analítico, mas aplica controles inspirados em privacidade por design para reduzir exposição desnecessária na camada publicada.",
    ]
    if isinstance(principles, list):
        for principle in principles:
            if isinstance(principle, dict):
                lines.append(f"- `{principle.get('principle')}`: {principle.get('control')}")

    lines.extend(
        [
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
    )
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
            f"- Resultado da validação LGPD/governança: **{validation_summary}**",
            f"- Evidência tabular dos checks: `{to_project_relative_path(PRIVACY_RESULTS_PATH)}`",
            "",
            "## Validação Aplicada",
            "",
            "| Check | Status | Detalhes |",
            "| --- | --- | --- |",
        ]
    )
    for check in checks:
        lines.append(f"| `{check.check_name}` | **{check.status}** | {check.details} |")

    lines.extend(
        [
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


def save_report(artifacts: PublishedArtifacts, contract: dict[str, object], checks: list[PrivacyCheck]) -> Path:
    ensure_directory(DOCS_DIR)
    REPORT_PATH.write_text(render_report(artifacts, contract, checks), encoding="utf-8")
    LOGGER.info("Documentação de privacidade salva em %s", REPORT_PATH)
    return REPORT_PATH


def run_publish_dashboard() -> PublishedArtifacts:
    internal_df = load_internal_fact()
    published_df = build_published_dashboard_table(internal_df)
    contract = load_privacy_contract()
    checks = validate_privacy_controls(published_df, contract)
    save_privacy_results(checks)
    failures = [check for check in checks if check.status == "FAIL"]
    if failures:
        failed_names = ", ".join(check.check_name for check in failures)
        raise RuntimeError(f"Validação LGPD/governança falhou na camada publicada: {failed_names}")
    artifacts = save_outputs(published_df)
    save_report(artifacts, contract, checks)
    return artifacts


if __name__ == "__main__":
    configure_logging()
    run_publish_dashboard()
