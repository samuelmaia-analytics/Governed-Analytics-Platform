from __future__ import annotations

from pathlib import Path

import pandas as pd

import app.components.cards as cards
import app.pages.cohort_retention as cohort_page
import app.pages.data_quality as data_quality_page
import app.pages.eda as eda_page
import app.pages.executive_overview as executive_overview_page
import app.pages.genai_insights as genai_page
import app.pages.governance_report as governance_report_page
import app.pages.lgpd_privacy_risk as lgpd_page
import app.pages.revenue_analytics as revenue_page
import app.pages.seller_performance as seller_page


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

    def caption(self, *_args, **_kwargs) -> None:
        return None

    def download_button(self, *_args, **_kwargs) -> None:
        return None

    def code(self, *_args, **_kwargs) -> None:
        return None

    def plotly_chart(self, *_args, **_kwargs) -> None:
        return None

    def expander(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        return _FakeContainer()

    def tabs(self, tab_names):  # type: ignore[no-untyped-def]
        return tuple(_FakeContainer() for _ in tab_names)

    def selectbox(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        options = _kwargs.get("options", _args[1] if len(_args) > 1 else [])
        return options[0] if options else None

    def slider(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        return _kwargs.get("value", _kwargs.get("min_value", 0))


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

    @staticmethod
    def histogram(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        return _FakeFigure()

    @staticmethod
    def box(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
        return _FakeFigure()

    @staticmethod
    def bar(*_args, **_kwargs) -> _FakeFigure:  # type: ignore[no-untyped-def]
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
    data_quality_page.render_data_quality(
        quality_results, quality_table, locale="en-US"
    )  # type: ignore[arg-type]

    no_severity_table = pd.DataFrame([{"status": "PASS"}])
    data_quality_page.render_data_quality(
        quality_results, no_severity_table, locale="pt-BR"
    )  # type: ignore[arg-type]


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
    lgpd_page.render_lgpd_privacy_risk(
        df, classification_df, risk_result, locale="en-US"
    )  # type: ignore[arg-type]

    monkeypatch.setattr(
        lgpd_page,
        "apply_privacy_actions",
        lambda in_df, _class_df: (in_df.copy(), pd.DataFrame()),
    )
    lgpd_page.render_lgpd_privacy_risk(
        df, classification_df, risk_result, locale="pt-BR"
    )  # type: ignore[arg-type]


def test_render_eda_with_empty_and_non_empty_profiles(monkeypatch) -> None:
    monkeypatch.setattr(eda_page, "st", _FakeStreamlit())
    monkeypatch.setattr(eda_page, "px", _FakePlotlyExpress())

    df = pd.DataFrame({"category": ["a", "b"], "value": [10, 20]})
    eda_page.render_eda(df, locale="en-US")  # type: ignore[arg-type]

    monkeypatch.setattr(eda_page, "top_categories", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "detect_outliers_iqr", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "correlation_matrix", lambda _df: pd.DataFrame())
    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]


def test_render_executive_overview_and_governance_report(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(executive_overview_page, "st", _FakeStreamlit())

    df = pd.DataFrame({"a": [1], "b": [2]})
    classification_df = pd.DataFrame(
        {
            "lgpd_classification": ["personal_data", "non_personal"],
            "recommended_action": ["mask", "keep"],
        }
    )
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


def test_render_revenue_analytics_with_and_without_semantic_slices(monkeypatch) -> None:
    monkeypatch.setattr(revenue_page, "st", _FakeStreamlit())
    monkeypatch.setattr(revenue_page, "px", _FakePlotlyExpress())

    df = pd.DataFrame(
        {
            "order_year_month": ["2024-01", "2024-01", "2024-02"],
            "seller_key": ["s1", "s2", "s1"],
            "total_item_value": [100.0, 120.0, 200.0],
        }
    )
    category_slice = pd.DataFrame(
        {
            "product_category_name_english": ["cat_a", "cat_b"],
            "revenue": [500.0, 300.0],
        }
    )
    cohort_slice = pd.DataFrame(
        {
            "purchase_cohort_month": ["2024-01", "2024-01", "2024-02"],
            "cohort_order_month_number": [0, 1, 0],
            "customers": [100, 40, 80],
            "avg_ticket": [120.0, 110.0, 130.0],
        }
    )

    monkeypatch.setattr(
        revenue_page,
        "_load_semantic_slice",
        lambda path: category_slice.copy()
        if "category_slice" in str(path)
        else cohort_slice.copy(),
    )
    revenue_page.render_revenue_analytics(df, locale="pt-BR")  # type: ignore[arg-type]

    monkeypatch.setattr(revenue_page, "_load_semantic_slice", lambda _path: pd.DataFrame())
    revenue_page.render_revenue_analytics(df, locale="en-US")  # type: ignore[arg-type]


def test_render_seller_performance_with_and_without_data(monkeypatch) -> None:
    monkeypatch.setattr(seller_page, "st", _FakeStreamlit())
    monkeypatch.setattr(seller_page, "px", _FakePlotlyExpress())

    seller_df = pd.DataFrame(
        {
            "seller_key": ["s1", "s2"],
            "seller_state": ["SP", "RJ"],
            "seller_volume_tier": ["core", "core"],
            "total_items": [100, 80],
            "seller_order_count": [90, 70],
            "avg_ticket": [120.0, 140.0],
            "avg_delivery_time_days": [10.0, 12.0],
            "delay_rate": [0.05, 0.08],
            "avg_review_score": [4.2, 4.0],
        }
    )
    monkeypatch.setattr(seller_page, "_load_seller_slice", lambda: seller_df.copy())
    seller_page.render_seller_performance(locale="pt-BR")  # type: ignore[arg-type]

    monkeypatch.setattr(seller_page, "_load_seller_slice", lambda: pd.DataFrame())
    seller_page.render_seller_performance(locale="en-US")  # type: ignore[arg-type]


def test_render_cohort_retention_with_and_without_data(monkeypatch) -> None:
    monkeypatch.setattr(cohort_page, "st", _FakeStreamlit())
    monkeypatch.setattr(cohort_page, "px", _FakePlotlyExpress())

    cohort_df = pd.DataFrame(
        {
            "purchase_cohort_month": ["2024-01", "2024-01", "2024-02"],
            "cohort_order_month_number": [0, 1, 0],
            "customers": [100, 45, 80],
            "avg_ticket": [120.0, 115.0, 130.0],
        }
    )
    monkeypatch.setattr(cohort_page, "_load_cohort_slice", lambda: cohort_df.copy())
    cohort_page.render_cohort_retention(locale="pt-BR")  # type: ignore[arg-type]

    monkeypatch.setattr(cohort_page, "_load_cohort_slice", lambda: pd.DataFrame())
    cohort_page.render_cohort_retention(locale="en-US")  # type: ignore[arg-type]


def test_render_genai_insights_with_and_without_data(monkeypatch) -> None:
    monkeypatch.setattr(genai_page, "st", _FakeStreamlit())
    monkeypatch.setattr(genai_page, "px", _FakePlotlyExpress())

    genai_df = pd.DataFrame(
        {
            "source_id": ["a1", "a2"],
            "category": ["Phone Accessories", "Phone Accessories"],
            "extraction_mode": ["reference", "reference"],
            "model_name": ["reference_output", "reference_output"],
        }
    )
    monkeypatch.setattr(genai_page, "_load_genai_features", lambda: genai_df.copy())
    genai_page.render_genai_insights(locale="pt-BR")  # type: ignore[arg-type]

    monkeypatch.setattr(genai_page, "_load_genai_features", lambda: pd.DataFrame())
    genai_page.render_genai_insights(locale="en-US")  # type: ignore[arg-type]


def test_load_genai_features_drops_empty_rows(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "product_text_features.csv"
    csv_path.write_text(
        "source_id;title;category\n"
        "phone_case_001;Phone Case;Accessories\n"
        ";;\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(genai_page, "GENAI_FEATURES_PATH", csv_path)
    loaded = genai_page._load_genai_features()
    assert len(loaded) == 1
    assert loaded.iloc[0]["source_id"] == "phone_case_001"
