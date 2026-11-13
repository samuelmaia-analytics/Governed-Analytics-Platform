from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.publication_shadow.execution_identity_manifest import (
    EXECUTION_IDENTITY_MANIFEST_V1,
    ExecutionIdentityManifest,
    IdentityStatus,
    ManifestEvidenceEntry,
)


def test_proven_rejected_for_mutable_path_reference() -> None:
    with pytest.raises(ValueError, match="PROVEN is not supported"):
        ManifestEvidenceEntry(
            evidence_type="shadow_telemetry",
            evidence_origin="pipeline_monitor_step",
            artifact_reference="publication_shadow_comparisons.jsonl",
            identity_status=IdentityStatus.PROVEN,
        )


def test_proven_rejected_for_arbitrary_text_reference() -> None:
    with pytest.raises(ValueError, match="PROVEN is not supported"):
        ManifestEvidenceEntry(
            evidence_type="shadow_telemetry",
            evidence_origin="pipeline_monitor_step",
            artifact_reference="any-arbitrary-reference",
            identity_status=IdentityStatus.PROVEN,
        )


def test_proven_rejected_for_non_verifiable_content_reference() -> None:
    with pytest.raises(ValueError, match="PROVEN is not supported"):
        ManifestEvidenceEntry(
            evidence_type="shadow_telemetry",
            evidence_origin="pipeline_monitor_step",
            artifact_reference="sha256:deadbeef",
            identity_status=IdentityStatus.PROVEN,
        )


def test_invalid_identity_status_rejected_runtime() -> None:
    with pytest.raises(ValueError, match="identity_status must be an IdentityStatus"):
        ManifestEvidenceEntry(
            evidence_type="publication_decision",
            identity_status="missing",  # type: ignore[arg-type]
        )


def test_duplicate_evidence_type_rejected_even_if_identical() -> None:
    entry = ManifestEvidenceEntry(
        evidence_type="publication_decision",
        evidence_origin="producer_a",
        artifact_reference="decision.json",
        identity_status=IdentityStatus.MISSING,
    )

    with pytest.raises(ValueError, match="Duplicate entry"):
        ExecutionIdentityManifest(
            run_id=None,
            dataset_name=None,
            entries=(entry, entry),
        )


def test_contradictory_records_rejected() -> None:
    entry_a = ManifestEvidenceEntry(
        evidence_type="publication_decision",
        evidence_origin="producer_a",
        artifact_reference="decision_a.json",
        identity_status=IdentityStatus.MISSING,
    )
    entry_b = ManifestEvidenceEntry(
        evidence_type="publication_decision",
        evidence_origin="producer_a",
        artifact_reference="decision_b.json",
        identity_status=IdentityStatus.MISSING,
    )

    with pytest.raises(ValueError, match="Contradictory entries"):
        ExecutionIdentityManifest(
            run_id=None,
            dataset_name=None,
            entries=(entry_a, entry_b),
        )


def test_entries_must_be_manifest_evidence_entry_instances() -> None:
    with pytest.raises(TypeError, match="ManifestEvidenceEntry"):
        ExecutionIdentityManifest(
            run_id=None,
            dataset_name=None,
            entries=("not-an-entry",),  # type: ignore[arg-type]
        )


def test_legacy_artifact_allowed_without_identity() -> None:
    entry = ManifestEvidenceEntry(
        evidence_type="publication_decision",
        identity_status=IdentityStatus.LEGACY_UNVERIFIABLE,
    )

    manifest = ExecutionIdentityManifest(
        run_id=None,
        dataset_name=None,
        entries=(entry,),
    )

    assert manifest.authorizes_publication is False
    assert manifest.run_id is None
    assert manifest.dataset_name is None


def test_overwritten_artifact_allowed_without_identity() -> None:
    entry = ManifestEvidenceEntry(
        evidence_type="shadow_telemetry",
        identity_status=IdentityStatus.OVERWRITTEN_UNVERIFIABLE,
    )

    manifest = ExecutionIdentityManifest(
        run_id=None,
        dataset_name=None,
        entries=(entry,),
    )

    assert manifest.authorizes_publication is False


def test_schema_version_is_fixed() -> None:
    entry = ManifestEvidenceEntry(evidence_type="publication_decision")

    with pytest.raises(ValueError, match="schema_version must be"):
        ExecutionIdentityManifest(
            schema_version="v0",
            run_id=None,
            dataset_name=None,
            entries=(entry,),
        )


def test_entry_normalizes_evidence_type() -> None:
    entry = ManifestEvidenceEntry(evidence_type="  shadow_telemetry  ")
    assert entry.evidence_type == "shadow_telemetry"


def test_manifest_is_immutable_and_deterministic() -> None:
    entry = ManifestEvidenceEntry(
        evidence_type="shadow_telemetry",
        evidence_origin="pipeline_monitor_step",
        artifact_reference="publication_shadow_comparisons.jsonl",
        identity_status=IdentityStatus.MISSING,
    )

    manifest_a = ExecutionIdentityManifest.from_entries(
        [entry],
        run_id="run-1",
        dataset_name="dataset_a",
    )
    manifest_b = ExecutionIdentityManifest(
        schema_version=EXECUTION_IDENTITY_MANIFEST_V1,
        run_id="run-1",
        dataset_name="dataset_a",
        entries=(entry,),
    )

    assert manifest_a.authorizes_publication is False
    assert manifest_a == manifest_b
    assert hash(manifest_a) == hash(manifest_b)

    with pytest.raises(FrozenInstanceError):
        manifest_a.run_id = "run-2"  # type: ignore[misc]
