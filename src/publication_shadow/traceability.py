from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Literal

from src.normative_publication_policy import NormativePublicationPolicy

ShadowEvaluatorName = Literal["normative", "readiness", "operational_gate"]
TraceabilityStatus = Literal["compatible", "incompatible", "insufficient"]
PolicyIdentityStatus = Literal["proven", "not_proven", "incompatible", "insufficient"]

_ALLOWED_EVALUATORS: set[str] = {"normative", "readiness", "operational_gate"}
_REQUIRED_EVALUATORS: set[str] = set(_ALLOWED_EVALUATORS)
_SUPPORTED_POLICY_FINGERPRINT_PREFIX = "sha256:"

_SUPPORTED_SHA256_FINGERPRINT_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ShadowEvidenceContext:
    """Minimal traceability context for a single evaluator output.

    Notes:
    - `dataset_id` maps to the contract `dataset_name` used across the project.
    - `execution_id` maps to the `run_id` concept used by governance/provenance.
    - `policy_fingerprint` is optional and only comparable when present with the
      same semantic in more than one context.

    Runtime validation:
    - `evaluator_name` is validated because `Literal` does not enforce values
      at runtime.
    """

    evaluator_name: ShadowEvaluatorName
    dataset_id: str | None = None
    execution_id: str | None = None
    policy_fingerprint: str | None = None
    evidence_origin: str | None = None

    def __post_init__(self) -> None:
        if self.evaluator_name not in _ALLOWED_EVALUATORS:
            raise ValueError(
                "Unknown evaluator_name. Expected one of: "
                + ", ".join(sorted(_ALLOWED_EVALUATORS))
                + "."
            )


@dataclass(frozen=True)
class TraceabilityAssessment:
    status: TraceabilityStatus
    policy_identity_status: PolicyIdentityStatus
    reasons: tuple[str, ...] = ()

    @property
    def context_compatible(self) -> bool:
        return self.status == "compatible"

    @property
    def authorizes_publication(self) -> bool:
        return False

    @property
    def policy_identity_proven(self) -> bool:
        return self.policy_identity_status == "proven"


def fingerprint_normative_policy(policy: NormativePublicationPolicy) -> str:
    """Create a deterministic fingerprint for a normative policy instance.

    Pure function (no IO) to allow synthetic traceability checks.
    """

    payload: dict[str, Any] = {
        "minimum_quality_score": policy.minimum_quality_score,
        "maximum_privacy_risk_score": policy.maximum_privacy_risk_score,
        "freshness_requirement": policy.freshness_requirement,
        "contract_required": policy.contract_required,
        "blocking_conditions": list(policy.blocking_conditions),
        "required_status": policy.required_status,
        "quality_threshold": policy.quality_threshold,
        "privacy_threshold": policy.privacy_threshold,
        "freshness_threshold": policy.freshness_threshold,
        "failed_checks_threshold": policy.failed_checks_threshold,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    digest = hashlib.sha256(canonical).hexdigest()
    return f"{_SUPPORTED_POLICY_FINGERPRINT_PREFIX}{digest}"


def _normalize_identifier(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _normalize_policy_fingerprint(value: str | None) -> str | None:
    normalized = _normalize_identifier(value)
    if normalized is None:
        return None

    if normalized.lower().startswith(_SUPPORTED_POLICY_FINGERPRINT_PREFIX):
        return (
            _SUPPORTED_POLICY_FINGERPRINT_PREFIX
            + normalized[len(_SUPPORTED_POLICY_FINGERPRINT_PREFIX) :].lower()
        )

    return normalized


def _is_valid_sha256_fingerprint(value: str) -> bool:
    return _SUPPORTED_SHA256_FINGERPRINT_PATTERN.fullmatch(value) is not None


def assess_shadow_traceability(
    contexts: Iterable[ShadowEvidenceContext | None],
) -> TraceabilityAssessment:
    """Assess whether evaluator outputs can be proven to share execution context.

    Fail-safe rules:
    - Requires exactly one context for each evaluator:
      normative, readiness, operational_gate
    - Missing/blank identifiers => insufficient
    - Conflicting dataset_id/execution_id => incompatible
    - policy_fingerprint is optional and only compared when:
      - two or more contexts provide it
      - all provided values use the supported fingerprint semantic

    Absence of context is never interpreted as compatibility.
    This assessment never authorizes publication.
    """

    context_list = list(contexts)
    if not context_list:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=("No contexts provided.",),
        )

    if any(ctx is None for ctx in context_list):
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=("One or more contexts are missing (None).",),
        )

    if len(context_list) != 3:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=(
                "Expected exactly 3 contexts (normative, readiness, operational_gate).",
            ),
        )

    normalized: list[ShadowEvidenceContext] = [ctx for ctx in context_list if ctx is not None]

    evaluator_names = [ctx.evaluator_name for ctx in normalized]
    if set(evaluator_names) != _REQUIRED_EVALUATORS or len(set(evaluator_names)) != 3:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=(
                "Expected exactly one context for each evaluator: normative, readiness, operational_gate.",
            ),
        )

    dataset_ids = {_normalize_identifier(ctx.dataset_id) for ctx in normalized}
    execution_ids = {_normalize_identifier(ctx.execution_id) for ctx in normalized}

    if None in dataset_ids:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=("dataset_id missing for one or more contexts.",),
        )
    if None in execution_ids:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=("execution_id missing for one or more contexts.",),
        )

    if len(dataset_ids) != 1:
        return TraceabilityAssessment(
            status="incompatible",
            policy_identity_status="insufficient",
            reasons=("dataset_id differs between contexts.",),
        )

    if len(execution_ids) != 1:
        return TraceabilityAssessment(
            status="incompatible",
            policy_identity_status="insufficient",
            reasons=("execution_id differs between contexts.",),
        )

    fingerprints_by_evaluator: dict[str, str | None] = {
        ctx.evaluator_name: _normalize_policy_fingerprint(ctx.policy_fingerprint)
        for ctx in normalized
    }

    fingerprints_provided_by_evaluator = {
        evaluator: fingerprint
        for evaluator, fingerprint in fingerprints_by_evaluator.items()
        if fingerprint is not None
    }

    policy_identity_status: PolicyIdentityStatus = "not_proven"
    reasons: list[str] = []

    if len(fingerprints_provided_by_evaluator) == 0:
        reasons.append("policy_fingerprint not available for comparison.")
    else:
        non_sha256 = {
            evaluator: fingerprint
            for evaluator, fingerprint in fingerprints_provided_by_evaluator.items()
            if not fingerprint.startswith(_SUPPORTED_POLICY_FINGERPRINT_PREFIX)
        }
        invalid_sha256 = {
            evaluator: fingerprint
            for evaluator, fingerprint in fingerprints_provided_by_evaluator.items()
            if fingerprint.startswith(_SUPPORTED_POLICY_FINGERPRINT_PREFIX)
            and not _is_valid_sha256_fingerprint(fingerprint)
        }

        if non_sha256:
            policy_identity_status = "insufficient"
            reasons.append(
                "policy_fingerprint has unsupported semantic/format; identity not comparable."
            )
        elif invalid_sha256:
            policy_identity_status = "insufficient"
            reasons.append("policy_fingerprint sha256 format is invalid.")
        else:
            distinct = set(fingerprints_provided_by_evaluator.values())
            if len(distinct) > 1:
                policy_identity_status = "incompatible"
                reasons.append("policy_fingerprint differs between contexts.")
            else:
                if len(fingerprints_provided_by_evaluator) == 3:
                    policy_identity_status = "proven"
                else:
                    policy_identity_status = "not_proven"
                    if len(fingerprints_provided_by_evaluator) == 1:
                        reasons.append(
                            "policy_fingerprint available for a single context only."
                        )
                    else:
                        reasons.append("policy_fingerprint missing for one or more contexts.")

    return TraceabilityAssessment(
        status="compatible",
        policy_identity_status=policy_identity_status,
        reasons=tuple(reasons),
    )
