from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

DEFAULT_OUTPUT_PATH = Path("data/gold/publication_decisions.csv")
FIELDNAMES = [
    "execution_id",
    "dataset_name",
    "quality_score",
    "lgpd_risk_score",
    "critical_issues",
    "decision",
    "reason",
    "approved_by",
    "approved_at",
]


@dataclass(frozen=True)
class PublicationGateInput:
    dataset_name: str
    quality_score: int
    lgpd_risk_score: int
    critical_issues: int
    execution_id: str
    approved_by: str


@dataclass(frozen=True)
class PublicationGateDecision:
    execution_id: str
    dataset_name: str
    quality_score: int
    lgpd_risk_score: int
    critical_issues: int
    decision: str
    reason: str
    approved_by: str
    approved_at: str

    def as_row(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "dataset_name": self.dataset_name,
            "quality_score": self.quality_score,
            "lgpd_risk_score": self.lgpd_risk_score,
            "critical_issues": self.critical_issues,
            "decision": self.decision,
            "reason": self.reason,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
        }


def build_execution_id() -> str:
    return datetime.now(UTC).strftime("pubgate-%Y%m%dT%H%M%S%fZ")


def evaluate_publication_gate(
    *,
    quality_score: int,
    lgpd_risk_score: int,
    critical_issues: int,
) -> tuple[str, str]:
    if quality_score < 70 or lgpd_risk_score > 80 or critical_issues > 0:
        return (
            "Blocked",
            "Publication blocked because quality, privacy risk, or critical issues breached hard thresholds.",
        )
    if 70 <= quality_score <= 89 or 61 <= lgpd_risk_score <= 80:
        return (
            "Needs Review",
            "Publication requires manual review because quality or LGPD risk is in the review range.",
        )
    return (
        "Approved",
        "Publication approved because quality, LGPD risk, and critical issue thresholds passed.",
    )


def build_decision(input_data: PublicationGateInput) -> PublicationGateDecision:
    decision, reason = evaluate_publication_gate(
        quality_score=input_data.quality_score,
        lgpd_risk_score=input_data.lgpd_risk_score,
        critical_issues=input_data.critical_issues,
    )
    approved_at = datetime.now(UTC).isoformat() if decision == "Approved" else ""
    approved_by = input_data.approved_by if decision == "Approved" else ""
    return PublicationGateDecision(
        execution_id=input_data.execution_id,
        dataset_name=input_data.dataset_name,
        quality_score=input_data.quality_score,
        lgpd_risk_score=input_data.lgpd_risk_score,
        critical_issues=input_data.critical_issues,
        decision=decision,
        reason=reason,
        approved_by=approved_by,
        approved_at=approved_at,
    )


def append_decisions(
    decisions: Iterable[PublicationGateDecision],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output_path.exists() or output_path.stat().st_size == 0
    with output_path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        for decision in decisions:
            writer.writerow(decision.as_row())


def _build_input_from_mapping(raw: dict[str, object], args: argparse.Namespace) -> PublicationGateInput:
    return PublicationGateInput(
        dataset_name=str(raw["dataset_name"]),
        quality_score=int(raw["quality_score"]),
        lgpd_risk_score=int(raw["lgpd_risk_score"]),
        critical_issues=int(raw.get("critical_issues", 0)),
        execution_id=str(raw.get("execution_id") or args.execution_id or build_execution_id()),
        approved_by=str(raw.get("approved_by") or args.approved_by),
    )


def load_inputs_from_file(path: Path, args: argparse.Namespace) -> list[PublicationGateInput]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
        records = loaded if isinstance(loaded, list) else [loaded]
        return [_build_input_from_mapping(dict(record), args) for record in records]
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [_build_input_from_mapping(dict(row), args) for row in reader]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply publication gate rules and append the decision to data/gold/publication_decisions.csv."
    )
    parser.add_argument("--dataset-name", help="Dataset evaluated by the gate.")
    parser.add_argument("--quality-score", type=int, help="Data quality score from 0 to 100.")
    parser.add_argument("--lgpd-risk-score", type=int, help="LGPD risk score from 0 to 100.")
    parser.add_argument("--critical-issues", type=int, default=0, help="Critical issues found before publication.")
    parser.add_argument("--execution-id", help="Optional execution identifier.")
    parser.add_argument("--approved-by", default="publication_gate_cli", help="Approver recorded when the decision is Approved.")
    parser.add_argument("--input-file", type=Path, help="Optional CSV or JSON file with publication gate inputs.")
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_PATH, help="Output CSV path.")
    return parser.parse_args()


def build_inputs(args: argparse.Namespace) -> list[PublicationGateInput]:
    if args.input_file:
        return load_inputs_from_file(args.input_file, args)
    missing = [
        name
        for name, value in {
            "--dataset-name": args.dataset_name,
            "--quality-score": args.quality_score,
            "--lgpd-risk-score": args.lgpd_risk_score,
        }.items()
        if value is None
    ]
    if missing:
        raise SystemExit(f"Missing required arguments: {', '.join(missing)}")
    return [
        PublicationGateInput(
            dataset_name=args.dataset_name,
            quality_score=args.quality_score,
            lgpd_risk_score=args.lgpd_risk_score,
            critical_issues=args.critical_issues,
            execution_id=args.execution_id or build_execution_id(),
            approved_by=args.approved_by,
        )
    ]


def main() -> int:
    args = parse_args()
    inputs = build_inputs(args)
    decisions = [build_decision(item) for item in inputs]
    append_decisions(decisions, args.output_file)
    for decision in decisions:
        print(
            f"{decision.execution_id} | {decision.dataset_name} | {decision.decision} | {decision.reason}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
