from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ObservationStatus(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    SUCCEEDED = "succeeded"
    PARTIALLY_FAILED = "partially_failed"
    FAILED = "failed"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True, slots=True)
class ShadowManifestCaptureDiagnostics:
    writer_status: ObservationStatus
    capture_status: ObservationStatus
    delivery_status: ObservationStatus

    writer_attempted: bool
    capture_enabled: bool
    consumer_present: bool
    skipped_empty_snapshot: bool

    snapshot_entries_count: int

    evidence_build_attempted: int
    evidence_build_succeeded: int
    evidence_build_failed: int

    entry_capture_attempted: int
    entry_capture_succeeded: int
    entry_capture_failed: int

    manifest_build_attempted: int
    manifest_build_succeeded: int
    manifest_build_failed: int

    consumer_call_attempted: int
    consumer_call_succeeded: int
    consumer_call_failed: int


    def __post_init__(self) -> None:
        def ensure_non_negative_int(name: str, value: int) -> None:
            if not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
            if value < 0:
                raise ValueError(f"{name} must be >= 0")

        def validate_group(
            prefix: str,
            attempted: int,
            succeeded: int,
            failed: int,
        ) -> None:
            ensure_non_negative_int(f"{prefix}_attempted", attempted)
            ensure_non_negative_int(f"{prefix}_succeeded", succeeded)
            ensure_non_negative_int(f"{prefix}_failed", failed)
            if succeeded > attempted:
                raise ValueError(
                    f"{prefix}_succeeded must be <= {prefix}_attempted"
                )
            if failed > attempted:
                raise ValueError(
                    f"{prefix}_failed must be <= {prefix}_attempted"
                )
            if succeeded + failed > attempted:
                raise ValueError(
                    f"{prefix}_succeeded + {prefix}_failed must be <= {prefix}_attempted"
                )

        ensure_non_negative_int("snapshot_entries_count", self.snapshot_entries_count)

        validate_group(
            "evidence_build",
            self.evidence_build_attempted,
            self.evidence_build_succeeded,
            self.evidence_build_failed,
        )
        validate_group(
            "entry_capture",
            self.entry_capture_attempted,
            self.entry_capture_succeeded,
            self.entry_capture_failed,
        )
        validate_group(
            "manifest_build",
            self.manifest_build_attempted,
            self.manifest_build_succeeded,
            self.manifest_build_failed,
        )
        validate_group(
            "consumer_call",
            self.consumer_call_attempted,
            self.consumer_call_succeeded,
            self.consumer_call_failed,
        )

        if (not self.writer_attempted) and (
            self.writer_status is not ObservationStatus.NOT_ATTEMPTED
        ):
            raise ValueError(
                "writer_status must be NOT_ATTEMPTED when writer_attempted is False"
            )

        if (not self.capture_enabled) and (
            self.capture_status is not ObservationStatus.NOT_ATTEMPTED
        ):
            raise ValueError(
                "capture_status must be NOT_ATTEMPTED when capture_enabled is False"
            )

        if (not self.consumer_present) and (
            self.delivery_status is not ObservationStatus.NOT_ATTEMPTED
        ):
            raise ValueError(
                "delivery_status must be NOT_ATTEMPTED when consumer_present is False"
            )

        if self.skipped_empty_snapshot:
            if self.snapshot_entries_count != 0:
                raise ValueError(
                    "snapshot_entries_count must be 0 when skipped_empty_snapshot is True"
                )
            if self.delivery_status is not ObservationStatus.NOT_ATTEMPTED:
                raise ValueError(
                    "delivery_status must be NOT_ATTEMPTED when skipped_empty_snapshot is True"
                )

        if (
            self.capture_status is ObservationStatus.SUCCEEDED
            and self.entry_capture_succeeded <= 0
        ):
            raise ValueError(
                "capture_status=SUCCEEDED requires entry_capture_succeeded > 0"
            )

        if (
            self.capture_status is ObservationStatus.FAILED
            and (self.evidence_build_failed + self.entry_capture_failed) <= 0
        ):
            raise ValueError(
                "capture_status=FAILED requires at least one capture failure"
            )

        if self.capture_status is ObservationStatus.PARTIALLY_FAILED:
            if (
                self.entry_capture_succeeded <= 0
                or (self.evidence_build_failed + self.entry_capture_failed) <= 0
            ):
                raise ValueError(
                    "capture_status=PARTIALLY_FAILED requires successes and failures"
                )

        if self.delivery_status is ObservationStatus.SUCCEEDED:
            if (
                self.consumer_call_succeeded <= 0
                or self.manifest_build_succeeded <= 0
            ):
                raise ValueError(
                    "delivery_status=SUCCEEDED requires manifest build and consumer success"
                )

        if (
            self.delivery_status is ObservationStatus.FAILED
            and (self.consumer_call_failed + self.manifest_build_failed) <= 0
        ):
            raise ValueError(
                "delivery_status=FAILED requires at least one delivery failure"
            )
