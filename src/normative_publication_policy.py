from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from src.publication_gate import (
    FreshnessStatus,
    PublicationDecision,
    SchemaContractStatus,
)

SupportedBlockingCondition = Literal[
    "critical_rule_failures_gt_0",
    "schema_contract_failed",
    "sensitive_data_without_protection",
    "privacy_risk_score_gt_maximum",
    "freshness_stale",
]

_SCORE_MIN = 0
_SCORE_MAX = 100

_FRESHNESS_VALUES: set[str] = {"fresh", "warning", "stale"}
_PUBLICATION_DECISIONS: set[str] = {"Approved", "Needs Review", "Blocked"}
_SUPPORTED_BLOCKING_CONDITIONS: set[str] = {
    "critical_rule_failures_gt_0",
    "schema_contract_failed",
    "sensitive_data_without_protection",
    "privacy_risk_score_gt_maximum",
    "freshness_stale",
}

_POLICY_KEYS = {
    "minimum_quality_score",
    "maximum_privacy_risk_score",
    "freshness_requirement",
    "contract_required",
    "blocking_conditions",
}

_CRITERIA_KEYS = {
    "required_status",
    "quality_threshold",
    "privacy_threshold",
    "freshness_threshold",
    "failed_checks_threshold",
}


@dataclass(frozen=True)
class NormativePublicationPolicy:
    minimum_quality_score: int
    maximum_privacy_risk_score: int
    freshness_requirement: FreshnessStatus
    contract_required: bool
    blocking_conditions: tuple[SupportedBlockingCondition, ...]

    required_status: PublicationDecision | None = None
    quality_threshold: str | None = None
    privacy_threshold: str | None = None
    freshness_threshold: FreshnessStatus | None = None
    failed_checks_threshold: int | None = None

    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormativeEvidence:
    data_quality_score: int | None = None
    privacy_risk_score: int | None = None
    freshness_status: FreshnessStatus | None = None
    schema_contract_status: SchemaContractStatus | None = None
    critical_rule_failures: int | None = None
    has_sensitive_data_without_protection: bool | None = None
    failed_checks_count: int | None = None


@dataclass(frozen=True)
class NormativeDecision:
    authorized: bool
    decision: PublicationDecision
    reasons: tuple[str, ...]
    policy_warnings: tuple[str, ...] = ()


class PolicyValidationError(ValueError):
    """Erro controlado para problemas de validação de política (contrato)."""


class EvidenceValidationError(ValueError):
    """Erro controlado para problemas de validação de evidências (inputs)."""


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_mapping(value: Any, *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PolicyValidationError(
            f"Campo '{field}' deve ser um mapeamento YAML (dict)."
        )
    return value


def _reject_unknown_keys(mapping: dict[str, Any], *, allowed: set[str], field: str) -> None:
    unknown = sorted(set(mapping.keys()) - allowed)
    if unknown:
        raise PolicyValidationError(
            f"Campos desconhecidos em '{field}': {', '.join(unknown)}."
        )


def _require_bool(value: Any, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise PolicyValidationError(f"Campo '{field}' deve ser booleano.")
    return value


def _require_int(value: Any, *, field: str) -> int:
    if not _is_int_not_bool(value):
        raise PolicyValidationError(f"Campo '{field}' deve ser inteiro.")
    return value


def _require_non_negative_int(value: Any, *, field: str) -> int:
    parsed = _require_int(value, field=field)
    if parsed < 0:
        raise PolicyValidationError(f"Campo '{field}' deve ser >= 0.")
    return parsed


def _require_score(value: Any, *, field: str) -> int:
    parsed = _require_int(value, field=field)
    if parsed < _SCORE_MIN or parsed > _SCORE_MAX:
        raise PolicyValidationError(
            f"Campo '{field}' deve estar no intervalo {_SCORE_MIN}–{_SCORE_MAX}."
        )
    return parsed


def _require_freshness(value: Any, *, field: str) -> FreshnessStatus:
    if value not in _FRESHNESS_VALUES:
        raise PolicyValidationError(
            f"Campo '{field}' deve ser um de: fresh, warning, stale."
        )
    return value


def _require_publication_decision(value: Any, *, field: str) -> PublicationDecision:
    if value not in _PUBLICATION_DECISIONS:
        raise PolicyValidationError(
            f"Campo '{field}' deve ser um de: Approved, Needs Review, Blocked."
        )
    return value


def _parse_supported_blocking_conditions(
    value: Any,
    *,
    required: bool,
) -> tuple[SupportedBlockingCondition, ...]:
    if value is None:
        if required:
            raise PolicyValidationError(
                "Campo 'blocking_conditions' e obrigatorio para esta politica."
            )
        return ()

    if not isinstance(value, list):
        raise PolicyValidationError("Campo 'blocking_conditions' deve ser uma lista.")

    normalized: list[SupportedBlockingCondition] = []
    for item in value:
        if not isinstance(item, str):
            raise PolicyValidationError(
                "Itens de 'blocking_conditions' devem ser strings."
            )
        if item not in _SUPPORTED_BLOCKING_CONDITIONS:
            raise PolicyValidationError(
                "Blocking condition desconhecida/nao suportada: "
                f"{item}."
            )
        normalized.append(item)  # type: ignore[assignment]

    if required and not normalized:
        raise PolicyValidationError(
            "Campo 'blocking_conditions' nao pode ser vazio para esta politica."
        )

    return tuple(normalized)


def _parse_threshold_expr(expr: str) -> tuple[str, int]:
    for op in (">=", "<=", "==", ">", "<"):
        if expr.startswith(op):
            raw = expr[len(op) :].strip()
            if raw == "":
                raise PolicyValidationError(f"Threshold invalido: {expr!r}.")
            try:
                return op, int(raw)
            except ValueError as exc:
                raise PolicyValidationError(f"Threshold invalido: {expr!r}.") from exc
    raise PolicyValidationError(f"Threshold invalido: {expr!r}.")


def _validate_threshold_expr(
    expr: Any,
    *,
    field: str,
    allow_ops: set[str],
    require_score_range: bool,
) -> None:
    if not isinstance(expr, str):
        raise PolicyValidationError(
            f"Campo '{field}' deve ser string."
        )

    op, target = _parse_threshold_expr(expr)
    if op not in allow_ops:
        allowed = ", ".join(sorted(allow_ops))
        raise PolicyValidationError(
            f"Operador invalido em '{field}': {op}. Permitidos: {allowed}."
        )
    if require_score_range and (target < _SCORE_MIN or target > _SCORE_MAX):
        raise PolicyValidationError(
            f"Threshold em '{field}' deve estar no intervalo {_SCORE_MIN}–{_SCORE_MAX}."
        )


def _eval_threshold(value: int, expr: str) -> bool:
    op, target = _parse_threshold_expr(expr)
    if op == ">=":
        return value >= target
    if op == "<=":
        return value <= target
    if op == "==":
        return value == target
    if op == ">":
        return value > target
    if op == "<":
        return value < target
    raise PolicyValidationError(f"Operador nao suportado: {op}.")


def _validate_policy(policy: NormativePublicationPolicy) -> None:
    if not _is_int_not_bool(policy.minimum_quality_score):
        raise PolicyValidationError(
            "minimum_quality_score deve ser inteiro."
        )

    if policy.minimum_quality_score < _SCORE_MIN or policy.minimum_quality_score > _SCORE_MAX:
        raise PolicyValidationError(
            "minimum_quality_score fora do intervalo 0–100."
        )

    if not _is_int_not_bool(policy.maximum_privacy_risk_score):
        raise PolicyValidationError(
            "maximum_privacy_risk_score deve ser inteiro."
        )

    if policy.maximum_privacy_risk_score < _SCORE_MIN or policy.maximum_privacy_risk_score > _SCORE_MAX:
        raise PolicyValidationError(
            "maximum_privacy_risk_score fora do intervalo 0–100."
        )

    if policy.freshness_requirement not in _FRESHNESS_VALUES:
        raise PolicyValidationError(
            "freshness_requirement invalido; deve ser fresh, warning ou stale."
        )

    if not isinstance(policy.contract_required, bool):
        raise PolicyValidationError(
            "contract_required deve ser booleano."
        )

    if not isinstance(policy.blocking_conditions, tuple):
        raise PolicyValidationError(
            "blocking_conditions deve ser uma tupla de strings suportadas."
        )

    if not policy.blocking_conditions:
        raise PolicyValidationError(
            "blocking_conditions vazio/ausente: politica nao pode aprovar por omissao."
        )

    for condition in policy.blocking_conditions:
        if not isinstance(condition, str) or condition not in _SUPPORTED_BLOCKING_CONDITIONS:
            raise PolicyValidationError(
                "Blocking condition desconhecida/nao suportada: "
                f"{condition}."
            )

    if policy.required_status is not None:
        if policy.required_status not in _PUBLICATION_DECISIONS:
            raise PolicyValidationError(
                "publication_criteria.required_status invalido."
            )
        if policy.required_status != "Approved":
            raise PolicyValidationError(
                "publication_criteria.required_status diferente de Approved nao e suportado nesta versao."
            )

    if policy.quality_threshold is not None:
        _validate_threshold_expr(
            policy.quality_threshold,
            field="publication_criteria.quality_threshold",
            allow_ops={">=", ">"},
            require_score_range=True,
        )

    if policy.privacy_threshold is not None:
        _validate_threshold_expr(
            policy.privacy_threshold,
            field="publication_criteria.privacy_threshold",
            allow_ops={"<=", "<"},
            require_score_range=True,
        )

    if policy.failed_checks_threshold is not None:
        if not _is_int_not_bool(policy.failed_checks_threshold):
            raise PolicyValidationError(
                "publication_criteria.failed_checks_threshold deve ser inteiro."
            )
        if policy.failed_checks_threshold < 0:
            raise PolicyValidationError(
                "publication_criteria.failed_checks_threshold deve ser >= 0."
            )

    if policy.freshness_threshold is not None:
        if policy.freshness_threshold not in _FRESHNESS_VALUES:
            raise PolicyValidationError(
                "publication_criteria.freshness_threshold invalido."
            )
        if policy.freshness_threshold != policy.freshness_requirement:
            raise PolicyValidationError(
                "freshness_threshold difere de freshness_requirement; politica inconsistente."
            )


def _validate_evidence_value(value: Any, *, field: str) -> int:
    if not _is_int_not_bool(value):
        raise EvidenceValidationError(f"Campo '{field}' deve ser inteiro.")
    return value


def _validate_score_evidence(value: Any, *, field: str) -> int:
    parsed = _validate_evidence_value(value, field=field)
    if parsed < _SCORE_MIN or parsed > _SCORE_MAX:
        raise EvidenceValidationError(
            f"Campo '{field}' deve estar no intervalo {_SCORE_MIN}–{_SCORE_MAX}."
        )
    return parsed


def _validate_non_negative_evidence(value: Any, *, field: str) -> int:
    parsed = _validate_evidence_value(value, field=field)
    if parsed < 0:
        raise EvidenceValidationError(f"Campo '{field}' deve ser >= 0.")
    return parsed


def load_policy_from_contract_dict(contract: dict[str, Any]) -> NormativePublicationPolicy:
    policy_dict = _require_mapping(
        contract.get("publication_policy"),
        field="publication_policy",
    )
    _reject_unknown_keys(policy_dict, allowed=_POLICY_KEYS, field="publication_policy")

    minimum_quality_score = _require_score(
        policy_dict.get("minimum_quality_score"),
        field="publication_policy.minimum_quality_score",
    )
    maximum_privacy_risk_score = _require_score(
        policy_dict.get("maximum_privacy_risk_score"),
        field="publication_policy.maximum_privacy_risk_score",
    )
    freshness_requirement = _require_freshness(
        policy_dict.get("freshness_requirement"),
        field="publication_policy.freshness_requirement",
    )
    contract_required = _require_bool(
        policy_dict.get("contract_required"),
        field="publication_policy.contract_required",
    )
    blocking_conditions = _parse_supported_blocking_conditions(
        policy_dict.get("blocking_conditions"),
        required=True,
    )

    criteria_dict: dict[str, Any] | None = None
    if "publication_criteria" in contract and contract.get("publication_criteria") is not None:
        criteria_dict = _require_mapping(
            contract.get("publication_criteria"),
            field="publication_criteria",
        )
        _reject_unknown_keys(criteria_dict, allowed=_CRITERIA_KEYS, field="publication_criteria")

    required_status: PublicationDecision | None = None
    quality_threshold: str | None = None
    privacy_threshold: str | None = None
    freshness_threshold: FreshnessStatus | None = None
    failed_checks_threshold: int | None = None

    if criteria_dict is not None:
        if "required_status" in criteria_dict:
            required_status = _require_publication_decision(
                criteria_dict.get("required_status"),
                field="publication_criteria.required_status",
            )

        quality_threshold = criteria_dict.get("quality_threshold")
        if quality_threshold is not None:
            _validate_threshold_expr(
                quality_threshold,
                field="publication_criteria.quality_threshold",
                allow_ops={">=", ">"},
                require_score_range=True,
            )

        privacy_threshold = criteria_dict.get("privacy_threshold")
        if privacy_threshold is not None:
            _validate_threshold_expr(
                privacy_threshold,
                field="publication_criteria.privacy_threshold",
                allow_ops={"<=", "<"},
                require_score_range=True,
            )

        if "freshness_threshold" in criteria_dict:
            freshness_threshold = _require_freshness(
                criteria_dict.get("freshness_threshold"),
                field="publication_criteria.freshness_threshold",
            )

        if "failed_checks_threshold" in criteria_dict and criteria_dict.get(
            "failed_checks_threshold"
        ) is not None:
            failed_checks_threshold = _require_non_negative_int(
                criteria_dict.get("failed_checks_threshold"),
                field="publication_criteria.failed_checks_threshold",
            )

    warnings: list[str] = []
    if freshness_threshold is not None and freshness_threshold != freshness_requirement:
        warnings.append(
            "freshness_threshold difere de freshness_requirement no contrato."
        )

    policy = NormativePublicationPolicy(
        minimum_quality_score=minimum_quality_score,
        maximum_privacy_risk_score=maximum_privacy_risk_score,
        freshness_requirement=freshness_requirement,
        contract_required=contract_required,
        blocking_conditions=blocking_conditions,
        required_status=required_status,
        quality_threshold=quality_threshold,
        privacy_threshold=privacy_threshold,
        freshness_threshold=freshness_threshold,
        failed_checks_threshold=failed_checks_threshold,
        warnings=tuple(warnings),
    )
    _validate_policy(policy)
    return policy


def load_policy_from_contract_file(contract_path: Path) -> NormativePublicationPolicy:
    contract_text = contract_path.read_text(encoding="utf-8")
    try:
        parsed = yaml.safe_load(contract_text)
    except yaml.YAMLError as exc:
        raise PolicyValidationError(
            f"Erro ao interpretar YAML do contrato: {contract_path}."
        ) from exc

    if not isinstance(parsed, dict):
        raise PolicyValidationError(
            "Contrato YAML deve ser um documento de mapeamento (dict)."
        )
    return load_policy_from_contract_dict(parsed)


def load_policy_for_dataset(
    dataset_name: str,
    *,
    contracts_dir: Path | None = None,
) -> NormativePublicationPolicy:
    base_dir = contracts_dir or Path("contracts")
    contract_filename = (
        dataset_name
        if dataset_name.endswith(".contract.yml")
        else f"{dataset_name}.contract.yml"
    )

    matches = list(base_dir.rglob(contract_filename))
    if not matches:
        raise FileNotFoundError(
            f"Nao foi encontrado contrato '{contract_filename}' em {base_dir}."
        )
    if len(matches) > 1:
        raise PolicyValidationError(
            f"Mais de um contrato encontrado para '{dataset_name}': {matches}"
        )

    return load_policy_from_contract_file(matches[0])


def evaluate_normative_policy(
    policy: NormativePublicationPolicy,
    evidence: NormativeEvidence,
) -> NormativeDecision:
    """Avalia a política normativa de publicação (contrato YAML).

    Limitacao conhecida: freshness e avaliado apenas por um `FreshnessStatus` já
    calculado externamente. Nao há inferencia temporal (timestamps) aqui.
    """

    _validate_policy(policy)

    reasons: list[str] = []

    missing: list[str] = []
    if evidence.data_quality_score is None:
        missing.append("data_quality_score")
    if evidence.privacy_risk_score is None:
        missing.append("privacy_risk_score")
    if evidence.freshness_status is None:
        missing.append("freshness_status")
    if evidence.schema_contract_status is None:
        missing.append("schema_contract_status")
    if evidence.critical_rule_failures is None:
        missing.append("critical_rule_failures")
    if evidence.has_sensitive_data_without_protection is None:
        missing.append("has_sensitive_data_without_protection")

    if policy.failed_checks_threshold is not None and evidence.failed_checks_count is None:
        missing.append("failed_checks_count")

    if missing:
        reasons.append(
            "Evidencias ausentes para avaliacao normativa (fail-safe): "
            + ", ".join(sorted(set(missing)))
            + "."
        )
        return NormativeDecision(
            authorized=False,
            decision="Blocked",
            reasons=tuple(reasons),
            policy_warnings=policy.warnings,
        )

    data_quality_score = _validate_score_evidence(
        evidence.data_quality_score,
        field="data_quality_score",
    )
    privacy_risk_score = _validate_score_evidence(
        evidence.privacy_risk_score,
        field="privacy_risk_score",
    )

    freshness_status = evidence.freshness_status
    if freshness_status not in _FRESHNESS_VALUES:
        raise EvidenceValidationError(
            "Campo 'freshness_status' deve ser um de: fresh, warning, stale."
        )

    schema_contract_status = evidence.schema_contract_status
    if schema_contract_status not in ("passed", "failed"):
        raise EvidenceValidationError(
            "Campo 'schema_contract_status' deve ser um de: passed, failed."
        )

    critical_rule_failures = _validate_non_negative_evidence(
        evidence.critical_rule_failures,
        field="critical_rule_failures",
    )

    has_sensitive = evidence.has_sensitive_data_without_protection
    if not isinstance(has_sensitive, bool):
        raise EvidenceValidationError(
            "Campo 'has_sensitive_data_without_protection' deve ser booleano."
        )

    failed_checks_count: int | None
    if evidence.failed_checks_count is None:
        failed_checks_count = None
    else:
        failed_checks_count = _validate_non_negative_evidence(
            evidence.failed_checks_count,
            field="failed_checks_count",
        )

    blocking_hits: list[str] = []
    for cond in policy.blocking_conditions:
        if cond == "critical_rule_failures_gt_0" and critical_rule_failures > 0:
            blocking_hits.append(cond)
        elif cond == "schema_contract_failed" and schema_contract_status == "failed":
            blocking_hits.append(cond)
        elif cond == "sensitive_data_without_protection" and has_sensitive:
            blocking_hits.append(cond)
        elif (
            cond == "privacy_risk_score_gt_maximum"
            and privacy_risk_score > policy.maximum_privacy_risk_score
        ):
            blocking_hits.append(cond)
        elif cond == "freshness_stale" and freshness_status == "stale":
            blocking_hits.append(cond)

    if blocking_hits:
        reasons.append(
            "Bloqueado por blocking_conditions: "
            + ", ".join(sorted(set(blocking_hits)))
            + "."
        )
        return NormativeDecision(
            authorized=False,
            decision="Blocked",
            reasons=tuple(reasons),
            policy_warnings=policy.warnings,
        )

    # Thresholds base da policy
    if data_quality_score < policy.minimum_quality_score:
        reasons.append(
            f"data_quality_score {data_quality_score} < minimum_quality_score {policy.minimum_quality_score}."
        )

    if privacy_risk_score > policy.maximum_privacy_risk_score:
        reasons.append(
            f"privacy_risk_score {privacy_risk_score} > maximum_privacy_risk_score {policy.maximum_privacy_risk_score}."
        )

    if freshness_status != policy.freshness_requirement:
        reasons.append(
            f"freshness_status {freshness_status} != freshness_requirement {policy.freshness_requirement}."
        )

    if policy.contract_required and schema_contract_status != "passed":
        reasons.append("contract_required=true exige schema_contract_status=passed.")

    # publication_criteria (quando presentes)
    if policy.quality_threshold is not None and not _eval_threshold(
        data_quality_score,
        policy.quality_threshold,
    ):
        reasons.append(
            f"data_quality_score {data_quality_score} nao satisfaz quality_threshold {policy.quality_threshold}."
        )

    if policy.privacy_threshold is not None and not _eval_threshold(
        privacy_risk_score,
        policy.privacy_threshold,
    ):
        reasons.append(
            f"privacy_risk_score {privacy_risk_score} nao satisfaz privacy_threshold {policy.privacy_threshold}."
        )

    if policy.failed_checks_threshold is not None:
        if failed_checks_count is None:
            reasons.append("failed_checks_count ausente (fail-safe).")
        elif failed_checks_count > policy.failed_checks_threshold:
            reasons.append(
                f"failed_checks_count {failed_checks_count} > failed_checks_threshold {policy.failed_checks_threshold}."
            )

    if reasons:
        return NormativeDecision(
            authorized=False,
            decision="Blocked",
            reasons=tuple(reasons),
            policy_warnings=policy.warnings,
        )

    return NormativeDecision(
        authorized=True,
        decision="Approved",
        reasons=("Aprovado pela politica normativa (contrato YAML).",),
        policy_warnings=policy.warnings,
    )