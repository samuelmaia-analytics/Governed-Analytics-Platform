from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

import app.pages.governance_control_center as gcc
from app.pages.governance_control_center import save_governance_snapshot


def test_save_governance_snapshot_appends_history(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "governance_history.csv"
    decision_path = tmp_path / "publication_decision.json"
    original_append = gcc.append_governance_history

    def isolated_append(**kwargs):
        return original_append(
            **kwargs, publication_decision_path=decision_path
        )

    monkeypatch.setattr(gcc, "append_governance_history", isolated_append)
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
    assert decision_path.is_file()


class _FakeFigure:
    def update_layout(self, **_kwargs) -> None:
        return None


class _FakePlotlyExpress:
    def __init__(self) -> None:
        self.bar_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.line_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def bar(self, *args, **kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        captured_args = tuple(
            arg.copy(deep=True) if isinstance(arg, pd.DataFrame) else arg for arg in args
        )
        self.bar_calls.append((captured_args, dict(kwargs)))
        return _FakeFigure()

    def line(self, *args, **kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        captured_args = tuple(
            arg.copy(deep=True) if isinstance(arg, pd.DataFrame) else arg for arg in args
        )
        self.line_calls.append((captured_args, dict(kwargs)))
        return _FakeFigure()


class _FakeContainer:
    def __init__(self, owner: _FakeStreamlit) -> None:
        self.owner = owner

    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False

    def metric(self, label: str, value: object, **kwargs: object) -> None:
        self.owner.metrics.append((label, value, kwargs))

    def markdown(self, value: str, **_kwargs: object) -> None:
        self.owner.markdowns.append(value)

    def plotly_chart(self, figure: object, **kwargs: object) -> None:
        self.owner.plotly_calls.append((figure, kwargs))

    def dataframe(self, value: pd.DataFrame, **kwargs: object) -> None:
        self.owner.dataframes.append((value.copy(deep=True), kwargs))

    def info(self, value: str, **kwargs: object) -> None:
        self.owner.infos.append((value, kwargs))

    def write(self, value: object, **_kwargs: object) -> None:
        self.owner.writes.append(value)

    def success(self, value: str, **kwargs: object) -> None:
        self.owner.successes.append((value, kwargs))

    def warning(self, value: str, **kwargs: object) -> None:
        self.owner.warnings.append((value, kwargs))

    def error(self, value: str, **kwargs: object) -> None:
        self.owner.errors.append((value, kwargs))

    def divider(self, *_args, **_kwargs) -> None:
        self.owner.divider_count += 1

    def caption(self, value: str, **_kwargs: object) -> None:
        self.owner.captions.append(value)


class _FakeStreamlit(_FakeContainer):
    def __init__(self, *, button_value: bool = False) -> None:
        self.titles: list[str] = []
        self.subheaders: list[str] = []
        self.captions: list[str] = []
        self.markdowns: list[str] = []
        self.writes: list[object] = []
        self.metrics: list[tuple[str, object, dict[str, object]]] = []
        self.infos: list[tuple[str, dict[str, object]]] = []
        self.successes: list[tuple[str, dict[str, object]]] = []
        self.warnings: list[tuple[str, dict[str, object]]] = []
        self.errors: list[tuple[str, dict[str, object]]] = []
        self.dataframes: list[tuple[pd.DataFrame, dict[str, object]]] = []
        self.plotly_calls: list[tuple[object, dict[str, object]]] = []
        self.expanders: list[str] = []
        self.buttons: list[tuple[str, dict[str, object]]] = []
        self.divider_count = 0
        self.button_value = button_value
        super().__init__(self)

    def title(self, value: str) -> None:
        self.titles.append(value)

    def subheader(self, value: str) -> None:
        self.subheaders.append(value)

    def columns(self, n: int):  # type: ignore[no-untyped-def]
        return tuple(_FakeContainer(self) for _ in range(n))

    def expander(self, label: str, **_kwargs: object):  # type: ignore[no-untyped-def]
        self.expanders.append(label)
        return _FakeContainer(self)

    def button(self, label: str, **kwargs: object) -> bool:
        self.buttons.append((label, kwargs))
        return self.button_value


def _sample_inputs() -> (
    tuple[pd.DataFrame, pd.DataFrame, dict[str, object], dict[str, object]]
):
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


def _patch_deterministic_gate(
    monkeypatch,
    *,
    decision: str,
    severity: str,
) -> tuple[list[dict[str, object]], gcc.PublicationReadinessDecision]:
    gate_calls: list[dict[str, object]] = []
    gate_result = gcc.PublicationReadinessDecision(
        decision=decision,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        reasons=[
            "Critical rule failures detected: 1.",
            "Data quality score below recommended threshold (50 < 80).",
            "Privacy risk score is elevated (100 >= 60).",
            "Unknown gate reason.",
        ],
        required_actions=[
            "Resolve critical quality rule failures before publication.",
            "Investigate failed checks and improve data quality score.",
            "Review privacy controls and mitigation actions.",
            "Unknown gate action.",
        ],
    )

    def fake_evaluate_publication_readiness(**kwargs):  # type: ignore[no-untyped-def]
        gate_calls.append(dict(kwargs))
        return gate_result

    monkeypatch.setattr(
        gcc, "_load_schema_contract_status", lambda: ("passed", None)
    )
    monkeypatch.setattr(gcc, "_load_freshness_status", lambda: ("fresh", None))
    monkeypatch.setattr(
        gcc, "evaluate_publication_readiness", fake_evaluate_publication_readiness
    )
    return gate_calls, gate_result


def test_render_governance_control_center_handles_empty_history(monkeypatch) -> None:
    df, classification_df, risk_result, quality_result = _sample_inputs()
    original_df = df.copy(deep=True)
    original_classification_df = classification_df.copy(deep=True)
    original_risk_result = deepcopy(risk_result)
    original_quality_result = deepcopy(quality_result)
    fake_st = _FakeStreamlit()
    fake_px = _FakePlotlyExpress()
    snapshot_calls: list[dict[str, object]] = []
    canonical_evaluator = gcc.evaluate_publication_readiness

    monkeypatch.setattr(gcc, "st", fake_st)
    monkeypatch.setattr(gcc, "px", fake_px)
    monkeypatch.setattr(
        gcc, "_load_governance_history", lambda *_args, **_kwargs: pd.DataFrame()
    )
    monkeypatch.setattr(
        gcc,
        "save_governance_snapshot",
        lambda **kwargs: snapshot_calls.append(dict(kwargs)) or Path("unused.csv"),
    )
    gate_calls, gate_result = _patch_deterministic_gate(
        monkeypatch,
        decision="Blocked",
        severity="Critical",
    )
    original_gate_reasons = list(gate_result.reasons)
    original_gate_actions = list(gate_result.required_actions)

    gcc.render_governance_control_center(
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,  # type: ignore[arg-type]
        quality_results=quality_result,  # type: ignore[arg-type]
        locale="en-US",  # type: ignore[arg-type]
    )

    assert_frame_equal(df, original_df)
    assert_frame_equal(classification_df, original_classification_df)
    assert risk_result == original_risk_result
    assert quality_result == original_quality_result
    assert gate_result.reasons == original_gate_reasons
    assert gate_result.required_actions == original_gate_actions

    assert fake_st.titles == ["Governance Lab"]
    assert any("does not replace" in caption for caption in fake_st.captions)
    assert "### How to interpret this page" in fake_st.markdowns
    assert len(fake_st.metrics) == 8
    assert [label for label, _value, _kwargs in fake_st.metrics] == [
        "Personal Columns",
        "Sensitive Columns",
        "Indirect Identifier Columns",
        "Privacy Risk Score",
        "Data Quality Score",
        "Failed Checks",
        "Governance Status",
        "Publication Readiness",
    ]
    assert fake_st.metrics[-2][1] == "Needs Review"
    assert fake_st.metrics[-1][1] == "Blocked"
    assert any(
        "results differ" in message for message, _kwargs in fake_st.infos
    )
    assert any(
        "not only a visual simulation" in message
        for message, _kwargs in fake_st.warnings
    )
    assert fake_st.buttons == [
        ("Save snapshot and update persisted decision", {"type": "primary"})
    ]
    assert snapshot_calls == []
    assert any(
        "No governance snapshot has been persisted" in message
        for message, _kwargs in fake_st.infos
    )
    assert "Technical lab details" in fake_st.expanders

    assert gate_calls == [
        {
            "data_quality_score": 100,
            "privacy_risk_score": 55,
            "critical_rule_failures": 0,
            "freshness_status": "fresh",
            "schema_contract_status": "passed",
            "has_sensitive_data_without_protection": False,
        }
    ]
    assert gcc._governance_status("high", 0) == "Blocked"
    assert gcc._governance_status("medium", 0) == "Needs Review"
    assert gcc._governance_status("low", 1) == "Needs Review"
    assert gcc._governance_status("low", 0) == "Approved"
    for failed_checks, expected_score in [(0, 100), (5, 50), (11, 0)]:
        score_input = deepcopy(quality_result)
        score_input["failed_checks_count"] = failed_checks
        assert gcc._data_quality_score(score_input) == expected_score  # type: ignore[arg-type]

    canonical_defaults = {
        "critical_rule_failures": 0,
        "freshness_status": "fresh",
        "schema_contract_status": "passed",
        "has_sensitive_data_without_protection": False,
    }
    assert (
        canonical_evaluator(
            data_quality_score=80,
            privacy_risk_score=59,
            **canonical_defaults,  # type: ignore[arg-type]
        ).decision
        == "Approved"
    )
    assert (
        canonical_evaluator(
            data_quality_score=79,
            privacy_risk_score=59,
            **canonical_defaults,  # type: ignore[arg-type]
        ).decision
        == "Needs Review"
    )
    privacy_review = canonical_evaluator(
        data_quality_score=100,
        privacy_risk_score=60,
        **canonical_defaults,  # type: ignore[arg-type]
    )
    assert privacy_review.decision == "Needs Review"
    privacy_high = canonical_evaluator(
        data_quality_score=100,
        privacy_risk_score=80,
        **canonical_defaults,  # type: ignore[arg-type]
    )
    assert privacy_high.decision == "Needs Review"
    assert privacy_high.severity == "High"
    assert (
        canonical_evaluator(
            data_quality_score=100,
            privacy_risk_score=0,
            critical_rule_failures=1,
            freshness_status="fresh",
            schema_contract_status="passed",
            has_sensitive_data_without_protection=False,
        ).decision
        == "Blocked"
    )
    assert (
        canonical_evaluator(
            data_quality_score=100,
            privacy_risk_score=0,
            critical_rule_failures=0,
            freshness_status="fresh",
            schema_contract_status="failed",
            has_sensitive_data_without_protection=False,
        ).decision
        == "Blocked"
    )
    assert (
        canonical_evaluator(
            data_quality_score=100,
            privacy_risk_score=0,
            critical_rule_failures=0,
            freshness_status="fresh",
            schema_contract_status="passed",
            has_sensitive_data_without_protection=True,
        ).decision
        == "Blocked"
    )
    freshness_warning = canonical_evaluator(
        data_quality_score=100,
        privacy_risk_score=0,
        critical_rule_failures=0,
        freshness_status="warning",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    freshness_stale = canonical_evaluator(
        data_quality_score=100,
        privacy_risk_score=0,
        critical_rule_failures=0,
        freshness_status="stale",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert freshness_warning.decision == "Needs Review"
    assert freshness_stale.decision == "Needs Review"
    assert freshness_stale.severity == "High"

    assert len(fake_px.bar_calls) == 2
    class_counts_display = fake_px.bar_calls[0][0][0]
    assert isinstance(class_counts_display, pd.DataFrame)
    assert class_counts_display["count"].tolist() == [1, 1]
    check_counts_display = fake_px.bar_calls[1][0][0]
    assert isinstance(check_counts_display, pd.DataFrame)
    assert check_counts_display["count"].tolist() == [1]

    executive_table, executive_kwargs = next(
        (table, kwargs)
        for table, kwargs in fake_st.dataframes
        if list(table.columns)
        == [
            "Column",
            "LGPD classification",
            "Risk level",
            "Recommended action",
            "Reason",
        ]
    )
    assert len(executive_table) == 1
    assert executive_kwargs["hide_index"] is True
    technical_table = next(
        table
        for table, _kwargs in fake_st.dataframes
        if list(table.columns)
        == [
            "column_name",
            "lgpd_classification",
            "risk_level",
            "recommended_action",
            "reason",
        ]
    )
    assert technical_table.iloc[0]["lgpd_classification"] == "personal_data"


def test_render_governance_control_center_with_history(
    tmp_path: Path, monkeypatch
) -> None:
    df, classification_df, risk_result, quality_result = _sample_inputs()
    classification_rows: list[dict[str, str]] = []
    for prefix, classification, risk_level, action in [
        ("s", "sensitive_personal_data", "high", "anonymize"),
        ("p", "personal_data", "high", "mask"),
        ("i", "indirect_identifier", "medium", "review"),
    ]:
        for index in range(4):
            classification_rows.append(
                {
                    "column_name": f"{prefix}_{index}",
                    "lgpd_classification": classification,
                    "risk_level": risk_level,
                    "recommended_action": action,
                    "reason": f"reason_{prefix}_{index}",
                }
            )
    classification_rows.append(
        {
            "column_name": "other",
            "lgpd_classification": "non_personal",
            "risk_level": "low",
            "recommended_action": "keep",
            "reason": "other reason",
        }
    )
    classification_df = pd.DataFrame(classification_rows)
    risk_result["recommendations"] = [f"recommendation_{index}" for index in range(6)]
    quality_result["checks"] = [
        {
            "check_name": f"check_{index}",
            "status": "FAIL",
            "severity": "low",
            "recommendation": f"fix_{index}",
        }
        for index in range(6)
    ] + [
        {
            "check_name": "passing_check",
            "status": "PASS",
            "severity": "low",
            "recommendation": "keep",
        }
    ]
    quality_result["failed_checks_count"] = 6
    timestamps = pd.date_range("2026-01-01", periods=35, tz="UTC")
    history_df = pd.DataFrame(
        {
            "execution_timestamp": list(reversed(timestamps)),
            "data_quality_score": list(range(35)),
            "privacy_risk_score": list(range(35, 70)),
            "publication_status": ["Approved", "Needs Review", "Blocked", "Approved", "Needs Review"]
            * 7,
            "failed_rules_count": list(range(35)),
            "warning_rules_count": list(range(35)),
            "critical_rules_count": [0] * 35,
            "row_count": list(range(100, 135)),
            "run_id": [f"r{index}" for index in range(35)],
            "dataset_name": ["fact_orders_dashboard"] * 35,
            "freshness_status": ["fresh"] * 35,
        }
    )
    original_df = df.copy(deep=True)
    original_classification_df = classification_df.copy(deep=True)
    original_risk_result = deepcopy(risk_result)
    original_quality_result = deepcopy(quality_result)
    original_history_df = history_df.copy(deep=True)
    fake_st = _FakeStreamlit(button_value=True)
    fake_px = _FakePlotlyExpress()
    snapshot_calls: list[dict[str, object]] = []
    saved_path = tmp_path / "governance_history.csv"

    def fake_save_governance_snapshot(**kwargs):  # type: ignore[no-untyped-def]
        snapshot_calls.append(dict(kwargs))
        return saved_path

    monkeypatch.setattr(gcc, "st", fake_st)
    monkeypatch.setattr(gcc, "px", fake_px)
    monkeypatch.setattr(
        gcc, "_load_governance_history", lambda *_args, **_kwargs: history_df
    )
    monkeypatch.setattr(gcc, "save_governance_snapshot", fake_save_governance_snapshot)
    gate_calls, gate_result = _patch_deterministic_gate(
        monkeypatch,
        decision="Approved",
        severity="Low",
    )
    original_gate_reasons = list(gate_result.reasons)
    original_gate_actions = list(gate_result.required_actions)

    gcc.render_governance_control_center(
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,  # type: ignore[arg-type]
        quality_results=quality_result,  # type: ignore[arg-type]
        locale="pt-BR",  # type: ignore[arg-type]
    )

    assert_frame_equal(df, original_df)
    assert_frame_equal(classification_df, original_classification_df)
    assert risk_result == original_risk_result
    assert quality_result == original_quality_result
    assert_frame_equal(history_df, original_history_df)
    assert gate_result.reasons == original_gate_reasons
    assert gate_result.required_actions == original_gate_actions

    assert fake_st.titles == ["Laboratório de Governança"]
    assert "### Como interpretar esta página" in fake_st.markdowns
    assert any(
        "Ação com persistência" in markdown for markdown in fake_st.markdowns
    )
    assert any(
        "não é apenas uma simulação visual" in message
        for message, _kwargs in fake_st.warnings
    )
    assert fake_st.buttons == [
        ("Salvar snapshot e atualizar decisão persistida", {"type": "primary"})
    ]
    assert len(snapshot_calls) == 1
    assert snapshot_calls[0]["df"] is df
    assert snapshot_calls[0]["risk_result"] is risk_result
    assert snapshot_calls[0]["quality_results"] is quality_result
    assert snapshot_calls[0]["publication_status"] == "Needs Review"
    assert not saved_path.exists()
    assert all(
        str(saved_path.resolve()) not in message
        for message, _kwargs in fake_st.successes
    )
    assert any(str(saved_path.resolve()) in caption for caption in fake_st.captions)

    assert gate_calls == [
        {
            "data_quality_score": 40,
            "privacy_risk_score": 55,
            "critical_rule_failures": 0,
            "freshness_status": "fresh",
            "schema_contract_status": "passed",
            "has_sensitive_data_without_protection": False,
        }
    ]
    assert fake_st.metrics[-2][1] == "Requer revisão"
    assert fake_st.metrics[-1][1] == "Aprovado"
    assert any(
        "resultados diferem" in message for message, _kwargs in fake_st.infos
    )

    technical_top = next(
        table
        for table, _kwargs in fake_st.dataframes
        if list(table.columns)
        == [
            "column_name",
            "lgpd_classification",
            "risk_level",
            "recommended_action",
            "reason",
        ]
    )
    assert len(technical_top) == 10
    assert technical_top["column_name"].tolist() == [
        "s_0",
        "s_1",
        "s_2",
        "s_3",
        "p_0",
        "p_1",
        "p_2",
        "p_3",
        "i_0",
        "i_1",
    ]
    assert technical_top["lgpd_classification"].tolist()[:4] == [
        "sensitive_personal_data"
    ] * 4

    presentation_top, presentation_top_kwargs = next(
        (table, kwargs)
        for table, kwargs in fake_st.dataframes
        if "Classificação LGPD" in table.columns
    )
    assert len(presentation_top) == 10
    assert presentation_top_kwargs["hide_index"] is True
    assert "Dado pessoal sensível" in presentation_top["Classificação LGPD"].tolist()
    assert "sensitive_personal_data" not in presentation_top[
        "Classificação LGPD"
    ].tolist()

    technical_history = next(
        table
        for table, _kwargs in fake_st.dataframes
        if "execution_timestamp" in table.columns
    )
    assert len(technical_history) == 30
    assert technical_history["execution_timestamp"].is_monotonic_increasing
    assert technical_history.iloc[0]["execution_timestamp"] == timestamps[5]
    presentation_history, presentation_history_kwargs = next(
        (table, kwargs)
        for table, kwargs in fake_st.dataframes
        if "Data da execução" in table.columns
    )
    assert len(presentation_history) == 30
    assert presentation_history_kwargs["hide_index"] is True

    rendered_text = " ".join(str(value) for value in fake_st.writes)
    assert (
        "Este dataset possui 2 linhas e 2 colunas. O diagnóstico resumido está "
        "Requer revisão. O risco de privacidade está classificado como Média "
        "(55/100), e a qualidade dos dados está em 40/100. O publication gate "
        "resultou em Aprovado."
    ) in rendered_text
    assert "Foi detectada 1 falha crítica de regra." in rendered_text
    assert (
        "Score de qualidade abaixo do limite recomendado (50 < 80)."
        in rendered_text
    )
    assert "Score de risco de privacidade elevado (100 >= 60)." in rendered_text
    assert (
        "Resolver falhas críticas de qualidade antes da publicação."
        in rendered_text
    )
    assert (
        "Investigar checks reprovados e melhorar o score de qualidade dos dados."
        in rendered_text
    )
    assert "Revisar controles de privacidade e ações de mitigação." in rendered_text
    assert "**Severidade:** Baixa" in rendered_text
    for technical_text in original_gate_reasons + original_gate_actions:
        assert technical_text in rendered_text
    assert (
        gcc._presentation_gate_reason("Unmapped reason.", is_en=False)
        == "Unmapped reason."
    )
    assert (
        gcc._presentation_gate_action("Unmapped action.", is_en=False)
        == "Unmapped action."
    )
    for index in range(5):
        assert f"check_{index}: fix_{index}" in rendered_text
        assert f"recommendation_{index}" in rendered_text
    assert "check_5: fix_5" not in rendered_text
    assert "recommendation_5" not in rendered_text

    quality_bar_data = fake_px.bar_calls[1][0][0]
    assert isinstance(quality_bar_data, pd.DataFrame)
    assert quality_bar_data["count"].tolist() == [6, 1]
    assert len(fake_px.line_calls) == 4


def test_load_schema_contract_status_from_real_results(
    tmp_path: Path, monkeypatch
) -> None:
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


def test_load_freshness_status_from_monitoring_results(
    tmp_path: Path, monkeypatch
) -> None:
    path = tmp_path / "published_layer_monitoring.csv"
    pd.DataFrame(
        [
            {
                "check_name": "published_file_freshness_hours",
                "status": "FAIL",
                "metric_value": 54,
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
    assert any(
        "Critical rule failures detected: 1." in reason
        for reason in gate_result.reasons
    )
    assert not any("Critical rule failures fallback" in note for note in fallback_notes)
