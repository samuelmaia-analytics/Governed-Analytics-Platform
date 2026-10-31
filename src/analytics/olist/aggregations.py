"""Order-level payment and review aggregations for Olist analytics."""

from __future__ import annotations

import pandas as pd

from src.analytics.olist.cleaning import deduplicate


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
