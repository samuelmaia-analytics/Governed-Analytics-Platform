"""Join-health and financial reconciliation summaries for Olist analytics."""

from __future__ import annotations

import pandas as pd


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


def build_payment_reconciliation_summary(
    fact_table: pd.DataFrame,
) -> dict[str, float]:
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
