from __future__ import annotations

from pathlib import Path

import pandas as pd

import app.components.cards as cards
import app.pages.data_quality as data_quality_page
import app.pages.eda as eda_page
import app.pages.executive_overview as executive_overview_page
import app.pages.governance_report as governance_report_page
import app.pages.lgpd_privacy_risk as lgpd_page


class _FakeContainer:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def subheader(self, *_args, **_kwargs) -> None:
        return None

    def markdown(self, *_args, **_kwargs) -> None:
        return None

    def dataframe(self, *_args, **_kwargs) -> None:
        return None

    def bar_chart(self, *_args, **_kwargs) -> None:
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

    def download_button(self, *_args, **_kwargs) -> None:
        return None

    def code(self, *_args, **_kwargs) -> None:
        return None

    def plotly_chart(self, *_args, **_kwargs) -> None:
        return None


class _FakeStreamlit(_FakeContainer):
    def columns(self, n: int):  # type: ignore[no-untyped-def]
        return tuple(_FakeContainer() for _ in range(n))


class _FakeFigure:
    def __init__(self) -> None:
        self.layout_updates = 0

    def update_layout(self, **_kwargs) -> None:
        self.layout_updates += 1


class _FakePlotlyExpress:
    @staticmethod
    def imshow(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        return _FakeFigure()


def test_render_metric_cards_handles_empty_and_chunked(monkeypatch) -> None:
    monkeypatch.setattr(cards, "st", _FakeStreamlit())
    cards.render_metric_cards([])
    cards.render_metric_cards(
        [{"label": f"k{i}", "value": str(i)} for i in range(5)],
        max_columns=4,
    )
    cards.render_metric_cards([{"label": "k", "value": "1"}], max_columns=0)


def test_render_data_quality_covers_critical_and_noncritical_paths(monkeypatch) -> None:
    monkeypatch.setattr(data_quality_page, "st", _FakeStreamlit())

    quality_results = {
        "total_rows": 100,
        "total_columns": 3,
        "null_pct_by_column": {"a": 10.0, "b": 0.0},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {"a": "int64"},
        "cardinality": {"a": 100},
        "possible_unique_keys": ["a"],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 1,
    }
    quality_table = pd.DataFrame(
        [
            {"status": "PASS", "severity": "low", "check_name": "ok"},
            {"status": "FAIL", "severity": "medium", "check_name": "warn"},
            {"status": "FAIL", "severity": "high", "check_name": "block"},
        ]
    )
    data_quality_page.render_data_quality(quality_results, quality_table, locale="en-US")  # type: ignore[arg-type]

    no_severity_table = pd.DataFrame([{"status": "PASS"}])
    data_quality_page.render_data_quality(quality_results, no_severity_table, locale="pt-BR")  # type: ignore[arg-type]


def test_render_lgpd_privacy_risk_with_and_without_metadata(monkeypatch) -> None:
    monkeypatch.setattr(lgpd_page, "st", _FakeStreamlit())

    df = pd.DataFrame({"email": ["a@x.com"], "v": [1]})
    classification_df = pd.DataFrame(
        {
            "column_name": ["email", "v"],
            "lgpd_classification": ["personal_data", "non_personal"],
            "recommended_action": ["mask", "keep"],
        }
    )
    risk_result = {
        "score": 35,
        "total_score": 35,
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

    monkeypatch.setattr(
        lgpd_page,
        "apply_privacy_actions",
        lambda in_df, _class_df: (in_df.copy(), pd.DataFrame([{"action": "mask"}])),
    )
    lgpd_page.render_lgpd_privacy_risk(df, classification_df, risk_result, locale="en-US")  # type: ignore[arg-type]

    monkeypatch.setattr(
        lgpd_page,
        "apply_privacy_actions",
        lambda in_df, _class_df: (in_df.copy(), pd.DataFrame()),
    )
    lgpd_page.render_lgpd_privacy_risk(df, classification_df, risk_result, locale="pt-BR")  # type: ignore[arg-type]


def test_render_eda_with_empty_and_non_empty_profiles(monkeypatch) -> None:
    monkeypatch.setattr(eda_page, "st", _FakeStreamlit())
    monkeypatch.setattr(eda_page, "px", _FakePlotlyExpress())

    df = pd.DataFrame({"category": ["a", "b"], "value": [10, 20]})
    eda_page.render_eda(df, locale="en-US")  # type: ignore[arg-type]

    monkeypatch.setattr(eda_page, "top_categories", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "detect_outliers_iqr", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "correlation_matrix", lambda _df: pd.DataFrame())
    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]


def test_render_executive_overview_and_governance_report(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(executive_overview_page, "st", _FakeStreamlit())
    monkeypatch.setattr(executive_overview_page, "render_metric_cards", lambda _metrics: None)

    df = pd.DataFrame({"a": [1], "b": [2]})
    classification_df = pd.DataFrame({"lgpd_classification": ["personal_data", "non_personal"]})
    risk_result = {
        "score": 15,
        "total_score": 15,
        "risk_level": "low",
        "explanation": "test",
        "summary": "test",
        "components": {},
        "score_components": {},
        "per_component_points": {},
        "component_explanations": {},
        "publication_recommendation": "approved",
        "recommendations": [],
    }
    quality_results = {
        "total_rows": 1,
        "total_columns": 2,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 0,
    }
    executive_overview_page.render_executive_overview(  # type: ignore[arg-type]
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,
        quality_results=quality_results,
        locale="en-US",
    )
    quality_results["failed_checks_count"] = 2
    executive_overview_page.render_executive_overview(  # type: ignore[arg-type]
        df=df,
        classification_df=classification_df,
        risk_result=risk_result,
        quality_results=quality_results,
        locale="pt-BR",
    )

    monkeypatch.setattr(governance_report_page, "st", _FakeStreamlit())
    existing = tmp_path / "existing.md"
    existing.write_text("# report", encoding="utf-8")
    missing = tmp_path / "missing.md"
    governance_report_page.render_governance_report(
        {"existing": existing, "missing": missing},
        locale="en-US",  # type: ignore[arg-type]
    )
