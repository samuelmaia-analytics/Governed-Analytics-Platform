import inspect

import pytest

from src.publication_shadow.execution_identity_manifest import (
    ExecutionIdentityManifest,
    IdentityStatus,
    ManifestEvidenceEntry,
)
from src.publication_shadow.in_memory_manifest_collector import (
    ContradictoryManifestEntryError,
    DuplicateManifestEntryError,
    InMemoryExecutionManifestCollector,
)


def test_init_accepts_run_id() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    assert collector.run_id == "run-1"


def test_init_accepts_run_id_none() -> None:
    collector = InMemoryExecutionManifestCollector(run_id=None)
    assert collector.run_id is None


def test_dataset_name_none_preserved() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1", dataset_name=None)
    assert collector.dataset_name is None


@pytest.mark.parametrize("field", ["run_id", "dataset_name"])
def test_rejects_whitespace_only_identifiers(field: str) -> None:
    kwargs: dict[str, object] = {"run_id": "run-1", "dataset_name": "ds"}
    kwargs[field] = "   "
    with pytest.raises(ValueError):
        InMemoryExecutionManifestCollector(**kwargs)  # type: ignore[arg-type]


def test_capture_valid_entry() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry = ManifestEvidenceEntry(
        evidence_type="shadow_comparison",
        evidence_origin="publication_shadow",
        artifact_reference="/tmp/shadow.jsonl",
        identity_status=IdentityStatus.MISSING,
    )
    collector.capture(entry)
    assert collector.snapshot_entries() == (entry,)


def test_capture_multiple_evidence_types() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry_a = ManifestEvidenceEntry(evidence_type="a")
    entry_b = ManifestEvidenceEntry(evidence_type="b")
    collector.capture(entry_a)
    collector.capture(entry_b)
    assert collector.snapshot_entries() == (entry_a, entry_b)


def test_duplicate_exact_entry_is_not_silent() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry = ManifestEvidenceEntry(evidence_type="a", evidence_origin="o")
    collector.capture(entry)
    with pytest.raises(DuplicateManifestEntryError):
        collector.capture(entry)


def test_contradictory_entry_same_type_is_error() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry_1 = ManifestEvidenceEntry(evidence_type="a", evidence_origin="o1")
    entry_2 = ManifestEvidenceEntry(evidence_type="a", evidence_origin="o2")
    collector.capture(entry_1)
    with pytest.raises(ContradictoryManifestEntryError):
        collector.capture(entry_2)


def test_rejects_invalid_entry_type() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    with pytest.raises(TypeError):
        collector.capture(object())  # type: ignore[arg-type]


def test_snapshot_is_immutable_tuple() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry = ManifestEvidenceEntry(evidence_type="a")
    collector.capture(entry)

    snap = collector.snapshot_entries()
    assert isinstance(snap, tuple)

    snap2 = snap + (ManifestEvidenceEntry(evidence_type="b"),)
    assert snap2 != collector.snapshot_entries()


def test_identity_is_immutable() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1", dataset_name="ds")
    original_run_id = collector.run_id
    original_dataset_name = collector.dataset_name

    with pytest.raises(AttributeError):
        collector.run_id = "other"  # type: ignore[misc]
    assert collector.run_id == original_run_id
    assert collector.dataset_name == original_dataset_name

    with pytest.raises(AttributeError):
        collector.dataset_name = "other"  # type: ignore[misc]
    assert collector.run_id == original_run_id
    assert collector.dataset_name == original_dataset_name

    with pytest.raises(AttributeError):
        collector._run_id = "other"  # type: ignore[attr-defined]
    assert collector.run_id == original_run_id
    assert collector.dataset_name == original_dataset_name

    with pytest.raises(AttributeError):
        collector._dataset_name = "other"  # type: ignore[attr-defined]
    assert collector.run_id == original_run_id
    assert collector.dataset_name == original_dataset_name


def test_two_collectors_do_not_leak_entries() -> None:
    c1 = InMemoryExecutionManifestCollector(run_id="run-1")
    c2 = InMemoryExecutionManifestCollector(run_id="run-2")
    entry = ManifestEvidenceEntry(evidence_type="a")

    c1.capture(entry)
    assert c1.snapshot_entries() == (entry,)
    assert c2.snapshot_entries() == ()


def test_determinism_for_same_sequence() -> None:
    seq = [
        ManifestEvidenceEntry(evidence_type="a", evidence_origin="o"),
        ManifestEvidenceEntry(evidence_type="b"),
    ]

    c1 = InMemoryExecutionManifestCollector(run_id="run-1")
    c2 = InMemoryExecutionManifestCollector(run_id="run-1")

    for entry in seq:
        c1.capture(entry)
        c2.capture(entry)

    assert c1.snapshot_entries() == c2.snapshot_entries()


def test_build_manifest_v1_compatible() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1", dataset_name=None)
    entry = ManifestEvidenceEntry(evidence_type="a")
    collector.capture(entry)

    manifest = collector.build_execution_identity_manifest_v1()
    assert isinstance(manifest, ExecutionIdentityManifest)
    assert manifest.authorizes_publication is False
    assert manifest.run_id == "run-1"
    assert manifest.dataset_name is None
    assert manifest.entries == (entry,)


def test_no_proven_status() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry = ManifestEvidenceEntry(evidence_type="a")
    collector.capture(entry)

    manifest = collector.build_execution_identity_manifest_v1()
    assert all(item.identity_status != IdentityStatus.PROVEN for item in manifest.entries)


def test_no_io_open_called(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("open() must not be called")

    monkeypatch.setattr("builtins.open", _boom)

    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    collector.capture(ManifestEvidenceEntry(evidence_type="a"))
    _ = collector.snapshot_entries()
    _ = collector.build_execution_identity_manifest_v1()


def test_build_manifest_failure_does_not_mutate_entries(monkeypatch: pytest.MonkeyPatch) -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    entry = ManifestEvidenceEntry(evidence_type="a")
    collector.capture(entry)

    def _raise(*args: object, **kwargs: object) -> ExecutionIdentityManifest:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "src.publication_shadow.execution_identity_manifest.ExecutionIdentityManifest.from_entries",
        _raise,
    )

    snap_before = collector.snapshot_entries()
    with pytest.raises(RuntimeError):
        collector.build_execution_identity_manifest_v1()
    assert collector.snapshot_entries() == snap_before


def test_callback_signature_is_compatible() -> None:
    collector = InMemoryExecutionManifestCollector(run_id="run-1")
    fn = collector.capture_manifest_entry_fn
    assert callable(fn)
    signature = inspect.signature(fn)
    assert len(signature.parameters) == 1
