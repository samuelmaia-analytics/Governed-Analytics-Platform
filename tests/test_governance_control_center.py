from __future__ import annotations

from pathlib import Path

import pandas as pd

import app.pages.governance_control_center as gcc
from app.pages.governance_control_center import save_governance_snapshot


def test_save_governance_snapshot_appends_history(tmp_path: Path) -> None:
    history_path = tmp_path / "governance_history.csv"
    df = pd.DataFrame({"id": [1, 2], "email": ["a@x.com", "b@x.com"]})
    risk_result = {
        "score": 35,
        "total_score": 35,
        "risk_level": "medium",
        "explanation": "test",
        "summary": "test",
        "components": {"personal_data_exposure": 7},
        "score_components": {"personal_data_exposure": 7},
        "per_component_points": {"personal_data_exposure": 7},
        "component_explanations": {"personal_data_exposure": "test"},
        "publication_recommendation": "needs_review",
        "recommendations": ["test"],
    }
    quality_result = {
        "total_rows": 2,
        "total_columns": 2,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 1,
    }

    first_path = save_governance_snapshot(
        df=df,
        risk_result=risk_result,
        quality_results=quality_result,
        publication_status="Needs Review",
        history_path=history_path,
    )
    second_path = save_governance_snapshot(
        df=df,
        risk_result=risk_result,
        quality_results=quality_result,
        publication_status="Needs Review",
        history_path=history_path,
    )

    stored = pd.read_csv(history_path)
    assert first_path == history_path
    assert second_path == history_path
    assert len(stored) == 2
    assert "publication_status" in stored.columns


class _FakeFigure:
    def update_layout(self, **_kwargs) -> None:
        return None


class _FakePlotlyExpress:
    @staticmethod
    def bar(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        return _FakeFigure()

    @staticmethod
    def line(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        return _FakeFigure()


class _FakeContainer:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def markdown(self, *_args, **_kwargs) -> None:
        return None

    def plotly_chart(self, *_args, **_kwargs) -> None:
        return None

    def dataframe(self, *_args, **_kwargs) -> None:
        return None

    def info(self, *_args, **_kwargs) -> None:
        return None

    def write(self, *_args, **_kwargs) -> None:
        return None

    def success(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, *_args, **_kwargs) -> None:
        return None

    def error(self, *_args, **_kwargs) -> None:
        return None

    def divider(self, *_args, **_kwargs) -> None:
        return None

    def caption(self, *_args, **_kwargs) -> None:
        return None


class _FakeStreamlit(_FakeContainer):
    def subheader(self, *_args, **_kwargs) -> None:
        return None

    def columns(self, n: int):  # type: ignore[no-untyped-def]
        return tuple(_FakeContainer() for _ in range(n))

    def expander(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        return _FakeContainer()

    def button(self, *_args, **_kwargs) -> bool:
        return False


def _sample_inputs() -> tuple[
    pd.DataFrame, pd.DataFrame, dict[str, object], dict[str, object]
]:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "value": [10.0, 12.0],
        }
    )
    classification_df = pd.DataFrame(
        {
            "column_name": ["order_id", "value"],
            "lgpd_classification": ["personal_data", "non_personal"],
            "risk_level": ["high", "low"],
            "recommended_action": ["mask", "keep"],
            "reason": ["test", "test"],
        }
    )
    risk_result = {
        "score": 55,
        "total_score": 55,
        "risk_level": "medium",
        "explanation": "test",
        "summary": "test",
        "components": {"x": 1},
        "score_components": {"x": 1},
        "per_component_points": {"x": 1},
        "component_explanations": {"x": "test"},
        "publication_recommendation": "needs_review",
        "recommendations": ["review controls"],
    }
    quality_result = {
        "total_rows": 2,
        "total_columns": 2,
        "null_pct_by_column": {"order_id": 0.0, "value": 0.0},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {"order_id": "object", "value": "float64"},
        "cardinality": {"order_id": 2, "value": 2},
        "possible_unique_keys": ["order_id"],
        "constant_columns": [],
        "checks": [
            {
                "check_name": "a",
                "status": "PASS",
                "severity": "low",
                "recommendation": "ok",
            }
        ],
        "failed_checks_count": 0,
    }
    return df, classification_df, risk_result, quality_result


def test_render_governance_control_center_handles_empty_history(monkeypatch) -> None:
    df, classification_df, risk_result, quality_result = _sample_inputs()
    monkeypatch.setattr(gcc, "st", _FakeStreamlit())
    monkeypatch.setattr(gcc, "px", _FakePlotlyExpress())
    monkeypatch.setattr(
        gcc, "_load_governance_history", lambda *_args, **_kwargs: pd.DataFrame()
    )

    gcc.render_governance_control_center(
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,  # type: ignore[arg-type]
        quality_results=quality_result,  # type: ignore[arg-type]
        locale="en-US",  # type: ignore[arg-type]
    )


def test_render_governance_control_center_with_history(monkeypatch) -> None:
    df, classification_df, risk_result, quality_result = _sample_inputs()
    history_df = pd.DataFrame(
        {
            "execution_timestamp": [
                "2026-01-01T00:00:00+00:00",
                "2026-01-02T00:00:00+00:00",
            ],
            "data_quality_score": [95, 90],
            "privacy_risk_score": [20, 40],
            "publication_status": ["Approved", "Needs Review"],
            "failed_rules_count": [0, 1],
            "warning_rules_count": [0, 1],
            "critical_rules_count": [0, 0],
            "row_count": [100, 120],
            "run_id": ["r1", "r2"],
            "dataset_name": ["fact_orders_dashboard", "fact_orders_dashboard"],
            "freshness_status": ["fresh", "warning"],
        }
    )
    monkeypatch.setattr(gcc, "st", _FakeStreamlit())
    monkeypatch.setattr(gcc, "px", _FakePlotlyExpress())
    monkeypatch.setattr(
        gcc, "_load_governance_history", lambda *_args, **_kwargs: history_df
    )

    gcc.render_governance_control_center(
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,  # type: ignore[arg-type]
        quality_results=quality_result,  # type: ignore[arg-type]
        locale="pt-BR",  # type: ignore[arg-type]
    )


def test_load_schema_contract_status_from_real_results(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "schema_contract_results.csv"
    pd.DataFrame(
        [
            {"check_name": "a", "status": "PASS"},
            {"check_name": "b", "status": "FAIL"},
        ]
    ).to_csv(path, index=False)
    monkeypatch.setattr(gcc, "SCHEMA_CONTRACT_RESULTS_PATH", path)

    status, note = gcc._load_schema_contract_status()
    assert status == "failed"
    assert note is None


def test_load_freshness_status_from_monitoring_results(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "published_layer_monitoring.csv"
    pd.DataFrame(
        [
            {
                "check_name": "published_file_freshness_hours",
                "status": "FAIL",
                "metric_value": 40,
                "threshold": 36,
            }
        ]
    ).to_csv(path, index=False)
    monkeypatch.setattr(gcc, "PUBLISHED_MONITORING_RESULTS_PATH", path)

    status, note = gcc._load_freshness_status()
    assert status == "warning"
    assert note is None


def test_evaluate_publication_gate_uses_critical_failures_from_severity() -> None:
    classification_df = pd.DataFrame(
        {
            "lgpd_classification": ["non_personal"],
            "recommended_action": ["keep"],
        }
    )
    risk_result = {
        "score": 20,
        "risk_level": "low",
        "recommendations": [],
    }
    quality_result = {
        "failed_checks_count": 3,
        "checks": [
            {"status": "FAIL", "severity": "low"},
            {"status": "FAIL", "severity": "high"},
            {"status": "PASS", "severity": "critical"},
        ],
    }

    gate_result, fallback_notes = gcc._evaluate_publication_gate(  # type: ignore[arg-type]
        classification_df=classification_df,
        risk_result=risk_result,  # type: ignore[arg-type]
        quality_results=quality_result,  # type: ignore[arg-type]
    )
    assert gate_result.decision == "Blocked"
    assert any("Critical rule failures detected: 1." in reason for reason in gate_result.reasons)
    assert not any("Critical rule failures fallback" in note for note in fallback_notes)
