"""Persistence and reporting for the Olist analytical mart."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.analytics.olist.reconciliation import (
    build_join_health_summary,
    build_payment_reconciliation_summary,
)
from src.utils import ensure_directory


@dataclass
class BuildArtifacts:
    fact_table: pd.DataFrame
    parquet_path: Path
    csv_path: Path
    duckdb_path: Path
    report_path: Path


def save_outputs(
    fact_table: pd.DataFrame,
    *,
    analytics_dir: Path,
    parquet_path: Path,
    csv_path: Path,
    duckdb_path: Path,
    duckdb_table: str,
    write_dataframe_fn: Callable[[pd.DataFrame, str, Path], Path],
    logger: logging.Logger,
) -> tuple[Path, Path, Path]:
    ensure_directory(analytics_dir)
    fact_table.to_parquet(parquet_path, index=False)
    fact_table.to_csv(csv_path, index=False)
    persisted_duckdb_path = write_dataframe_fn(
        fact_table, duckdb_table, duckdb_path
    )
    logger.info(
        "Saidas salvas em %s, %s e %s::%s",
        parquet_path,
        csv_path,
        persisted_duckdb_path,
        duckdb_table,
    )
    return parquet_path, csv_path, persisted_duckdb_path


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


def save_report(
    fact_table: pd.DataFrame,
    *,
    docs_dir: Path,
    report_path: Path,
    render_report_fn: Callable[[pd.DataFrame], str],
    logger: logging.Logger,
) -> Path:
    ensure_directory(docs_dir)
    report_path.write_text(render_report_fn(fact_table), encoding="utf-8")
    logger.info("Relatório salvo em %s", report_path)
    return report_path
