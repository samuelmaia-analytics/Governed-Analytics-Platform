from __future__ import annotations

from collections.abc import Callable

from src.publication_shadow.execution_identity_manifest import (
    ExecutionIdentityManifest,
    IdentityStatus,
    ManifestEvidenceEntry,
)


class DuplicateManifestEntryError(ValueError):
    pass


class ContradictoryManifestEntryError(ValueError):
    pass


def _require_identifier(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return stripped


class InMemoryExecutionManifestCollector:
    """In-memory collector for a single execution identity.

    This component is observability-only:
    - Stores only ManifestEvidenceEntry in memory.
    - Owns run_id and dataset_name for the *execution scope*.
    - Can build an ExecutionIdentityManifest v1 on demand.
    - Never produces IdentityStatus.PROVEN.

    Building a manifest in memory does not prove content identity.
    """

    __slots__ = (
        "_run_id",
        "_dataset_name",
        "_identity_frozen",
        "_entries_by_type",
        "_order",
    )

    def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
        self._identity_frozen = False
        self._run_id = _require_identifier(run_id, field_name="run_id")
        self._dataset_name = _require_identifier(dataset_name, field_name="dataset_name")
        self._entries_by_type: dict[str, ManifestEvidenceEntry] = {}
        self._order: list[str] = []
        self._identity_frozen = True

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"_run_id", "_dataset_name"} and getattr(
            self, "_identity_frozen", False
        ):
            raise AttributeError(f"{name} is immutable after initialization")
        super().__setattr__(name, value)

    @property
    def run_id(self) -> str | None:
        return self._run_id

    @property
    def dataset_name(self) -> str | None:
        return self._dataset_name

    @property
    def capture_manifest_entry_fn(self) -> Callable[[ManifestEvidenceEntry], None]:
        return self.capture

    def capture(self, entry: ManifestEvidenceEntry) -> None:
        if not isinstance(entry, ManifestEvidenceEntry):
            raise TypeError("entry must be a ManifestEvidenceEntry")
        if entry.identity_status == IdentityStatus.PROVEN:
            raise ValueError("IdentityStatus.PROVEN must not be accepted by the collector")

        evidence_type = entry.evidence_type
        prior = self._entries_by_type.get(evidence_type)
        if prior is None:
            self._entries_by_type[evidence_type] = entry
            self._order.append(evidence_type)
            return

        if prior == entry:
            raise DuplicateManifestEntryError(
                f"Duplicate entry for evidence_type '{evidence_type}'."
            )

        raise ContradictoryManifestEntryError(
            f"Contradictory entries for evidence_type '{evidence_type}'."
        )

    def snapshot_entries(self) -> tuple[ManifestEvidenceEntry, ...]:
        return tuple(self._entries_by_type[evidence_type] for evidence_type in self._order)

    def build_execution_identity_manifest_v1(self) -> ExecutionIdentityManifest:
        entries = self.snapshot_entries()
        return ExecutionIdentityManifest.from_entries(
            entries, run_id=self._run_id, dataset_name=self._dataset_name
        )
