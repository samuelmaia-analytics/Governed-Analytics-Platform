from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

EXECUTION_IDENTITY_MANIFEST_V1 = "execution_identity_manifest_v1"


class IdentityStatus(StrEnum):
    PROVEN = "proven"
    MISSING = "missing"
    CONTRADICTORY = "contradictory"
    LEGACY_UNVERIFIABLE = "legacy_unverifiable"
    OVERWRITTEN_UNVERIFIABLE = "overwritten_unverifiable"


@dataclass(frozen=True)
class ManifestEvidenceEntry:
    """A single evidence link declared by a producer.

    This is an observability-only contract. It must not infer missing identity
    fields or promote incomplete declarations to proven identity.

    NOTE: In v1, IdentityStatus.PROVEN is intentionally rejected because this
    contract cannot validate immutability or content identity for
    artifact_reference without filesystem/network verification.
    """

    evidence_type: str
    evidence_origin: str | None = None
    artifact_reference: str | None = None
    identity_status: IdentityStatus = IdentityStatus.MISSING

    def __post_init__(self) -> None:
        if not isinstance(self.identity_status, IdentityStatus):
            raise ValueError("identity_status must be an IdentityStatus")
        if self.identity_status == IdentityStatus.PROVEN:
            raise ValueError(
                "IdentityStatus.PROVEN is not supported in execution_identity_manifest_v1"
            )

        evidence_type = _require_non_empty(self.evidence_type, field_name="evidence_type")
        object.__setattr__(self, "evidence_type", evidence_type)
        object.__setattr__(self, "evidence_origin", _normalize_non_empty(self.evidence_origin))
        object.__setattr__(
            self, "artifact_reference", _normalize_non_empty(self.artifact_reference)
        )


@dataclass(frozen=True)
class ExecutionIdentityManifest:
    """ExecutionIdentityManifest v1.

    Represents explicit identity links (run_id + dataset_name) declared by a
    producer for a set of evidence artifacts.

    Fail-safe rules:
    - IdentityStatus.PROVEN is not supported in v1.
      This version cannot prove immutability or content identity for
      artifact_reference without filesystem/network verification.
    """

    schema_version: str = EXECUTION_IDENTITY_MANIFEST_V1
    run_id: str | None = None
    dataset_name: str | None = None
    entries: tuple[ManifestEvidenceEntry, ...] = ()

    @property
    def authorizes_publication(self) -> bool:
        return False

    def __post_init__(self) -> None:
        if self.schema_version != EXECUTION_IDENTITY_MANIFEST_V1:
            raise ValueError("schema_version must be 'execution_identity_manifest_v1'.")

        object.__setattr__(self, "run_id", _normalize_non_empty(self.run_id))
        object.__setattr__(self, "dataset_name", _normalize_non_empty(self.dataset_name))

        if not isinstance(self.entries, tuple):
            object.__setattr__(self, "entries", tuple(self.entries))

        for entry in self.entries:
            if not isinstance(entry, ManifestEvidenceEntry):
                raise TypeError("entries must contain only ManifestEvidenceEntry instances")

        for entry in self.entries:
            if entry.identity_status == IdentityStatus.PROVEN:
                raise ValueError(
                    "IdentityStatus.PROVEN is not supported in execution_identity_manifest_v1"
                )

        seen_by_type: dict[str, ManifestEvidenceEntry] = {}
        for entry in self.entries:
            prior = seen_by_type.get(entry.evidence_type)
            if prior is None:
                seen_by_type[entry.evidence_type] = entry
                continue
            if entry != prior:
                raise ValueError(
                    f"Contradictory entries for evidence_type '{entry.evidence_type}'."
                )
            raise ValueError(f"Duplicate entry for evidence_type '{entry.evidence_type}'.")

    @classmethod
    def from_entries(
        cls,
        entries: Iterable[ManifestEvidenceEntry],
        *,
        run_id: str | None,
        dataset_name: str | None,
    ) -> "ExecutionIdentityManifest":
        return cls(run_id=run_id, dataset_name=dataset_name, entries=tuple(entries))


def _normalize_non_empty(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected string identifier")
    stripped = value.strip()
    return stripped if stripped else None


def _require_non_empty(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return stripped
