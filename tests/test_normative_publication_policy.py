from __future__ import annotations

from pathlib import Path

import pytest

from src.normative_publication_policy import (
    EvidenceValidationError,
    NormativeDecision,
    NormativeEvidence,
    NormativePublicationPolicy,
    PolicyValidationError,
    evaluate_normative_policy,
    load_policy_for_dataset,
    load_policy_from_contract_dict,
    load_policy_from_contract_file,
)


def test_load_policy_for_real_contract_fact_orders_dashboard() -> None:
    policy = load_policy_for_dataset("fact_orders_dashboard")

    assert policy.minimum_quality_score == 80
    assert policy.maximum_privacy_risk_score == 70
    assert policy.freshness_requirement == "fresh"
    assert policy.contract_required is True
    assert "schema_contract_failed" in policy.blocking_conditions


def test_evaluate_normative_policy_approved_when_all_thresholds_met() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": [
                    "critical_rule_failures_gt_0",
                    "schema_contract_failed",
                    "sensitive_data_without_protection",
                    "privacy_risk_score_gt_maximum",
                    "freshness_stale",
                ],
            },
            "publication_criteria": {
                "required_status": "Approved",
                "quality_threshold": ">=80",
                "privacy_threshold": "<=70",
                "freshness_threshold": "fresh",
                "failed_checks_threshold": 0,
            },
        }
    )

    decision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=80,
            privacy_risk_score=70,
            freshness_status="fresh",
            schema_contract_status="passed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
            failed_checks_count=0,
        ),
    )

    assert decision.authorized is True
    assert decision.decision == "Approved"


def test_evaluate_normative_policy_fail_safe_when_evidence_missing() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    decision = evaluate_normative_policy(policy, NormativeEvidence())

    assert decision.authorized is False
    assert decision.decision == "Blocked"
    assert any("Evidencias ausentes" in reason for reason in decision.reasons)


def test_load_policy_rejects_missing_publication_policy() -> None:
    with pytest.raises(PolicyValidationError, match="publication_policy"):
        load_policy_from_contract_dict({})


def test_load_policy_rejects_unknown_yaml_field_in_publication_policy() -> None:
    with pytest.raises(PolicyValidationError, match="Campos desconhecidos"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                    "unexpected": 123,
                }
            }
        )


def test_load_policy_rejects_missing_blocking_conditions() -> None:
    with pytest.raises(PolicyValidationError, match="blocking_conditions"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                }
            }
        )


def test_load_policy_rejects_contract_required_wrong_type() -> None:
    with pytest.raises(PolicyValidationError, match="contract_required"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": "true",
                    "blocking_conditions": ["schema_contract_failed"],
                }
            }
        )


def test_load_policy_rejects_unknown_blocking_condition() -> None:
    with pytest.raises(
        PolicyValidationError,
        match="Blocking condition desconhecida",
    ):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["unknown_condition"],
                }
            }
        )


def test_load_policy_rejects_malformed_threshold() -> None:
    with pytest.raises(PolicyValidationError, match="Threshold invalido"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "quality_threshold": "=>80",
                    "freshness_threshold": "fresh",
                },
            }
        )


def test_load_policy_rejects_threshold_out_of_score_range() -> None:
    with pytest.raises(PolicyValidationError, match="intervalo"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "quality_threshold": ">=101",
                    "freshness_threshold": "fresh",
                },
            }
        )


def test_load_policy_rejects_publication_criteria_unknown_field() -> None:
    with pytest.raises(PolicyValidationError, match="publication_criteria"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "freshness_threshold": "fresh",
                    "unexpected": 123,
                },
            }
        )


def test_load_policy_rejects_semantic_contradiction_freshness_threshold() -> None:
    with pytest.raises(PolicyValidationError, match="freshness_threshold difere"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "freshness_threshold": "stale",
                },
            }
        )


def test_load_policy_rejects_failed_checks_threshold_bool() -> None:
    with pytest.raises(PolicyValidationError, match="inteiro"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "freshness_threshold": "fresh",
                    "failed_checks_threshold": True,
                },
            }
        )


@pytest.mark.parametrize(
    ("expr", "message"),
    [
        (">=", "Threshold invalido"),
        (">=abc", "Threshold invalido"),
        ("80", "Threshold invalido"),
    ],
)
def test_parse_threshold_expr_rejects_invalid_inputs(expr: str, message: str) -> None:
    from src import normative_publication_policy as module

    with pytest.raises(PolicyValidationError, match=message):
        module._parse_threshold_expr(expr)


@pytest.mark.parametrize(
    ("field", "expr"),
    [
        ("publication_criteria.quality_threshold", "<=80"),
        ("publication_criteria.privacy_threshold", ">=70"),
    ],
)
def test_validate_threshold_expr_rejects_invalid_operator(field: str, expr: str) -> None:
    from src import normative_publication_policy as module

    allow_ops = {">=", ">"} if "quality" in field else {"<=", "<"}

    with pytest.raises(PolicyValidationError, match="Operador invalido"):
        module._validate_threshold_expr(
            expr,
            field=field,
            allow_ops=allow_ops,
            require_score_range=True,
        )


@pytest.mark.parametrize(
    ("value", "expr", "expected"),
    [
        (10, ">=80", False),
        (80, ">=80", True),
        (80, ">80", False),
        (81, ">80", True),
        (70, "<=70", True),
        (71, "<=70", False),
        (69, "<70", True),
        (70, "<70", False),
        (10, "==10", True),
        (10, "==11", False),
        (10, ">9", True),
        (10, "<11", True),
    ],
)
def test_eval_threshold_operators(value: int, expr: str, expected: bool) -> None:
    from src import normative_publication_policy as module

    assert module._eval_threshold(value, expr) is expected


def test_evidence_rejects_negative_scores() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="intervalo"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=-1,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_evidence_rejects_scores_over_100() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="intervalo"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=0,
                privacy_risk_score=101,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_evidence_rejects_boolean_used_as_number() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="inteiro"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=True,  # type: ignore[arg-type]
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_policy_built_programmatically_with_invalid_data_is_rejected() -> None:
    with pytest.raises(PolicyValidationError, match="intervalo"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 101,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                }
            }
        )


def test_policy_direct_instantiation_rejects_unknown_blocking_condition() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("unknown_condition",),  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="Blocking condition"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_policy_direct_instantiation_rejects_blocking_conditions_wrong_type() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=["schema_contract_failed"],  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="blocking_conditions"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_policy_direct_instantiation_rejects_threshold_not_string() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        quality_threshold=123,  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="quality_threshold"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_policy_direct_instantiation_rejects_invalid_freshness_requirement() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="invalid",  # type: ignore[arg-type]
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="freshness_requirement"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_load_policy_from_contract_file_handles_malformed_yaml(tmp_path: Path) -> None:
    contract_path = tmp_path / "bad.contract.yml"
    contract_path.write_text("publication_policy: [\n", encoding="utf-8")

    with pytest.raises(PolicyValidationError):
        load_policy_from_contract_file(contract_path)


def test_combined_missing_and_invalid_evidence_never_authorizes() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    decision: NormativeDecision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=-1,
            privacy_risk_score=None,
            freshness_status="fresh",
            schema_contract_status="passed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
        ),
    )

    assert decision.authorized is False
    assert decision.decision == "Blocked"


def test_policy_file_loader_rejects_non_mapping_document(tmp_path: Path) -> None:
    contract_path = tmp_path / "invalid.contract.yml"
    contract_path.write_text("- not-a-mapping\n", encoding="utf-8")

    with pytest.raises(PolicyValidationError, match="documento de mapeamento"):
        load_policy_from_contract_file(contract_path)


def test_determinism_same_inputs_same_outputs() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["privacy_risk_score_gt_maximum"],
            }
        }
    )

    evidence = NormativeEvidence(
        data_quality_score=95,
        privacy_risk_score=10,
        freshness_status="fresh",
        schema_contract_status="passed",
        critical_rule_failures=0,
        has_sensitive_data_without_protection=False,
    )

    first = evaluate_normative_policy(policy, evidence)
    second = evaluate_normative_policy(policy, evidence)

    assert first == second


@pytest.mark.parametrize(
    ("condition", "evidence"),
    [
        (
            "critical_rule_failures_gt_0",
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=1,
                has_sensitive_data_without_protection=False,
            ),
        ),
        (
            "schema_contract_failed",
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="failed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        ),
        (
            "sensitive_data_without_protection",
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=True,
            ),
        ),
        (
            "privacy_risk_score_gt_maximum",
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=71,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        ),
        (
            "freshness_stale",
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="stale",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        ),
    ],
)
def test_blocking_conditions_enforced(condition: str, evidence: NormativeEvidence) -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": [condition],
            }
        }
    )

    decision = evaluate_normative_policy(policy, evidence)
    assert decision.authorized is False
    assert decision.decision == "Blocked"
    assert any("blocking_conditions" in reason for reason in decision.reasons)


def test_policy_threshold_reasons_are_reported() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 80,
                "maximum_privacy_risk_score": 70,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    decision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=79,
            privacy_risk_score=71,
            freshness_status="warning",
            schema_contract_status="passed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
        ),
    )

    assert decision.authorized is False
    assert decision.decision == "Blocked"
    assert any("minimum_quality_score" in reason for reason in decision.reasons)
    assert any("maximum_privacy_risk_score" in reason for reason in decision.reasons)
    assert any("freshness_requirement" in reason for reason in decision.reasons)


def test_contract_required_blocks_when_schema_not_passed() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["privacy_risk_score_gt_maximum"],
            }
        }
    )

    decision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=100,
            privacy_risk_score=0,
            freshness_status="fresh",
            schema_contract_status="failed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
        ),
    )

    assert decision.authorized is False
    assert any("contract_required" in reason for reason in decision.reasons)


def test_publication_criteria_threshold_reasons() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            },
            "publication_criteria": {
                "required_status": "Approved",
                "quality_threshold": ">=80",
                "privacy_threshold": "<=70",
                "freshness_threshold": "fresh",
                "failed_checks_threshold": 0,
            },
        }
    )

    decision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=79,
            privacy_risk_score=71,
            freshness_status="fresh",
            schema_contract_status="passed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
            failed_checks_count=1,
        ),
    )

    assert decision.authorized is False
    assert any("quality_threshold" in reason for reason in decision.reasons)
    assert any("privacy_threshold" in reason for reason in decision.reasons)
    assert any("failed_checks_threshold" in reason for reason in decision.reasons)


def test_failed_checks_threshold_requires_failed_checks_count_fail_safe() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            },
            "publication_criteria": {
                "required_status": "Approved",
                "freshness_threshold": "fresh",
                "failed_checks_threshold": 0,
            },
        }
    )

    decision = evaluate_normative_policy(
        policy,
        NormativeEvidence(
            data_quality_score=100,
            privacy_risk_score=0,
            freshness_status="fresh",
            schema_contract_status="passed",
            critical_rule_failures=0,
            has_sensitive_data_without_protection=False,
            failed_checks_count=None,
        ),
    )

    assert decision.authorized is False
    assert any("failed_checks_count" in reason for reason in decision.reasons)


def test_evidence_rejects_invalid_schema_contract_status() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="schema_contract_status"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="unknown",  # type: ignore[arg-type]
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_evidence_rejects_invalid_freshness_status() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="freshness_status"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="invalid",  # type: ignore[arg-type]
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection=False,
            ),
        )


def test_evidence_rejects_invalid_has_sensitive_data_type() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match="has_sensitive_data_without_protection"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=0,
                has_sensitive_data_without_protection="no",  # type: ignore[arg-type]
            ),
        )


def test_load_policy_for_dataset_errors_on_missing_contract(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_policy_for_dataset("missing_dataset", contracts_dir=tmp_path)


def test_load_policy_for_dataset_errors_on_duplicate_contracts(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()

    content = (
        "publication_policy:\n"
        "  minimum_quality_score: 80\n"
        "  maximum_privacy_risk_score: 70\n"
        "  freshness_requirement: fresh\n"
        "  contract_required: true\n"
        "  blocking_conditions:\n"
        "    - schema_contract_failed\n"
    )

    (tmp_path / "a" / "dup.contract.yml").write_text(content, encoding="utf-8")
    (tmp_path / "b" / "dup.contract.yml").write_text(content, encoding="utf-8")

    with pytest.raises(PolicyValidationError, match="Mais de um contrato"):
        load_policy_for_dataset("dup", contracts_dir=tmp_path)

def test_load_policy_rejects_failed_checks_threshold_negative() -> None:
    with pytest.raises(PolicyValidationError, match=">= 0"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 0,
                    "maximum_privacy_risk_score": 100,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Approved",
                    "freshness_threshold": "fresh",
                    "failed_checks_threshold": -1,
                },
            }
        )


def test_load_policy_rejects_invalid_freshness_requirement() -> None:
    with pytest.raises(PolicyValidationError, match="freshness_requirement"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "invalid",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                }
            }
        )


def test_load_policy_rejects_invalid_required_status_value() -> None:
    with pytest.raises(PolicyValidationError, match="required_status"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": ["schema_contract_failed"],
                },
                "publication_criteria": {
                    "required_status": "Invalid",
                    "freshness_threshold": "fresh",
                },
            }
        )


def test_parse_supported_blocking_conditions_optional_none_returns_empty_tuple() -> None:
    from src import normative_publication_policy as module

    assert module._parse_supported_blocking_conditions(None, required=False) == ()


def test_parse_supported_blocking_conditions_rejects_non_list_type() -> None:
    from src import normative_publication_policy as module

    with pytest.raises(PolicyValidationError, match="deve ser uma lista"):
        module._parse_supported_blocking_conditions("x", required=False)


def test_parse_supported_blocking_conditions_rejects_non_string_items() -> None:
    from src import normative_publication_policy as module

    with pytest.raises(PolicyValidationError, match="devem ser strings"):
        module._parse_supported_blocking_conditions([1], required=False)


def test_load_policy_rejects_empty_blocking_conditions_list() -> None:
    with pytest.raises(PolicyValidationError, match="nao pode ser vazio"):
        load_policy_from_contract_dict(
            {
                "publication_policy": {
                    "minimum_quality_score": 80,
                    "maximum_privacy_risk_score": 70,
                    "freshness_requirement": "fresh",
                    "contract_required": True,
                    "blocking_conditions": [],
                }
            }
        )


def test_eval_threshold_raises_on_unsupported_operator(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import normative_publication_policy as module

    def fake_parse(_: str) -> tuple[str, int]:
        return "!=", 10

    monkeypatch.setattr(module, "_parse_threshold_expr", fake_parse)

    with pytest.raises(PolicyValidationError, match="Operador nao suportado"):
        module._eval_threshold(10, "!=10")


def test_policy_direct_instantiation_rejects_minimum_quality_score_not_int() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score="80",  # type: ignore[arg-type]
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="minimum_quality_score deve ser inteiro"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_minimum_quality_score_out_of_range() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=-1,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="fora do intervalo"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_maximum_privacy_risk_score_not_int() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score="70",  # type: ignore[arg-type]
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="maximum_privacy_risk_score deve ser inteiro"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_maximum_privacy_risk_score_out_of_range() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=101,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="fora do intervalo"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_contract_required_not_bool() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required="yes",  # type: ignore[arg-type]
        blocking_conditions=("schema_contract_failed",),
    )

    with pytest.raises(PolicyValidationError, match="contract_required deve ser booleano"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_empty_blocking_conditions_tuple() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=(),
    )

    with pytest.raises(PolicyValidationError, match="nao pode aprovar por omissao"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_required_status_invalid() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        required_status="invalid",  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="required_status invalido"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_required_status_not_approved() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        required_status="Needs Review",  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="diferente de Approved"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_failed_checks_threshold_wrong_type() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        failed_checks_threshold="0",  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="failed_checks_threshold deve ser inteiro"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_failed_checks_threshold_negative() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        failed_checks_threshold=-1,
    )

    with pytest.raises(PolicyValidationError, match="failed_checks_threshold deve ser >= 0"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_policy_direct_instantiation_rejects_freshness_threshold_invalid() -> None:
    policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=70,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=("schema_contract_failed",),
        freshness_threshold="invalid",  # type: ignore[arg-type]
    )

    with pytest.raises(PolicyValidationError, match="freshness_threshold"):
        evaluate_normative_policy(policy, NormativeEvidence())


def test_evidence_rejects_negative_critical_rule_failures() -> None:
    policy = load_policy_from_contract_dict(
        {
            "publication_policy": {
                "minimum_quality_score": 0,
                "maximum_privacy_risk_score": 100,
                "freshness_requirement": "fresh",
                "contract_required": True,
                "blocking_conditions": ["schema_contract_failed"],
            }
        }
    )

    with pytest.raises(EvidenceValidationError, match=">= 0"):
        evaluate_normative_policy(
            policy,
            NormativeEvidence(
                data_quality_score=100,
                privacy_risk_score=0,
                freshness_status="fresh",
                schema_contract_status="passed",
                critical_rule_failures=-1,
                has_sensitive_data_without_protection=False,
            ),
        )
