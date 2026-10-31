from __future__ import annotations

import pandas as pd

from src.publication_evidence import build_current_privacy_inputs
from src.publication_provenance import EvidenceSource, PipelineGovernanceContext
from src.publish_components.models import PrivacyCheck


def _checks() -> list[PrivacyCheck]:
    return [
        PrivacyCheck("forbidden_columns_absent", "PASS", "none"),
        PrivacyCheck("classification_leakage", "PASS", "none"),
    ]


def _inherent_source() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["x"],
            "user_id": ["x"],
            "email": ["x"],
            "phone": ["x"],
            "name": ["x"],
            "address": ["x"],
            "cpf": ["x"],
            "cnpj": ["x"],
            "document": ["x"],
            "gender": ["x"],
            "health_status": ["x"],
        }
    )


def _previous_false_positive_candidate() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "delivery_time_days": [12345678000195],
            "seller_dispatch_time_days": [12345678000195],
            "carrier_delivery_time_days": [12345678000195],
            "estimated_delay_days": [12345678000195],
            "seller_avg_delivery_days": [12345678000195],
            "seller_delay_rate": [12345678000195],
            "freight_to_price_ratio": [12345678000195],
            "total_item_value": [12345678000195],
            "product_category_name": ["books"],
            "product_category_name_english": ["books"],
            "order_id": ["11999999999"],
            "customer_unique_id": ["11999999999"],
            "seller_key": ["11999999999"],
        }
    )


def test_dual_scores_use_source_and_published_candidate_independently() -> None:
    published = pd.DataFrame({"metric": [1]})

    current = build_current_privacy_inputs(_inherent_source(), published, _checks())

    assert current.inherent_privacy_risk_score == 100
    assert current.residual_privacy_risk_score == 0
    assert current.risk_result is not None
    assert current.risk_result["score"] == current.inherent_privacy_risk_score
    assert current.classification is current.inherent_classification
    assert current.residual_classification is not None


def test_residual_score_reflects_corrected_classifier_without_changing_scorer() -> None:
    current = build_current_privacy_inputs(
        _inherent_source(), _previous_false_positive_candidate(), _checks()
    )

    assert current.inherent_privacy_risk_score == 100
    assert current.residual_privacy_risk_score == 30


def test_context_carries_both_scores_with_same_run_provenance() -> None:
    context = PipelineGovernanceContext("run-x")

    context.record_current_privacy(
        _inherent_source(), pd.DataFrame({"metric": [1]}), _checks()
    )

    assert context.inherent_privacy_risk_score == 100
    assert context.residual_privacy_risk_score == 0
    assert context.inherent_privacy_risk_provenance is not None
    assert context.residual_privacy_risk_provenance is not None
    assert context.inherent_privacy_risk_provenance.run_id == "run-x"
    assert context.residual_privacy_risk_provenance.run_id == "run-x"
    assert context.inherent_privacy_risk_provenance.source is EvidenceSource.PRIVACY
    assert context.residual_privacy_risk_provenance.source is EvidenceSource.PRIVACY
    assert context.build_provenanced_evidence().evidence.privacy_risk_score == 100


def test_dual_scores_remain_missing_without_same_run_dataframes() -> None:
    current = build_current_privacy_inputs(None, None, _checks())

    assert current.inherent_privacy_risk_score is None
    assert current.residual_privacy_risk_score is None
    assert current.risk_result is None
    assert current.protection.protected is None
