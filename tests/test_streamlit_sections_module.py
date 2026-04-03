from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

import streamlit_app.sections as sections
from streamlit_app.data import FilterState


class DummyContext:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False


class FakeStreamlit:
    def __init__(self) -> None:
        self.markdowns: list[str] = []
        self.captions: list[str] = []
        self.infos: list[str] = []
        self.metrics: list[dict[str, str]] = []
        self.plots = 0
        self.dataframes = 0
        self.downloads = 0

    def markdown(self, value: str, **_kwargs) -> None:
        self.markdowns.append(value)

    def metric(self, **kwargs) -> None:
        self.metrics.append(kwargs)

    def columns(self, spec, **_kwargs):  # type: ignore[no-untyped-def]
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyContext() for _ in range(count)]

    def plotly_chart(self, _fig, **_kwargs) -> None:
        self.plots += 1

    def caption(self, value: str) -> None:
        self.captions.append(value)

    def info(self, value: str) -> None:
        self.infos.append(value)

    def dataframe(self, _data, **_kwargs) -> None:
        self.dataframes += 1

    def tabs(self, labels):  # type: ignore[no-untyped-def]
        return [DummyContext() for _ in labels]

    def download_button(self, **_kwargs) -> None:
        self.downloads += 1


def build_sections_frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for month in [1, 2]:
        for state in ["SP", "RJ"]:
            for order_index in range(45):
                rows.append(
                    {
                        "order_id": f"{month}-{state}-{order_index}",
                        "customer_unique_id": f"c-{month}-{state}-{order_index}",
                        "selected_state": state,
                        "category_label": "Bed Bath Table" if state == "SP" else "Health Beauty",
                        "payment_type_mode": "credit_card",
                        "order_status": "delivered",
                        "order_purchase_timestamp": pd.Timestamp(2018, month, 10),
                        "order_delivered_customer_date": pd.Timestamp(2018, month, 15),
                        "delivery_time_days": 4.0 if state == "SP" else 8.0,
                        "estimated_delay_days": 1.0,
                        "is_delayed": state == "RJ",
                        "review_score_mean": 4.5 if state == "SP" else 3.5,
                        "total_item_value": 100.0 + order_index,
                        "freight_value": 10.0,
                        "price": 90.0,
                        "month_start": pd.Timestamp(2018, month, 1),
                        "quarter_label": "2018 Q1",
                    }
                )
    return pd.DataFrame(rows)


def test_render_kpi_row_and_context_components(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(sections, "st", fake_st)

    sections.render_kpi_row(
        [
            {"label": f"KPI {index}", "value": "10", "delta": "+1%", "help": "ok"}
            for index in range(8)
        ]
    )
    sections.render_context_bar(
        build_sections_frame(),
        FilterState(
            start_date=pd.Timestamp("2018-01-01"),
            end_date=pd.Timestamp("2018-02-28"),
            categories=["Bed Bath Table"],
            states=["SP"],
            price_range=(0.0, 1000.0),
            freight_range=(0.0, 100.0),
            order_status=["delivered"],
            payment_types=["credit_card"],
            geography_mode="Cliente",
        ),
    )
    sections.render_smart_summary(build_sections_frame())

    assert len(fake_st.metrics) == 8
    assert any("Contexto do Recorte" in markdown for markdown in fake_st.markdowns)
    assert any("Leitura automática dos principais sinais" in markdown for markdown in fake_st.markdowns)


def test_render_chart_and_visual_sections(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(sections, "st", fake_st)
    fig = go.Figure()
    for chart_name in [
        "chart_revenue_line",
        "chart_orders_area",
        "chart_seasonality_heatmap",
        "chart_delay_by_period",
        "chart_top_categories_revenue",
        "chart_top_categories_orders",
        "chart_category_share_donut",
        "chart_category_value_vs_satisfaction",
        "chart_state_revenue",
        "chart_state_delivery_time",
        "chart_state_delay_rate",
        "chart_delivery_boxplot",
        "chart_delay_by_category",
        "chart_delivery_vs_review",
    ]:
        monkeypatch.setattr(sections, chart_name, lambda _df, fig=fig: fig)

    monkeypatch.setattr(
        sections,
        "build_smart_summary",
        lambda _df: {
            "summary": "Resumo",
            "chips": [{"label": "A", "value": "B"}],
            "recommendations": ["Recomendação"],
        },
    )
    monkeypatch.setattr(
        sections,
        "build_executive_insights",
        lambda _df: [{"title": "Sinal comercial", "text": "Texto"}],
    )
    monkeypatch.setattr(sections, "build_regional_insights", lambda _df: ["Insight"])

    df = build_sections_frame()
    sections.render_temporal_section(df)
    sections.render_category_section(df)
    sections.render_geography_section(df, "Cliente")
    sections.render_operations_section(df)
    sections.render_health_section(
        {
            "generated_at_utc": "2026-03-29T12:00:00+00:00",
            "total_checks": 4,
            "failed_checks": 1,
            "results": [
                {"check_name": "check_a", "status": "PASS", "severity": "high", "metric_value": 1},
                {"check_name": "check_b", "status": "FAIL", "severity": "medium", "metric_value": 2},
            ],
        }
    )
    sections.render_semantic_section(
        {
            "logistics": pd.DataFrame(
                {
                    "order_year": [2018],
                    "order_month": [1],
                    "customer_state": ["SP"],
                    "seller_state": ["RJ"],
                    "delayed_rate": [0.12],
                    "avg_freight_to_price_ratio": [0.15],
                }
            ),
            "seller": pd.DataFrame(
                {
                    "seller_key": ["s1"],
                    "delay_rate": [0.08],
                    "seller_volume_tier": ["core"],
                }
            ),
            "cohort": pd.DataFrame(
                {
                    "purchase_cohort_month": ["2018-01"],
                    "cohort_order_month_number": [1],
                    "customers": [10],
                }
            ),
        }
    )
    sections.render_executive_insights(df)
    sections.render_support_tables(df)

    assert fake_st.plots >= 11
    assert fake_st.dataframes >= 4
    assert fake_st.downloads == 3


def test_render_geography_section_handles_insufficient_volume(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(sections, "st", fake_st)
    monkeypatch.setattr(
        sections,
        "build_state_table",
        lambda _df: pd.DataFrame(
            {
                "uf": ["SP"],
                "receita": [100.0],
                "pedidos": [10],
                "ticket_medio": [10.0],
                "frete_medio": [5.0],
                "prazo_medio": [3.0],
                "atraso_pct": [1.0],
                "review_medio": [4.5],
            }
        ),
    )

    sections.render_geography_section(build_sections_frame(), "Cliente")

    assert fake_st.infos == ["O recorte atual não possui massa suficiente para uma análise regional comparável por UF."]


def test_render_health_and_semantic_sections_handle_missing_assets(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(sections, "st", fake_st)

    sections.render_health_section(None)
    sections.render_semantic_section({})

    assert fake_st.infos == [
        "O monitoramento recorrente ainda não está disponível neste ambiente. O dashboard segue operacional com a base principal.",
        "Os recortes semânticos ainda não estão disponíveis neste ambiente. A navegação principal do dashboard continua disponível.",
    ]
