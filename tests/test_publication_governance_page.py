from __future__ import annotations

import csv
import json
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import app.pages.publication_governance as page


def _write_json(path: Path, record: dict[str, object]) -> None:
    path.write_text(json.dumps(record), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def _write_checks(path: Path, statuses: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["check_name", "status"])
        writer.writeheader()
        writer.writerows(
            {"check_name": f"check_{index}", "status": status}
            for index, status in enumerate(statuses)
        )


def test_load_publication_governance_snapshot_from_persisted_evidence(
    tmp_path: Path,
) -> None:
    decision = tmp_path / "decision.json"
    shadow = tmp_path / "shadow.jsonl"
    dual = tmp_path / "dual.jsonl"
    content = tmp_path / "content.jsonl"
    privacy = tmp_path / "privacy.csv"
    schema = tmp_path / "schema.csv"
    business = tmp_path / "business.csv"
    quality = tmp_path / "quality.csv"
    monitoring = tmp_path / "monitoring.csv"

    _write_json(decision, {"status": "Approved"})
    _write_jsonl(
        shadow,
        [
            {
                "run_id": "old-run",
                "canonical_decision": "Approved",
            },
            {
                "run_id": "run-1",
                "canonical_decision": "Needs Review",
                "canonical_severity": "High",
                "provenance_valid": True,
            },
        ],
    )
    _write_jsonl(
        dual,
        [
            {
                "run_id": "run-1",
                "evaluated": True,
                "inherent_score": 86,
                "residual_score": 53,
                "residual_decision": "Approved",
                "residual_severity": "Low",
                "divergence_type": "residual_less_restrictive",
            }
        ],
    )
    _write_jsonl(
        content,
        [
            {
                "run_id": "run-1",
                "source_content_fingerprint": "source-sha256",
                "published_content_fingerprint": "published-sha256",
            }
        ],
    )
    _write_checks(privacy, ["PASS"] * 16)
    _write_checks(schema, ["PASS"] * 134)
    _write_checks(business, ["PASS"] * 5)
    _write_checks(quality, ["PASS"] * 24 + ["WARN"])
    _write_checks(monitoring, ["PASS"] * 12)

    snapshot = page.load_publication_governance_snapshot(
        decision_path=decision,
        shadow_path=shadow,
        dual_path=dual,
        content_path=content,
        privacy_path=privacy,
        schema_path=schema,
        business_path=business,
        quality_path=quality,
        monitoring_path=monitoring,
    )

    assert snapshot.run_id == "run-1"
    assert snapshot.historical_decision == "Approved"
    assert (snapshot.inherent_score, snapshot.residual_score) == (86, 53)
    assert snapshot.shadow_decision == "Needs Review"
    assert snapshot.residual_decision == "Approved"
    assert snapshot.divergence_type == "residual_less_restrictive"
    assert snapshot.sensitive_data_protected is True
    assert snapshot.privacy.display == "16/16 PASS"
    assert snapshot.schema.display == "134/134 PASS"
    assert snapshot.business.display == "5/5 PASS"
    assert snapshot.quality.display == "24/25 PASS · 1 WARN"
    assert snapshot.monitoring.display == "12/12 PASS"
    assert snapshot.execution_provenance == "Valid · same run"
    assert snapshot.content_provenance == "Recorded · same run"
    assert snapshot.source_fingerprint == "source-sha256"
    assert snapshot.published_fingerprint == "published-sha256"


def test_render_publication_governance_explains_diagnostic_authority(
    monkeypatch,
) -> None:
    calls: list[tuple[str, str]] = []
    metric_groups: list[list[dict[str, str]]] = []

    class FakeColumn:
        def info(self, value: str) -> None:
            calls.append(("info", value))

        def success(self, value: str) -> None:
            calls.append(("success", value))

        def warning(self, value: str) -> None:
            calls.append(("column_warning", value))

    fake_st = SimpleNamespace(
        header=lambda value: calls.append(("header", value)),
        caption=lambda value: calls.append(("caption", value)),
        warning=lambda value: calls.append(("warning", value)),
        success=lambda value: calls.append(("success", value)),
        info=lambda value: calls.append(("info", value)),
        subheader=lambda value: calls.append(("subheader", value)),
        columns=lambda count: [FakeColumn() for _ in range(count)],
        expander=lambda *_args, **_kwargs: nullcontext(),
        markdown=lambda value: calls.append(("markdown", value)),
        code=lambda value: calls.append(("code", value)),
    )
    monkeypatch.setattr(page, "st", fake_st)
    monkeypatch.setattr(
        page,
        "render_metric_cards",
        lambda metrics, **_kwargs: metric_groups.append(metrics),
    )
    checks = page.CheckSummary(1, 0, 0, 1)
    snapshot = page.PublicationGovernanceSnapshot(
        run_id="run-1",
        historical_decision="Approved",
        shadow_decision="Needs Review",
        shadow_severity="High",
        residual_decision="Approved",
        residual_severity="Low",
        inherent_score=86,
        residual_score=53,
        divergence_type="residual_less_restrictive",
        sensitive_data_protected=True,
        privacy=page.CheckSummary(16, 0, 0, 16),
        schema=checks,
        business=checks,
        quality=checks,
        monitoring=checks,
        execution_provenance="Valid · same run",
        content_provenance="Recorded · same run",
        source_fingerprint="source-sha256",
        published_fingerprint="published-sha256",
    )

    page.render_publication_governance(snapshot)

    assert ("warning", page.DIAGNOSTIC_NOTICE) in calls
    assert ("info", "Residual evaluation is less restrictive") in calls
    assert any(
        kind == "success" and "Authoritative decision: Approved" in value
        for kind, value in calls
    )
    assert any(
        "historical decision remains the publication authority" in value
        for kind, value in calls
        if kind == "markdown"
    )
    assert any(
        metric["label"] == "Sensitive data protection"
        and metric["value"] == "Protected — 16/16 privacy controls passed"
        for group in metric_groups
        for metric in group
    )
    assert any(
        metric["label"] == "Execution provenance"
        and metric["value"] == "Evidence linked to the same execution"
        for group in metric_groups
        for metric in group
    )
    assert any(
        metric["label"] == "Content provenance"
        and metric["value"] == "Dataset fingerprint recorded"
        for group in metric_groups
        for metric in group
    )
    assert any(
        metric["label"] == "Diagnostic / Shadow · residual"
        and metric["value"] == "53 → Approved / Low"
        for group in metric_groups
        for metric in group
    )


def test_missing_artifacts_are_reported_as_unavailable(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    snapshot = page.load_publication_governance_snapshot(
        decision_path=missing,
        shadow_path=missing,
        dual_path=missing,
        content_path=missing,
        privacy_path=missing,
        schema_path=missing,
        business_path=missing,
        quality_path=missing,
        monitoring_path=missing,
    )

    assert snapshot.run_id == "Unavailable"
    assert snapshot.sensitive_data_protected is None
    assert snapshot.execution_provenance == "Unavailable or mismatched"
    assert snapshot.content_provenance == "Unavailable or mismatched"
