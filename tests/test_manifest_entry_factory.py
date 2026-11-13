from __future__ import annotations

import builtins
from dataclasses import FrozenInstanceError

import pytest

from src.publication_shadow.execution_identity_manifest import (
    EXECUTION_IDENTITY_MANIFEST_V1,
    ExecutionIdentityManifest,
    IdentityStatus,
)
from src.publication_shadow.manifest_entry_factory import (
    ArtifactMutability,
    EvidenceCondition,
    ManifestIdentityInput,
    build_execution_identity_manifest_v1,
    build_manifest_evidence_entry,
)


def test_factory_identity_complete_never_proven() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_shadow_comparisons",
        evidence_origin="pipeline",
        artifact_reference="publication_shadow_comparisons.jsonl",
        artifact_mutability=ArtifactMutability.APPEND_MULTI_RUN,
    )

    manifest = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
        entries=[entry],
    )

    assert isinstance(manifest, ExecutionIdentityManifest)
    assert manifest.schema_version == EXECUTION_IDENTITY_MANIFEST_V1
    assert manifest.run_id == "run-1"
    assert manifest.dataset_name == "dataset_a"
    assert manifest.entries == (entry,)
    assert entry.identity_status != IdentityStatus.PROVEN
    assert manifest.authorizes_publication is False


def test_factory_run_id_absent_is_preserved() -> None:
    entry = build_manifest_evidence_entry(evidence_type="publication_decision")
    manifest = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id=None, dataset_name="dataset_a"),
        entries=[entry],
    )

    assert manifest.run_id is None
    assert manifest.dataset_name == "dataset_a"


def test_factory_dataset_name_absent_is_preserved() -> None:
    entry = build_manifest_evidence_entry(evidence_type="schema_contract_results")
    manifest = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id="run-1", dataset_name=None),
        entries=[entry],
    )

    assert manifest.run_id == "run-1"
    assert manifest.dataset_name is None


def test_factory_evidence_origin_absent_is_preserved() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="governance_history",
        evidence_origin=None,
    )

    assert entry.evidence_origin is None


def test_factory_rejects_invalid_evidence_type() -> None:
    with pytest.raises(ValueError, match="evidence_type"):
        build_manifest_evidence_entry(evidence_type="   ")


def test_factory_overwrite_artifact_classified_as_overwritten_unverifiable() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_reference="publication_decision.json",
        artifact_mutability=ArtifactMutability.OVERWRITE,
    )

    assert entry.identity_status == IdentityStatus.OVERWRITTEN_UNVERIFIABLE


def test_factory_append_multi_run_is_not_auto_overwritten() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_shadow_comparisons",
        artifact_reference="publication_shadow_comparisons.jsonl",
        artifact_mutability=ArtifactMutability.APPEND_MULTI_RUN,
    )

    assert entry.identity_status == IdentityStatus.MISSING


def test_factory_legacy_evidence_is_legacy_unverifiable() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="legacy_artifact",
        condition=EvidenceCondition.LEGACY,
        artifact_reference="legacy.csv",
    )

    assert entry.identity_status == IdentityStatus.LEGACY_UNVERIFIABLE


def test_factory_explicit_overwritten_condition_is_overwritten_unverifiable() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="schema_contract_results",
        condition=EvidenceCondition.OVERWRITTEN,
        artifact_reference="schema_contract_results.csv",
    )

    assert entry.identity_status == IdentityStatus.OVERWRITTEN_UNVERIFIABLE


def test_factory_reference_absent_is_preserved() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="quality_checks",
        artifact_reference=None,
    )

    assert entry.artifact_reference is None
    assert entry.identity_status == IdentityStatus.MISSING


def test_factory_rejects_whitespace_only_identifiers() -> None:
    with pytest.raises(ValueError, match="run_id must not be empty"):
        build_execution_identity_manifest_v1(
            identity=ManifestIdentityInput(run_id="   ", dataset_name="dataset_a"),
            entries=[build_manifest_evidence_entry(evidence_type="x")],
        )

    with pytest.raises(ValueError, match="dataset_name must not be empty"):
        build_execution_identity_manifest_v1(
            identity=ManifestIdentityInput(run_id="run-1", dataset_name="   "),
            entries=[build_manifest_evidence_entry(evidence_type="x")],
        )

    with pytest.raises(ValueError, match="evidence_origin must not be empty"):
        build_manifest_evidence_entry(
            evidence_type="x",
            evidence_origin="   ",
        )


def test_factory_explicit_contradictory_condition_is_preserved() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_shadow_comparisons",
        condition=EvidenceCondition.CONTRADICTORY,
        artifact_reference="publication_shadow_comparisons.jsonl",
    )

    assert entry.identity_status == IdentityStatus.CONTRADICTORY


def test_manifest_rejects_duplicate_entry_by_evidence_type() -> None:
    entry = build_manifest_evidence_entry(evidence_type="publication_decision")

    with pytest.raises(ValueError, match="Duplicate entry"):
        build_execution_identity_manifest_v1(
            identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
            entries=[entry, entry],
        )


def test_manifest_rejects_contradictory_entries_by_evidence_type() -> None:
    entry_a = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_reference="publication_decision.json",
    )
    entry_b = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_reference="publication_decision_other.json",
    )

    with pytest.raises(ValueError, match="Contradictory entries"):
        build_execution_identity_manifest_v1(
            identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
            entries=[entry_a, entry_b],
        )


def test_factory_is_deterministic() -> None:
    a1 = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_reference="publication_decision.json",
        artifact_mutability=ArtifactMutability.OVERWRITE,
    )
    a2 = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_reference="publication_decision.json",
        artifact_mutability=ArtifactMutability.OVERWRITE,
    )

    assert a1 == a2
    assert hash(a1) == hash(a2)

    m1 = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
        entries=[a1],
    )
    m2 = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
        entries=[a2],
    )

    assert m1 == m2
    assert hash(m1) == hash(m2)


def test_factory_returns_immutable_objects() -> None:
    entry = build_manifest_evidence_entry(evidence_type="publication_decision")

    with pytest.raises(FrozenInstanceError):
        entry.evidence_type = "changed"  # type: ignore[misc]

    identity = ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a")
    with pytest.raises(FrozenInstanceError):
        identity.run_id = "changed"  # type: ignore[misc]


def test_factory_does_not_perform_io() -> None:
    original_open = builtins.open

    def _raise(*args: object, **kwargs: object) -> object:  # noqa: ANN401
        raise AssertionError("unexpected IO")

    builtins.open = _raise  # type: ignore[assignment]
    try:
        entry = build_manifest_evidence_entry(evidence_type="publication_decision")
        manifest = build_execution_identity_manifest_v1(
            identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
            entries=[entry],
        )
        assert manifest.authorizes_publication is False
    finally:
        builtins.open = original_open


def test_factory_rejects_invalid_artifact_mutability_runtime() -> None:
    with pytest.raises(ValueError, match="artifact_mutability must be an ArtifactMutability"):
        build_manifest_evidence_entry(
            evidence_type="publication_decision",
            artifact_mutability="overwrite",  # type: ignore[arg-type]
        )


def test_factory_rejects_invalid_evidence_condition_runtime() -> None:
    with pytest.raises(ValueError, match="condition must be an EvidenceCondition"):
        build_manifest_evidence_entry(
            evidence_type="publication_decision",
            condition="present",  # type: ignore[arg-type]
        )


def test_factory_contradictory_overwrite_preserves_contradictory() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_mutability=ArtifactMutability.OVERWRITE,
        condition=EvidenceCondition.CONTRADICTORY,
        artifact_reference="publication_decision.json",
    )

    assert entry.identity_status == IdentityStatus.CONTRADICTORY


def test_factory_legacy_overwrite_preserves_legacy_unverifiable() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="legacy_artifact",
        artifact_mutability=ArtifactMutability.OVERWRITE,
        condition=EvidenceCondition.LEGACY,
        artifact_reference="legacy.csv",
    )

    assert entry.identity_status == IdentityStatus.LEGACY_UNVERIFIABLE


def test_factory_present_overwrite_is_overwritten_unverifiable() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_mutability=ArtifactMutability.OVERWRITE,
        condition=EvidenceCondition.PRESENT,
        artifact_reference="publication_decision.json",
    )

    assert entry.identity_status == IdentityStatus.OVERWRITTEN_UNVERIFIABLE


def test_factory_missing_overwrite_is_missing() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_decision",
        artifact_mutability=ArtifactMutability.OVERWRITE,
        condition=EvidenceCondition.MISSING,
        artifact_reference="publication_decision.json",
    )

    assert entry.identity_status == IdentityStatus.MISSING


def test_factory_append_multi_run_present_is_missing() -> None:
    entry = build_manifest_evidence_entry(
        evidence_type="publication_shadow_comparisons",
        artifact_mutability=ArtifactMutability.APPEND_MULTI_RUN,
        condition=EvidenceCondition.PRESENT,
        artifact_reference="publication_shadow_comparisons.jsonl",
    )

    assert entry.identity_status == IdentityStatus.MISSING


def test_factory_never_produces_proven_for_valid_enum_combinations() -> None:
    for mutability in ArtifactMutability:
        for condition in EvidenceCondition:
            if mutability == ArtifactMutability.APPEND_MULTI_RUN and condition == EvidenceCondition.OVERWRITTEN:
                continue
            entry = build_manifest_evidence_entry(
                evidence_type="x",
                artifact_mutability=mutability,
                condition=condition,
            )
            assert entry.identity_status != IdentityStatus.PROVEN
            assert entry.identity_status in {
                IdentityStatus.MISSING,
                IdentityStatus.CONTRADICTORY,
                IdentityStatus.LEGACY_UNVERIFIABLE,
                IdentityStatus.OVERWRITTEN_UNVERIFIABLE,
            }


def test_factory_never_authorizes_publication() -> None:
    entry = build_manifest_evidence_entry(evidence_type="publication_decision")
    manifest = build_execution_identity_manifest_v1(
        identity=ManifestIdentityInput(run_id="run-1", dataset_name="dataset_a"),
        entries=[entry],
    )
    assert manifest.authorizes_publication is False
