from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

import streamlit_app.data as data_module


class FakeSidebar:
    def __init__(self) -> None:
        self.selectbox_values: list[object] = []
        self.radio_value = "Cliente"
        self.slider_values: list[tuple[float, float]] = []
        self.button_value = False
        self.date_value: tuple[date, date] | None = None
        self.toggle_value = False
        self.captions: list[str] = []

    def selectbox(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self.selectbox_values.pop(0)

    def caption(self, value: str) -> None:
        self.captions.append(value)

    def markdown(self, *_args, **_kwargs) -> None:
        return None

    def button(self, *_args, **_kwargs) -> bool:
        return self.button_value

    def date_input(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        return self.date_value

    def radio(self, *_args, **_kwargs) -> str:
        return self.radio_value

    def slider(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self.slider_values.pop(0)

    def toggle(self, *_args, **_kwargs) -> bool:
        return self.toggle_value


def build_dashboard_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "customer_unique_id": ["c1", "c2", "c3"],
            "product_category_name": ["cama_mesa_banho", "beleza_saude", None],
            "product_category_name_english": ["bed_bath_table", None, None],
            "customer_state": ["SP", "RJ", None],
            "seller_state": ["MG", "RJ", None],
            "order_status": ["delivered", None, "approved"],
            "payment_type_mode": ["credit_card", None, "boleto"],
            "is_delayed": [True, None, False],
            "review_score_mean": [4.5, 3.8, 5.0],
            "delivery_time_days": [4.0, 7.0, 2.0],
            "estimated_delay_days": [1.0, 2.0, 0.0],
            "total_item_value": [110.0, 210.0, 55.0],
            "price": [100.0, 200.0, 50.0],
            "freight_value": [10.0, 10.0, 5.0],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-10", "2018-02-11", "2018-01-05"]),
            "order_delivered_customer_date": pd.to_datetime(["2018-01-12", "2018-02-20", "2018-01-07"]),
            "order_date": ["2018-01-10", "2018-02-11", "2018-01-05"],
        }
    )


def test_load_data_reads_csv_and_derives_dashboard_columns(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "fact_orders_dashboard.csv"
    build_dashboard_frame().to_csv(csv_path, index=False)

    monkeypatch.setattr(data_module, "FACT_PARQUET_PATH", tmp_path / "missing.parquet")
    monkeypatch.setattr(data_module, "FACT_CSV_PATH", csv_path)

    df = data_module.load_data()

    assert "category_label" in df.columns
    assert df.loc[0, "category_label"] == "Bed Bath Table"
    assert df.loc[1, "order_status"] == "unknown"
    assert df.loc[1, "payment_type_mode"] == "unknown"
    assert df.loc[2, "customer_state"] == "NA"
    assert "quarter_label" in df.columns


def test_load_data_uses_order_date_as_fallback_for_purchase_timestamp(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "fact_orders_dashboard.csv"
    df = build_dashboard_frame()
    df["order_purchase_timestamp"] = [None, None, None]
    df["order_date"] = ["2018-01-10", "2018-02-11", "2018-01-05"]
    df.to_csv(csv_path, index=False)

    monkeypatch.setattr(data_module, "FACT_PARQUET_PATH", tmp_path / "missing.parquet")
    monkeypatch.setattr(data_module, "FACT_CSV_PATH", csv_path)
    data_module.load_data.clear()

    loaded = data_module.load_data()

    assert loaded["order_purchase_timestamp"].notna().all()


def test_load_data_raises_when_no_valid_purchase_dates_exist(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "fact_orders_dashboard.csv"
    df = build_dashboard_frame()
    df["order_purchase_timestamp"] = [None, None, None]
    df["order_date"] = [None, None, None]
    df.to_csv(csv_path, index=False)

    monkeypatch.setattr(data_module, "FACT_PARQUET_PATH", tmp_path / "missing.parquet")
    monkeypatch.setattr(data_module, "FACT_CSV_PATH", csv_path)
    data_module.load_data.clear()

    try:
        data_module.load_data()
    except ValueError as exc:
        assert "order_purchase_timestamp" in str(exc)
    else:
        raise AssertionError("Esperava ValueError para base sem datas válidas.")


def test_build_default_filter_state_sets_expected_defaults(monkeypatch) -> None:
    fake_st = type("FakeSt", (), {"session_state": {}})()
    monkeypatch.setattr(data_module, "st", fake_st)

    data_module.build_default_filter_state(build_dashboard_frame())

    assert fake_st.session_state["flt_geography_mode"] == "Cliente"
    assert fake_st.session_state["flt_category_mode"] == "Todas as categorias"
    assert fake_st.session_state["flt_price_range"] == (50.0, 200.0)


def test_reset_filters_removes_only_filter_keys_and_reruns(monkeypatch) -> None:
    rerun_called = {"value": False}
    fake_st = type(
        "FakeSt",
        (),
        {
            "session_state": {"flt_a": 1, "flt_b": 2, "other": 3},
            "rerun": staticmethod(lambda: rerun_called.__setitem__("value", True)),
        },
    )()
    monkeypatch.setattr(data_module, "st", fake_st)

    data_module.reset_filters()

    assert fake_st.session_state == {"other": 3}
    assert rerun_called["value"] is True


def test_resolve_single_or_all_returns_full_options_when_all_is_selected() -> None:
    result = data_module.resolve_single_or_all("Todos", "SP", ["SP", "RJ"], "Todos")

    assert result == ["SP", "RJ"]


def test_build_select_filter_returns_all_options_in_all_mode(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.selectbox_values = ["Todas"]
    fake_st = type("FakeSt", (), {"sidebar": sidebar, "session_state": {}})()
    monkeypatch.setattr(data_module, "st", fake_st)

    selected = data_module.build_select_filter(
        label="Categoria",
        mode_key="flt_category_mode",
        value_key="flt_category_value",
        all_label="Todas",
        focus_label="Específica",
        options=["A", "B"],
    )

    assert selected == ["A", "B"]
    assert fake_st.session_state["flt_category_value"] == "Todas"


def test_build_select_filter_returns_empty_list_when_no_options_exist(monkeypatch) -> None:
    sidebar = FakeSidebar()
    fake_st = type("FakeSt", (), {"sidebar": sidebar, "session_state": {}})()
    monkeypatch.setattr(data_module, "st", fake_st)

    selected = data_module.build_select_filter(
        label="Categoria",
        mode_key="flt_category_mode",
        value_key="flt_category_value",
        all_label="Todas",
        focus_label="Específica",
        options=[],
    )

    assert selected == []
    assert fake_st.session_state["flt_category_value"] == "Todas"
    assert sidebar.captions[-1] == "Sem opções disponíveis para categoria no recorte atual."


def test_clean_dimension_options_removes_placeholders_and_duplicates() -> None:
    values = pd.Series(["SP", "NA", "unknown", "SP", None, "RJ"])

    result = data_module.clean_dimension_options(values)

    assert result == ["RJ", "SP"]


def test_build_sidebar_filters_returns_structured_filter_state(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.selectbox_values = [
        "Categoria específica",
        "Bed Bath Table",
        "UF específica",
        "SP",
        "Status específico",
        "delivered",
        "Meio específico",
        "credit_card",
    ]
    sidebar.date_value = (date(2018, 1, 5), date(2018, 2, 11))
    sidebar.slider_values = [(50.0, 150.0), (5.0, 10.0)]
    fake_st = type("FakeSt", (), {"sidebar": sidebar, "session_state": {}})()
    monkeypatch.setattr(data_module, "st", fake_st)

    filters = data_module.build_sidebar_filters(data_module.load_data())

    assert filters.categories == ["Bed Bath Table"]
    assert filters.states == ["SP"]
    assert filters.order_status == ["delivered"]
    assert filters.payment_types == ["credit_card"]
    assert filters.price_range == (50.0, 150.0)


def test_build_sidebar_filters_supports_single_day_selection(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.selectbox_values = [
        "Todas as categorias",
        "Todos os estados",
        "Todos os status",
        "Todos os meios",
    ]
    sidebar.date_value = date(2018, 1, 10)
    sidebar.slider_values = [(50.0, 200.0), (5.0, 10.0)]
    fake_st = type("FakeSt", (), {"sidebar": sidebar, "session_state": {}})()
    monkeypatch.setattr(data_module, "st", fake_st)

    filters = data_module.build_sidebar_filters(data_module.load_data())

    assert filters.start_date == pd.Timestamp("2018-01-10")
    assert filters.end_date == pd.Timestamp("2018-01-10")


def test_build_app_mode_reads_sidebar_toggle(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.toggle_value = True
    fake_st = type("FakeSt", (), {"sidebar": sidebar})()
    monkeypatch.setattr(data_module, "st", fake_st)

    assert data_module.build_app_mode() is True


def test_build_dashboard_locale_defaults_to_portuguese_brazil(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.selectbox_values = ["Português (Brasil)"]
    fake_st = type("FakeSt", (), {"sidebar": sidebar})()
    monkeypatch.setattr(data_module, "st", fake_st)

    locale = data_module.build_dashboard_locale()

    assert locale == "pt-BR"
    assert sidebar.captions[-1] == "O dashboard está configurado para Português (Brasil)."


def test_build_dashboard_locale_supports_english_us(monkeypatch) -> None:
    sidebar = FakeSidebar()
    sidebar.selectbox_values = ["English (US)"]
    fake_st = type("FakeSt", (), {"sidebar": sidebar})()
    monkeypatch.setattr(data_module, "st", fake_st)

    locale = data_module.build_dashboard_locale()

    assert locale == "en-US"
    assert sidebar.captions[-1] == "Numbers follow international formatting and the app interface switches to English."


def test_load_semantic_assets_reads_available_parquets(tmp_path: Path, monkeypatch) -> None:
    logistics_path = tmp_path / "logistics.parquet"
    seller_path = tmp_path / "seller.parquet"
    executive_kpi_path = tmp_path / "executive_kpis.parquet"
    pd.DataFrame({"a": [1]}).to_parquet(logistics_path, index=False)
    pd.DataFrame({"b": [2]}).to_parquet(seller_path, index=False)
    pd.DataFrame({"metric_id": ["revenue_gross"]}).to_parquet(executive_kpi_path, index=False)

    monkeypatch.setattr(data_module, "LOGISTICS_PARQUET_PATH", logistics_path)
    monkeypatch.setattr(data_module, "SELLER_PARQUET_PATH", seller_path)
    monkeypatch.setattr(data_module, "COHORT_PARQUET_PATH", tmp_path / "missing.parquet")
    monkeypatch.setattr(data_module, "EXECUTIVE_KPI_PARQUET_PATH", executive_kpi_path)
    data_module.load_semantic_assets.clear()

    assets = data_module.load_semantic_assets()

    assert set(assets) == {"logistics", "seller", "executive_kpis"}


def test_load_monitoring_status_reads_json_summary(tmp_path: Path, monkeypatch) -> None:
    summary_path = tmp_path / "published_layer_monitoring.json"
    summary_path.write_text(json.dumps({"failed_checks": 1, "total_checks": 3}), encoding="utf-8")
    history_path = tmp_path / "published_layer_monitoring_history.csv"
    pd.DataFrame([{"generated_at_utc": "2026-04-05T10:00:00+00:00", "health_score": 92}]).to_csv(history_path, index=False)

    monkeypatch.setattr(data_module, "MONITORING_SUMMARY_PATH", summary_path)
    monkeypatch.setattr(data_module, "MONITORING_HISTORY_PATH", history_path)
    data_module.load_monitoring_status.clear()

    status = data_module.load_monitoring_status()

    assert status["failed_checks"] == 1
    assert status["total_checks"] == 3
    assert status["history"] == [{"generated_at_utc": "2026-04-05T10:00:00+00:00", "health_score": 92}]
