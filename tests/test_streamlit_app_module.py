from __future__ import annotations

import pandas as pd
import pytest

import streamlit_app.app as app_module
from streamlit_app.data import FilterState


class StopCalled(Exception):
    pass


class FakeSidebar:
    def __init__(self) -> None:
        self.captions: list[str] = []

    def caption(self, value: str) -> None:
        self.captions.append(value)


class FakeStreamlit:
    def __init__(self) -> None:
        self.sidebar = FakeSidebar()
        self.markdowns: list[str] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def markdown(self, value: str, **_kwargs) -> None:
        self.markdowns.append(value)

    def error(self, value: str) -> None:
        self.errors.append(value)

    def warning(self, value: str) -> None:
        self.warnings.append(value)

    def stop(self) -> None:
        raise StopCalled()


def build_app_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1"],
            "customer_unique_id": ["c1"],
            "selected_state": ["SP"],
            "category_label": ["Bed Bath Table"],
            "payment_type_mode": ["credit_card"],
            "order_status": ["delivered"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01"]),
            "order_delivered_customer_date": pd.to_datetime(["2018-01-05"]),
            "delivery_time_days": [4.0],
            "estimated_delay_days": [1.0],
            "is_delayed": [True],
            "review_score_mean": [4.5],
            "total_item_value": [110.0],
            "freight_value": [10.0],
            "price": [100.0],
            "month_start": pd.to_datetime(["2018-01-01"]),
            "quarter_label": ["2018 Q1"],
        }
    )


def build_filters() -> FilterState:
    return FilterState(
        start_date=pd.Timestamp("2018-01-01"),
        end_date=pd.Timestamp("2018-01-31"),
        categories=["Bed Bath Table"],
        states=["SP"],
        price_range=(0.0, 1000.0),
        freight_range=(0.0, 100.0),
        order_status=["delivered"],
        payment_types=["credit_card"],
        geography_mode="Cliente",
    )


def test_main_stops_with_error_when_data_file_is_missing(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(app_module, "st", fake_st)
    monkeypatch.setattr(app_module, "apply_theme", lambda: None)
    monkeypatch.setattr(app_module, "load_data", lambda: (_ for _ in ()).throw(FileNotFoundError("missing file")))

    with pytest.raises(StopCalled):
        app_module.main()

    assert fake_st.errors == ["missing file"]


def test_main_stops_with_warning_when_filters_return_no_rows(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(app_module, "st", fake_st)
    monkeypatch.setattr(app_module, "apply_theme", lambda: None)
    monkeypatch.setattr(app_module, "load_data", build_app_frame)
    monkeypatch.setattr(app_module, "build_sidebar_filters", lambda _df: build_filters())
    monkeypatch.setattr(app_module, "build_app_mode", lambda: False)
    monkeypatch.setattr(app_module, "filter_dataframe", lambda _df, _filters: pd.DataFrame())
    monkeypatch.setattr(app_module, "get_previous_period_df", lambda _df, _filters: pd.DataFrame())

    with pytest.raises(StopCalled):
        app_module.main()

    assert fake_st.warnings == ["Nenhum registro encontrado para os filtros selecionados."]


def test_main_runs_presentation_mode_flow(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    calls: list[str] = []
    monkeypatch.setattr(app_module, "st", fake_st)
    monkeypatch.setattr(app_module, "apply_theme", lambda: calls.append("theme"))
    monkeypatch.setattr(app_module, "load_data", build_app_frame)
    monkeypatch.setattr(app_module, "build_sidebar_filters", lambda _df: build_filters())
    monkeypatch.setattr(app_module, "build_app_mode", lambda: True)
    monkeypatch.setattr(app_module, "filter_dataframe", lambda df, _filters: df.copy())
    monkeypatch.setattr(app_module, "get_previous_period_df", lambda df, _filters: df.copy())
    monkeypatch.setattr(app_module, "render_header", lambda *_args, **_kwargs: calls.append("header"))
    monkeypatch.setattr(app_module, "build_metrics", lambda *_args, **_kwargs: [{"label": "A", "value": "B", "delta": "C", "help": "D"}] * 8)
    monkeypatch.setattr(app_module, "render_kpi_row", lambda _metrics: calls.append("kpi"))
    monkeypatch.setattr(app_module, "render_temporal_section", lambda _df: calls.append("tempo"))
    monkeypatch.setattr(app_module, "render_category_section", lambda _df: calls.append("categoria"))
    monkeypatch.setattr(app_module, "render_geography_section", lambda _df, _mode: calls.append("geo"))
    monkeypatch.setattr(app_module, "render_executive_insights", lambda _df: calls.append("insights"))

    app_module.main()

    assert calls == ["theme", "header", "kpi", "tempo", "categoria", "geo", "insights"]
    assert fake_st.sidebar.captions[-1] == "Registros filtrados: 1"


def test_main_runs_full_view_flow(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    calls: list[str] = []
    monkeypatch.setattr(app_module, "st", fake_st)
    monkeypatch.setattr(app_module, "apply_theme", lambda: calls.append("theme"))
    monkeypatch.setattr(app_module, "load_data", build_app_frame)
    monkeypatch.setattr(app_module, "build_sidebar_filters", lambda _df: build_filters())
    monkeypatch.setattr(app_module, "build_app_mode", lambda: False)
    monkeypatch.setattr(app_module, "filter_dataframe", lambda df, _filters: df.copy())
    monkeypatch.setattr(app_module, "get_previous_period_df", lambda df, _filters: df.copy())
    monkeypatch.setattr(app_module, "render_header", lambda *_args, **_kwargs: calls.append("header"))
    monkeypatch.setattr(app_module, "render_story_nav", lambda: "Visão completa")
    monkeypatch.setattr(app_module, "render_context_bar", lambda *_args, **_kwargs: calls.append("context"))
    monkeypatch.setattr(app_module, "render_smart_summary", lambda _df: calls.append("smart"))
    monkeypatch.setattr(app_module, "build_metrics", lambda *_args, **_kwargs: [{"label": "A", "value": "B", "delta": "C", "help": "D"}] * 8)
    monkeypatch.setattr(app_module, "render_kpi_row", lambda _metrics: calls.append("kpi"))
    monkeypatch.setattr(app_module, "render_temporal_section", lambda _df: calls.append("tempo"))
    monkeypatch.setattr(app_module, "render_category_section", lambda _df: calls.append("categoria"))
    monkeypatch.setattr(app_module, "render_geography_section", lambda _df, _mode: calls.append("geo"))
    monkeypatch.setattr(app_module, "render_operations_section", lambda _df: calls.append("ops"))
    monkeypatch.setattr(app_module, "render_executive_insights", lambda _df: calls.append("insights"))
    monkeypatch.setattr(app_module, "render_support_tables", lambda _df: calls.append("tables"))

    app_module.main()

    assert calls == ["theme", "header", "context", "smart", "kpi", "tempo", "categoria", "geo", "ops", "insights", "tables"]
