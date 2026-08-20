from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import app.components.cards as cards
import app.pages.cohort_retention as cohort_page
import app.pages.data_catalog as data_catalog_page
import app.pages.data_quality as data_quality_page
import app.pages.eda as eda_page
import app.pages.executive_overview as executive_overview_page
import app.pages.genai_insights as genai_page
import app.pages.governance_control_center as control_center_page
import app.pages.governance_report as governance_report_page
import app.pages.lgpd_privacy_risk as lgpd_page
import app.pages.revenue_analytics as revenue_page
import app.pages.seller_performance as seller_page
from app.pages.publication_governance import (
    CheckSummary,
    PublicationGovernanceSnapshot,
)


class _FakeContainer:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def title(self, *_args, **_kwargs) -> None:
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

    def page_link(self, *_args, **_kwargs) -> None:
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
    titles: list[str] = []
    markdown_calls: list[str] = []
    captions: list[str] = []
    metrics: list[tuple[str, object]] = []
    bar_charts: list[
        tuple[pd.DataFrame | pd.Series, dict[str, object]]
    ] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []
    expanders: list[str] = []
    errors: list[str] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def bar_chart(
            self, data: pd.DataFrame | pd.Series, **kwargs: object
        ) -> None:
            bar_charts.append((data.copy(), kwargs))

        def dataframe(
            self, frame: pd.DataFrame, **kwargs: object
        ) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

        def expander(
            self, label: str, **_kwargs
        ) -> CapturingContainer:
            expanders.append(label)
            return CapturingContainer()

        def error(self, value: str) -> None:
            errors.append(value)

    monkeypatch.setattr(data_quality_page, "st", CapturingStreamlit())

    quality_results = {
        "total_rows": 112650,
        "total_columns": 34,
        "null_pct_by_column": {
            "estimated_delay_days": 2.18,
            "order_delivered_customer_date": 2.18,
            "carrier_delivery_time_days": 2.18,
            "delivery_time_days": 2.18,
            "product_category_name_english": 1.44,
            "product_category_name": 1.42,
            "seller_dispatch_time_days": 1.07,
            "review_score_mean": 0.84,
            "seller_avg_delivery_days": 0.18,
            "order_id": 0.0,
            "order_item_id": 0.0,
            "order_month": 0.0,
            "order_status": 0.0,
            "customer_unique_id": 0.0,
            "order_estimated_delivery_date": 0.0,
            "order_date": 0.0,
            "order_year": 0.0,
            "order_purchase_timestamp": 0.0,
            "seller_order_count": 0.0,
            "seller_volume_tier": 0.0,
        },
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {"order_id": "object"},
        "cardinality": {"order_id": 112650},
        "possible_unique_keys": ["order_id"],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 5,
    }
    passed_checks = [
        {
            "check_name": f"passed_check_{index}",
            "status": "PASS",
            "severity": "low",
            "affected_columns": ["order_id"],
            "affected_rows": 0,
            "recommendation": "No remediation required.",
            "rule_source": "quality_rule",
        }
        for index in range(16)
    ]
    quality_table = pd.DataFrame(
        [
            *passed_checks,
            {
                "check_name": "revenue_accepted_range",
                "status": "FAIL",
                "severity": "medium",
                "affected_columns": ["revenue"],
                "affected_rows": 3,
                "recommendation": "Review outlier revenue records and business rule boundaries.",
                "rule_source": "business_rule",
            },
            {
                "check_name": "revenue_no_negative",
                "status": "FAIL",
                "severity": "high",
                "affected_columns": ["revenue"],
                "affected_rows": 1,
                "recommendation": "Negative revenue should be justified or corrected.",
                "rule_source": "quality_rule",
            },
            {
                "check_name": "order_status_allowed_values",
                "status": "FAIL",
                "severity": "high",
                "affected_columns": ["order_status"],
                "affected_rows": 4,
                "recommendation": "Standardize order status values according to contract.",
                "rule_source": "schema_contract",
            },
            {
                "check_name": "product_category_required",
                "status": "FAIL",
                "severity": "medium",
                "affected_columns": ["product_category"],
                "affected_rows": 6,
                "recommendation": "Review missing product categories.",
                "rule_source": "quality_rule",
            },
            {
                "check_name": "seller_state_known",
                "status": "FAIL",
                "severity": "low",
                "affected_columns": ["seller_state"],
                "affected_rows": 1,
                "recommendation": "Review unknown seller states.",
                "rule_source": "quality_rule",
            },
        ]
    )
    original_quality_results = quality_results.copy()
    original_null_pct = dict(quality_results["null_pct_by_column"])
    original_quality_table = quality_table.copy(deep=True)

    data_quality_page.render_data_quality(
        quality_results, quality_table, locale="en-US"
    )  # type: ignore[arg-type]

    assert titles == ["Qualidade dos Dados"]
    assert any("Visão executiva" in text for text in markdown_calls)
    assert "### Como interpretar esta página" in markdown_calls
    assert any("dataset demonstrativo" in text for text in captions)
    assert ("Total de validações", "21") in metrics
    assert ("Aprovadas", "16") in metrics
    assert ("Alertas", "0") in metrics
    assert ("Falhas", "5") in metrics
    assert ("Total de linhas", "112.650") in metrics
    assert ("Total de colunas", "34") in metrics
    assert ("Score de qualidade", "50 / 100") in metrics
    assert errors == ["Bloqueado"]

    status_chart, status_chart_options = next(
        (chart, options)
        for chart, options in bar_charts
        if isinstance(chart, pd.DataFrame) and "status_label" in chart.columns
    )
    assert status_chart["status"].tolist() == ["PASS", "FAIL"]
    assert status_chart["status_label"].tolist() == ["APROVADO", "FALHA"]
    assert status_chart["count"].tolist() == [16, 5]
    assert status_chart_options == {
        "x": "status_label",
        "y": "count",
        "x_label": "Quantidade",
        "y_label": "Status",
        "horizontal": True,
        "sort": False,
        "height": 220,
    }
    assert "### Resultado das validações" in markdown_calls
    null_chart, null_chart_options = next(
        (chart, options)
        for chart, options in bar_charts
        if isinstance(chart, pd.DataFrame) and "column_label" in chart.columns
    )
    assert null_chart["column_name"].tolist() == list(original_null_pct)
    assert null_chart["null_pct"].tolist() == list(original_null_pct.values())
    assert null_chart["column_label"].tolist() == [
        "Desvio do prazo",
        "Data de entrega",
        "Entrega transportadora",
        "Tempo de entrega",
        "Categoria (inglês)",
        "Categoria produto",
        "Despacho seller",
        "Avaliação média",
        "Entrega média seller",
        "ID pedido",
        "Item pedido",
        "Mês pedido",
        "Status pedido",
        "Cliente",
        "Entrega estimada",
        "Data pedido",
        "Ano pedido",
        "Data da compra",
        "Pedidos seller",
        "Faixa de volume",
    ]
    assert all(not label.endswith(("...", "…")) for label in null_chart["column_label"])
    assert null_chart_options == {
        "x": "column_label",
        "y": "null_pct",
        "x_label": "Percentual de valores nulos",
        "y_label": "Campo",
        "horizontal": True,
        "sort": False,
        "height": 620,
    }
    assert "### Percentual de valores nulos por campo" in markdown_calls

    executive_table = next(
        frame for frame in displayed_frames if "Validação" in frame.columns
    )
    assert executive_table["Validação"].tolist() == [
        "Faixa válida de receita",
        "Receita não negativa",
        "Status de pedido permitido",
        "Product category required",
    ]
    assert executive_table["Status"].tolist() == ["FALHA"] * 4
    assert executive_table["Severidade"].tolist() == [
        "MÉDIA",
        "ALTA",
        "ALTA",
        "MÉDIA",
    ]
    assert executive_table["Colunas afetadas"].tolist() == [
        "Receita",
        "Receita",
        "Status do pedido",
        "Categoria do produto",
    ]
    assert executive_table["Linhas afetadas"].tolist() == [3, 1, 4, 6]
    assert executive_table["Origem da regra"].tolist() == [
        "business_rule",
        "quality_rule",
        "schema_contract",
        "quality_rule",
    ]
    assert executive_table["Recomendação"].tolist()[:3] == [
        "Revisar valores atípicos de receita e os limites definidos pelas regras de negócio.",
        "Valores negativos de receita devem ser justificados ou corrigidos.",
        "Padronizar os valores de status do pedido conforme o contrato de dados.",
    ]
    executive_index = next(
        index
        for index, frame in enumerate(displayed_frames)
        if "Validação" in frame.columns
    )
    assert dataframe_options[executive_index]["hide_index"] is True

    technical_table = next(
        frame for frame in displayed_frames if "check_name" in frame.columns
    )
    pd.testing.assert_frame_equal(technical_table, original_quality_table)
    assert "Detalhes técnicos das validações" in expanders
    assert quality_table["status"].tolist() == [
        *("PASS" for _ in range(16)),
        *("FAIL" for _ in range(5)),
    ]
    assert quality_results == original_quality_results
    assert quality_results["null_pct_by_column"] == original_null_pct
    pd.testing.assert_frame_equal(quality_table, original_quality_table)

    no_severity_table = pd.DataFrame([{"status": "PASS"}])
    data_quality_page.render_data_quality(
        quality_results, no_severity_table, locale="pt-BR"
    )  # type: ignore[arg-type]


def test_render_lgpd_privacy_risk_with_and_without_metadata(monkeypatch) -> None:
    titles: list[str] = []
    subtitles: list[str] = []
    captions: list[str] = []
    markdown_calls: list[str] = []
    info_calls: list[str] = []
    write_calls: list[str] = []
    metrics: list[tuple[str, object]] = []
    tab_groups: list[list[str]] = []
    expanders: list[str] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def subheader(self, value: str) -> None:
            subtitles.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def info(self, value: str) -> None:
            info_calls.append(value)

        def write(self, value: str) -> None:
            write_calls.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def tabs(self, tab_names):  # type: ignore[no-untyped-def]
            tab_groups.append(list(tab_names))
            return tuple(CapturingContainer() for _ in tab_names)

        def expander(
            self, label: str, **_kwargs
        ) -> CapturingContainer:
            expanders.append(label)
            return CapturingContainer()

    monkeypatch.setattr(lgpd_page, "st", CapturingStreamlit())

    df = pd.DataFrame({"email": ["a@x.com"], "v": [1]})
    classification_df = pd.DataFrame(
        {
            "column_name": ["email", "v"],
            "lgpd_classification": ["personal_data", "non_personal"],
            "recommended_action": ["mask", "keep"],
        }
    )
    risk_result = {
        "score": 100,
        "total_score": 100,
        "risk_level": "high",
        "explanation": "test",
        "summary": "test",
        "components": {"x": 1},
        "score_components": {"x": 1},
        "per_component_points": {"x": 1},
        "component_explanations": {"x": "test"},
        "publication_recommendation": "blocked",
        "recommendations": [
            "Apply masking for direct identifiers in shared datasets.",
            "Anonymize or remove sensitive columns from executive layers.",
            "Review null patterns in critical personal-data columns.",
            "Document legal basis and retention policy for personal data usage.",
            "Block publication until masking/anonymization controls are implemented.",
        ],
    }
    original_recommendations = list(risk_result["recommendations"])

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

    assert titles == ["Privacidade e Controles LGPD"] * 2
    assert tab_groups[0] == [
        "Score e risco",
        "Classificações",
        "Prévia de transformações",
    ]
    assert "Avaliação diagnóstica de privacidade" in subtitles
    assert any("RIPD formal" in caption for caption in captions)
    assert "### Como interpretar esta página" in markdown_calls
    assert any("riscos elevados" in message for message in info_calls)
    assert ("Score de risco de privacidade", "100 / 100") in metrics
    assert ("Nível de risco", "ALTO") in metrics
    assert ("Recomendação de publicação", "BLOQUEADO") in metrics
    assert "Componentes técnicos do score" in expanders
    assert "- Aplicar mascaramento aos identificadores diretos em datasets compartilhados." in write_calls
    assert "- Anonimizar ou remover colunas sensíveis das camadas executivas." in write_calls
    assert "- Revisar padrões de valores nulos em colunas críticas de dados pessoais." in write_calls
    assert "- Documentar a base legal e a política de retenção para uso de dados pessoais." in write_calls
    assert (
        "- Bloquear a publicação até que os controles de mascaramento ou "
        "anonimização estejam implementados."
    ) in write_calls
    assert risk_result["score"] == 100
    assert risk_result["risk_level"] == "high"
    assert risk_result["publication_recommendation"] == "blocked"
    assert risk_result["recommendations"] == original_recommendations


def test_render_eda_with_empty_and_non_empty_profiles(monkeypatch) -> None:
    titles: list[str] = []
    subtitles: list[str] = []
    captions: list[str] = []
    markdown_calls: list[str] = []
    write_calls: list[str] = []
    info_calls: list[str] = []
    metrics: list[tuple[str, object]] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []
    tab_groups: list[list[str]] = []
    expanders: list[str] = []
    selectbox_calls: list[tuple[str, dict[str, object]]] = []
    slider_calls: list[tuple[str, dict[str, object]]] = []
    histogram_calls: list[tuple[pd.DataFrame, dict[str, object]]] = []
    box_calls: list[tuple[pd.DataFrame, dict[str, object]]] = []
    bar_calls: list[tuple[pd.DataFrame, dict[str, object]]] = []
    imshow_calls: list[tuple[pd.DataFrame, dict[str, object]]] = []
    selected_columns = iter(["value", "category", "event_time", "category"])

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs: object) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def subheader(self, value: str) -> None:
            subtitles.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def write(self, value: str) -> None:
            write_calls.append(value)

        def info(self, value: str) -> None:
            info_calls.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def dataframe(
            self, frame: pd.DataFrame, **kwargs: object
        ) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

        def tabs(self, tab_names):  # type: ignore[no-untyped-def]
            tab_groups.append(list(tab_names))
            return tuple(CapturingContainer() for _ in tab_names)

        def expander(self, label: str, **_kwargs: object) -> CapturingContainer:
            expanders.append(label)
            return CapturingContainer()

        def selectbox(self, label: str, **kwargs: object) -> str:
            selectbox_calls.append((label, kwargs))
            return next(selected_columns)

        def slider(self, label: str, **kwargs: object) -> int:
            slider_calls.append((label, kwargs))
            return int(kwargs["value"])

    class CapturingPlotlyExpress:
        @staticmethod
        def imshow(frame: pd.DataFrame, **kwargs: object) -> _FakeFigure:
            imshow_calls.append((frame.copy(), kwargs))
            return _FakeFigure()

        @staticmethod
        def histogram(frame: pd.DataFrame, **kwargs: object) -> _FakeFigure:
            histogram_calls.append((frame.copy(), kwargs))
            return _FakeFigure()

        @staticmethod
        def box(frame: pd.DataFrame, **kwargs: object) -> _FakeFigure:
            box_calls.append((frame.copy(), kwargs))
            return _FakeFigure()

        @staticmethod
        def bar(frame: pd.DataFrame, **kwargs: object) -> _FakeFigure:
            bar_calls.append((frame.copy(), kwargs))
            return _FakeFigure()

    df = pd.DataFrame(
        {
            "category": ["a", "b", "c", "d", "e", "f", "a", "b", None, "a"],
            "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, None, 100.0],
            "value_two": [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 200.0],
            "event_time": pd.date_range("2026-01-01", periods=10),
        }
    )
    original_df = df.copy(deep=True)

    helper_names = [
        "generate_storytelling_insights",
        "descriptive_statistics",
        "dtype_distribution",
        "top_categories",
        "null_profile",
        "detect_outliers_iqr",
        "correlation_matrix",
        "run_statistical_tests",
    ]
    original_helpers = {name: getattr(eda_page, name) for name in helper_names}
    helper_calls: dict[str, list[object]] = {name: [] for name in helper_names}

    expected_descriptive = original_helpers["descriptive_statistics"](df)
    expected_dtypes = original_helpers["dtype_distribution"](df)
    expected_categories = original_helpers["top_categories"](df)
    expected_nulls = original_helpers["null_profile"](df)
    expected_outliers = original_helpers["detect_outliers_iqr"](df)
    expected_correlation = original_helpers["correlation_matrix"](df)
    expected_tests = original_helpers["run_statistical_tests"](df)

    def capture_helper(name):  # type: ignore[no-untyped-def]
        helper = original_helpers[name]

        def wrapped(in_df):  # type: ignore[no-untyped-def]
            result = helper(in_df)
            helper_calls[name].append(
                result.copy() if isinstance(result, pd.DataFrame) else list(result)
            )
            return result

        return wrapped

    for helper_name in helper_names:
        monkeypatch.setattr(eda_page, helper_name, capture_helper(helper_name))

    monkeypatch.setattr(eda_page, "st", CapturingStreamlit())
    monkeypatch.setattr(eda_page, "px", CapturingPlotlyExpress())

    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]
    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]
    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]

    for helper_name in helper_names:
        assert len(helper_calls[helper_name]) == 3

    pd.testing.assert_frame_equal(
        helper_calls["descriptive_statistics"][0], expected_descriptive
    )
    pd.testing.assert_frame_equal(helper_calls["dtype_distribution"][0], expected_dtypes)
    pd.testing.assert_frame_equal(helper_calls["top_categories"][0], expected_categories)
    pd.testing.assert_frame_equal(helper_calls["null_profile"][0], expected_nulls)
    pd.testing.assert_frame_equal(helper_calls["detect_outliers_iqr"][0], expected_outliers)
    pd.testing.assert_frame_equal(
        helper_calls["correlation_matrix"][0], expected_correlation
    )
    pd.testing.assert_frame_equal(helper_calls["run_statistical_tests"][0], expected_tests)

    assert titles == ["Análise Técnica dos Dados"] * 3
    assert subtitles == [
        "Diagnóstico exploratório do ativo analítico para compreender estrutura, "
        "distribuição, ausência de valores, outliers e relações entre variáveis."
    ] * 3
    assert any("não representam, por si só, decisões de negócio" in text for text in captions)
    assert "### Como interpretar esta página" in markdown_calls
    assert "### Leitura técnica" in markdown_calls
    assert any("Cada resultado deve ser interpretado" in text for text in write_calls)
    assert metrics[:4] == [
        ("Registros", "10"),
        ("Colunas", "4"),
        ("Colunas numéricas", "2"),
        ("Colunas com nulos", "2"),
    ]
    assert ["Visão Geral", "Análise por Coluna"] in tab_groups
    assert [
        "Resumo",
        "Perfil estrutural",
        "Relações numéricas",
        "Detalhes estatísticos",
    ] in tab_groups
    assert "Detalhes técnicos da análise" in expanders

    assert all(call[1]["options"] == list(df.columns) for call in selectbox_calls[:3])
    assert all(call[1]["key"] == "eda_column_selector" for call in selectbox_calls[:3])
    assert slider_calls == [
        (
            "Quantidade de categorias exibidas",
            {"min_value": 5, "max_value": 7, "value": 7, "key": "eda_top_n"},
        )
    ]

    numeric_histograms = [call for call in histogram_calls if call[1]["x"] == "value"]
    assert len(numeric_histograms) == 1
    assert numeric_histograms[0][1]["nbins"] == 40
    assert numeric_histograms[0][1]["marginal"] == "rug"
    datetime_histograms = [
        call for call in histogram_calls if call[1]["x"] == "event_time"
    ]
    assert len(datetime_histograms) == 1
    assert "nbins" not in datetime_histograms[0][1]
    assert "marginal" not in datetime_histograms[0][1]
    assert len(box_calls) == 1
    assert box_calls[0][1]["y"] == "value"
    assert box_calls[0][1]["points"] == "outliers"

    expected_counts = df["category"].dropna().value_counts().head(7).reset_index()
    expected_counts.columns = ["category", "count"]
    assert len(bar_calls) == 1
    pd.testing.assert_frame_equal(bar_calls[0][0], expected_counts)
    assert bar_calls[0][1]["x"] == "category"
    assert bar_calls[0][1]["y"] == "count"
    assert len(imshow_calls) == 3
    for correlation_frame, kwargs in imshow_calls:
        pd.testing.assert_frame_equal(correlation_frame, expected_correlation)
        assert kwargs == {
            "text_auto": True,
            "aspect": "auto",
            "color_continuous_scale": "Blues",
        }

    assert any(frame.equals(expected_descriptive) for frame in displayed_frames)
    assert any(frame.equals(expected_dtypes) for frame in displayed_frames)
    assert any(frame.equals(expected_categories) for frame in displayed_frames)
    assert any(frame.equals(expected_nulls) for frame in displayed_frames)
    assert any(frame.equals(expected_outliers) for frame in displayed_frames)
    assert any(frame.equals(expected_correlation) for frame in displayed_frames)
    assert any(frame.equals(expected_tests) for frame in displayed_frames)
    assert any("Variável" in frame.columns for frame in displayed_frames)
    assert any("Percentual ausente" in frame.columns for frame in displayed_frames)
    assert any("Normalidade — Jarque-Bera" in frame.astype(str).values for frame in displayed_frames)
    assert any(options.get("hide_index") is True for options in dataframe_options)

    monkeypatch.setattr(eda_page, "generate_storytelling_insights", lambda _df: [])
    monkeypatch.setattr(eda_page, "top_categories", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "detect_outliers_iqr", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "correlation_matrix", lambda _df: pd.DataFrame())
    monkeypatch.setattr(eda_page, "run_statistical_tests", lambda _df: pd.DataFrame())
    eda_page.render_eda(df, locale="pt-BR")  # type: ignore[arg-type]

    assert "Sem insights narrativos disponíveis para este dataset." in info_calls
    assert "Sem colunas categóricas disponíveis." in info_calls
    assert "Sem colunas numéricas para detecção de outliers." in info_calls
    assert "Sem colunas numéricas para correlação." in info_calls
    assert "Dados numéricos insuficientes para testes estatísticos." in info_calls
    assert selectbox_calls[-1][1]["key"] == "eda_column_selector"
    assert slider_calls[-1][1] == {
        "min_value": 5,
        "max_value": 7,
        "value": 7,
        "key": "eda_top_n",
    }

    pd.testing.assert_frame_equal(df, original_df)

    page_source = Path(eda_page.__file__).read_text(encoding="utf-8")
    src_eda_source = (Path(eda_page.__file__).parents[2] / "src" / "eda.py").read_text(
        encoding="utf-8"
    )
    assert "df[column].dropna()" in page_source
    assert "df[column].isna().sum()" in page_source
    assert "df[column].isna().mean() * 100" in page_source
    assert "nunique(dropna=False)" in page_source
    assert "str(df[column].dtype)" in page_source
    assert "is_numeric_dtype(df[column])" in page_source
    assert "is_datetime64_any_dtype(df[column])" in page_source
    assert "pd.to_datetime" not in page_source
    assert "series.value_counts().head(top_n).reset_index()" in page_source
    assert "min_value=5" in page_source
    assert "max_value=min(50, distinct)" in page_source
    assert "value=min(20, distinct)" in page_source
    assert "nbins=40" in page_source
    assert 'marginal="rug"' in page_source
    assert 'points="outliers"' in page_source
    assert "groupby(" not in page_source
    assert ".merge(" not in page_source
    assert "top_n: int = 5" in src_eda_source
    assert "numeric_df.columns[:5]" in src_eda_source
    assert "if n < 8" in src_eda_source
    assert "p_value < 0.05" in src_eda_source
    assert "1.5 * iqr" in src_eda_source


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


def test_portfolio_overview_prioritizes_value_kpis_and_navigation(
    monkeypatch,
) -> None:
    calls: list[tuple[str, str]] = []
    metrics: list[tuple[str, object]] = []
    page_links: list[str] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

        def info(self, value: str) -> None:
            calls.append(("info", value))

        def success(self, value: str) -> None:
            calls.append(("success", value))

        def page_link(self, *_args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            page_links.append(str(kwargs["label"]))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            calls.append(("title", value))

        def caption(self, value: str) -> None:
            calls.append(("caption", value))

        def markdown(self, value: str) -> None:
            calls.append(("markdown", value))

        def write(self, value: str) -> None:
            calls.append(("write", value))

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def expander(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
            return CapturingContainer()

    checks = CheckSummary(1, 0, 0, 1)
    snapshot = PublicationGovernanceSnapshot(
        run_id="run-1",
        historical_decision="Needs Review",
        shadow_decision="Needs Review",
        shadow_severity="High",
        residual_decision="Approved",
        residual_severity="Low",
        inherent_score=86,
        residual_score=53,
        divergence_type="residual_less_restrictive",
        sensitive_data_protected=True,
        privacy=CheckSummary(16, 0, 0, 16),
        schema=checks,
        business=checks,
        quality=CheckSummary(24, 1, 0, 25),
        monitoring=CheckSummary(12, 0, 0, 12),
        execution_provenance="Valid · same run",
        content_provenance="Recorded · same run",
        source_fingerprint="source-sha256",
        published_fingerprint="published-sha256",
    )
    monkeypatch.setattr(executive_overview_page, "st", CapturingStreamlit())
    monkeypatch.setattr(
        executive_overview_page,
        "_render_operational_readiness_section",
        lambda _locale: None,
    )

    executive_overview_page.render_executive_overview(  # type: ignore[arg-type]
        df=pd.DataFrame({"value": [1, 2]}),
        classification_df=pd.DataFrame(
            {
                "lgpd_classification": ["non_personal"],
                "recommended_action": ["keep"],
            }
        ),
        risk_result={
            "score": 15,
            "risk_level": "low",
            "recommendations": [],
        },
        quality_results={"failed_checks_count": 0},
        locale="pt-BR",
        business_page=SimpleNamespace(),
        governance_page=SimpleNamespace(),
        governance_snapshot=snapshot,
        duckdb_version="1.0",
    )

    assert ("title", "Governed Analytics Platform") in calls
    assert ("caption", "Projeto de portfólio profissional") in calls
    assert any(
        "transforma dados brutos" in value
        for kind, value in calls
        if kind == "markdown"
    )
    assert any(
        "fins demonstrativos" in value
        for kind, value in calls
        if kind == "caption"
    )
    assert metrics[:4] == [
        ("Registros governados", "2"),
        ("Governança de publicação", "Decisão auditável disponível"),
        ("Controles de privacidade", "16/16 PASS"),
        ("Qualidade e monitoramento", "Qualidade 24/25 · Monitoramento 12/12"),
    ]
    assert all(value != "Needs Review" for _, value in metrics[:4])
    assert snapshot.historical_decision == "Needs Review"
    assert any(
        kind == "write"
        and "plataforma analítica governada" in value
        and "15/100" not in value
        for kind, value in calls
    )
    assert (
        "caption",
        "Indicadores diagnósticos do ambiente demonstrativo.",
    ) in calls
    assert page_links == ["Explore Business Insights", "View Governance Decision"]
    assert ("info", "Raw Data") in calls
    assert ("success", "Trusted Analytics") in calls
    assert any(
        "github.com/samuelmaia-analytics" in value
        for kind, value in calls
        if kind == "markdown"
    )
    assert control_center_page.GOVERNANCE_LAB_NOTICE.startswith(
        "Interactive diagnostic environment"
    )


def test_portfolio_overview_uses_demonstration_fallbacks_without_evidence(
    monkeypatch,
) -> None:
    calls: list[tuple[str, str]] = []
    metrics: list[tuple[str, object]] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def caption(self, value: str) -> None:
            calls.append(("caption", value))

        def write(self, value: str) -> None:
            calls.append(("write", value))

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def expander(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
            return CapturingContainer()

    unavailable = CheckSummary(0, 0, 0, 0)
    snapshot = PublicationGovernanceSnapshot(
        run_id="Unavailable",
        historical_decision="Unavailable",
        shadow_decision="Unavailable",
        shadow_severity="Unavailable",
        residual_decision="Unavailable",
        residual_severity="Unavailable",
        inherent_score=None,
        residual_score=None,
        divergence_type="Unavailable",
        sensitive_data_protected=None,
        privacy=unavailable,
        schema=unavailable,
        business=unavailable,
        quality=unavailable,
        monitoring=unavailable,
        execution_provenance="Unavailable",
        content_provenance="Unavailable",
        source_fingerprint="Unavailable",
        published_fingerprint="Unavailable",
    )
    monkeypatch.setattr(executive_overview_page, "st", CapturingStreamlit())
    monkeypatch.setattr(
        executive_overview_page,
        "_render_operational_readiness_section",
        lambda _locale: None,
    )

    executive_overview_page.render_executive_overview(  # type: ignore[arg-type]
        df=pd.DataFrame({"value": [1, 2]}),
        classification_df=pd.DataFrame(
            {
                "lgpd_classification": ["non_personal"],
                "recommended_action": ["keep"],
            }
        ),
        risk_result={
            "score": 100,
            "total_score": 100,
            "risk_level": "high",
            "explanation": "Demonstration risk fixture",
            "summary": "Demonstration risk fixture",
            "components": {},
            "score_components": {},
            "per_component_points": {},
            "component_explanations": {},
            "publication_recommendation": "blocked",
            "recommendations": [],
        },
        quality_results={
            "total_rows": 2,
            "total_columns": 1,
            "null_pct_by_column": {},
            "columns_over_30pct_null": [],
            "duplicate_rows": 0,
            "dtypes": {"value": "int64"},
            "cardinality": {"value": 2},
            "possible_unique_keys": ["value"],
            "constant_columns": [],
            "checks": [],
            "failed_checks_count": 5,
        },
        locale="pt-BR",
        governance_snapshot=snapshot,
    )

    assert metrics[:4] == [
        ("Registros governados", "2"),
        ("Governança de publicação", "Decisão auditável disponível"),
        ("Controles de privacidade", "Controles demonstrados"),
        ("Qualidade e monitoramento", "Validações demonstradas"),
    ]
    primary_values = {str(value) for _, value in metrics[:4]}
    assert "0/0 PASS" not in primary_values
    assert "Unavailable" not in primary_values
    assert "Approved" not in primary_values

    headline = next(value for kind, value in calls if kind == "write")
    assert "100/100" not in headline
    assert "50/100" not in headline
    assert "5 falhas" not in headline
    assert ("Score de Risco LGPD", "100 / 100") in metrics
    assert ("Score de Qualidade", "50 / 100") in metrics
    assert (
        "caption",
        "Indicadores diagnósticos do ambiente demonstrativo.",
    ) in calls


def test_render_revenue_analytics_with_and_without_semantic_slices(monkeypatch) -> None:
    metrics: list[tuple[str, object]] = []
    tabs: list[str] = []
    titles: list[str] = []
    subtitles: list[str] = []
    captions: list[str] = []
    markdown_calls: list[str] = []
    plot_calls: list[tuple[str, pd.DataFrame, dict[str, object]]] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def subheader(self, value: str) -> None:
            subtitles.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def tabs(self, tab_names):  # type: ignore[no-untyped-def]
            tabs.extend(tab_names)
            return tuple(CapturingContainer() for _ in tab_names)

        def dataframe(self, frame: pd.DataFrame, **kwargs: object) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

    class CapturingPlotlyExpress:
        @staticmethod
        def _capture(
            kind: str, frame: pd.DataFrame, kwargs: dict[str, object]
        ) -> _FakeFigure:
            plot_calls.append((kind, frame.copy(), kwargs))
            return _FakeFigure()

        @staticmethod
        def bar(
            frame: pd.DataFrame, **kwargs: object
        ) -> _FakeFigure:
            return CapturingPlotlyExpress._capture("bar", frame, kwargs)

        @staticmethod
        def imshow(
            frame: pd.DataFrame, **kwargs: object
        ) -> _FakeFigure:
            return CapturingPlotlyExpress._capture("imshow", frame, kwargs)

    monkeypatch.setattr(revenue_page, "st", CapturingStreamlit())
    monkeypatch.setattr(revenue_page, "px", CapturingPlotlyExpress())

    df = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_year_month": ["2024-01", "2024-01", "2024-02"],
            "seller_key": [
                "seller_id_1a2b3c4d5e6f7g8h",
                "seller_id_8h7g6f5e4d3c2b1a",
                "seller_id_1a2b3c4d5e6f7g8h",
            ],
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
    original_df = df.copy(deep=True)
    original_category_slice = category_slice.copy(deep=True)
    original_cohort_slice = cohort_slice.copy(deep=True)

    monkeypatch.setattr(
        revenue_page,
        "_load_semantic_slice",
        lambda path: category_slice.copy()
        if "category_slice" in str(path)
        else cohort_slice.copy(),
    )
    revenue_page.render_revenue_analytics(df, locale="pt-BR")  # type: ignore[arg-type]

    assert titles == ["Business Insights"]
    assert metrics[:4] == [
        ("Receita total", "R$ 420,00"),
        ("Pedidos", "2"),
        ("Ticket médio", "R$ 210,00"),
        ("Sellers ativos", "2"),
    ]
    assert tabs == [
        "Evolução da receita",
        "Pareto por categoria",
        "Cohort",
        "Top Sellers",
    ]
    assert "Leitura executiva" in " ".join(markdown_calls)
    assert subtitles == [
        "Evolução mensal da receita",
        "Concentração de receita por categoria",
        "Top sellers por receita",
    ]
    assert any("dataset demonstrativo" in caption for caption in captions)
    assert any("análise de cohort" in caption for caption in captions)

    monthly_plot = next(
        (frame, kwargs)
        for kind, frame, kwargs in plot_calls
        if kind == "bar" and kwargs["x"] == "order_year_month"
    )
    assert monthly_plot[0]["revenue"].tolist() == [220.0, 200.0]
    assert "title" not in monthly_plot[1]
    assert monthly_plot[1]["labels"] == {
        "order_year_month": "Ano-mês",
        "revenue": "Receita",
    }
    category_plot = next(
        (frame, kwargs)
        for kind, frame, kwargs in plot_calls
        if kind == "bar" and kwargs["x"] == "category"
    )
    assert "title" not in category_plot[1]
    assert {kwargs["title"] for _, _, kwargs in plot_calls if "title" in kwargs} == {
        "Ticket médio por cohort",
        "Retenção por cohort (%)",
        "Top sellers por receita",
    }
    assert displayed_frames[0].columns.tolist() == [
        "Categoria",
        "Receita",
        "Cumulativo %",
    ]
    assert displayed_frames[0]["Receita"].tolist() == ["R$ 500,00", "R$ 300,00"]
    assert dataframe_options[0]["hide_index"] is True
    seller_plot = next(
        (frame, kwargs)
        for kind, frame, kwargs in plot_calls
        if kind == "bar" and kwargs["x"] == "seller_label"
    )
    assert seller_plot[0]["seller_key"].tolist() == [
        "seller_id_1a2b3c4d5e6f7g8h",
        "seller_id_8h7g6f5e4d3c2b1a",
    ]
    assert seller_plot[0]["seller_label"].tolist() == ["…5e6f7g8h", "…4d3c2b1a"]
    assert seller_plot[1]["hover_data"] == {
        "seller_key": True,
        "seller_label": False,
    }
    pd.testing.assert_frame_equal(df, original_df)
    pd.testing.assert_frame_equal(category_slice, original_category_slice)
    pd.testing.assert_frame_equal(cohort_slice, original_cohort_slice)

    monkeypatch.setattr(
        revenue_page, "_load_semantic_slice", lambda _path: pd.DataFrame()
    )
    revenue_page.render_revenue_analytics(df, locale="en-US")  # type: ignore[arg-type]


def test_render_seller_performance_with_and_without_data(monkeypatch) -> None:
    titles: list[str] = []
    markdown_calls: list[str] = []
    captions: list[str] = []
    metrics: list[tuple[str, object]] = []
    selectbox_calls: list[dict[str, object]] = []
    plot_calls: list[tuple[pd.DataFrame, dict[str, object]]] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []
    expanders: list[str] = []
    infos: list[str] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

        def selectbox(self, label: str, **kwargs: object):  # type: ignore[no-untyped-def]
            options = list(kwargs["options"])  # type: ignore[arg-type]
            format_func = kwargs.get("format_func")
            visual_options = (
                [format_func(option) for option in options]  # type: ignore[operator]
                if format_func is not None
                else options
            )
            selectbox_calls.append(
                {
                    "label": label,
                    "options": options,
                    "visual_options": visual_options,
                    "key": kwargs.get("key"),
                }
            )
            return options[0]

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def dataframe(self, frame: pd.DataFrame, **kwargs: object) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

        def expander(self, label: str, **_kwargs):  # type: ignore[no-untyped-def]
            expanders.append(label)
            return self

        def info(self, value: str) -> None:
            infos.append(value)

    class CapturingPlotlyExpress(_FakePlotlyExpress):
        @staticmethod
        def bar(frame: pd.DataFrame, **kwargs: object) -> _FakeFigure:
            plot_calls.append((frame.copy(), kwargs))
            return _FakeFigure()

    seller_count = 22
    seller_df = pd.DataFrame(
        {
            "seller_key": [
                f"seller_id_{index:016x}" for index in range(1, seller_count + 1)
            ],
            "seller_state": ["SP" if index % 2 else "RJ" for index in range(1, 23)],
            "seller_volume_tier": [
                ["long_tail", "scaled", "core", "strategic"][(index - 1) % 4]
                for index in range(1, 23)
            ],
            "total_items": list(range(101, 123)),
            "seller_order_count": list(range(1, 23)),
            "avg_ticket": [100.0] * seller_count,
            "avg_delivery_time_days": [5.0 + index for index in range(1, 23)],
            "delay_rate": [index / 100 for index in range(1, 23)],
            "avg_review_score": [4.0 + index / 100 for index in range(1, 23)],
        }
    )
    original = seller_df.copy(deep=True)
    monkeypatch.setattr(seller_page, "st", CapturingStreamlit())
    monkeypatch.setattr(seller_page, "px", CapturingPlotlyExpress())
    monkeypatch.setattr(seller_page, "_load_seller_slice", lambda: seller_df.copy())

    seller_page.render_seller_performance(locale="pt-BR")  # type: ignore[arg-type]

    assert titles == ["Desempenho de Sellers"]
    assert any("Visão de volume" in value for value in markdown_calls)
    assert "### Como interpretar esta página" in markdown_calls
    assert "### Leitura executiva" in markdown_calls
    assert any("dataset" not in value.lower() for value in captions)
    assert metrics == [
        ("Sellers ativos", "22"),
        ("Pedidos", "253"),
        ("Taxa média de atraso", "11,5%"),
        ("Tempo médio de entrega", "16,5 dias"),
    ]

    assert selectbox_calls == [
        {
            "label": "Faixa de volume",
            "options": ["all", "core", "long_tail", "scaled", "strategic"],
            "visual_options": [
                "Todos",
                "Core",
                "Cauda longa",
                "Em escala",
                "Estratégico",
            ],
            "key": "seller_perf_tier_filter",
        },
        {
            "label": "Estado",
            "options": ["all", "RJ", "SP"],
            "visual_options": ["Todos", "RJ", "SP"],
            "key": "seller_perf_state_filter",
        },
    ]

    tier_frame, tier_options = plot_calls[0]
    expected_tier = (
        original["seller_volume_tier"]
        .value_counts(dropna=False)
        .rename_axis("seller_volume_tier")
        .reset_index(name="count")
    )
    pd.testing.assert_frame_equal(
        tier_frame[["seller_volume_tier", "count"]], expected_tier
    )
    assert tier_options["orientation"] == "h"
    assert set(tier_frame["tier_label"]) == {
        "Cauda longa",
        "Em escala",
        "Core",
        "Estratégico",
    }

    sla_frame, sla_options = plot_calls[1]
    expected_sla = (
        original.groupby("seller_volume_tier", dropna=False)
        .agg(
            avg_delay_rate=("delay_rate", "mean"),
            avg_delivery_days=("avg_delivery_time_days", "mean"),
        )
        .reset_index()
    )
    expected_sla["avg_delay_rate"] = expected_sla["avg_delay_rate"] * 100
    pd.testing.assert_frame_equal(
        sla_frame[
            ["seller_volume_tier", "avg_delay_rate", "avg_delivery_days"]
        ],
        expected_sla,
    )
    assert sla_options["orientation"] == "h"

    assert len(displayed_frames) == 2
    executive_ranking, technical_ranking = displayed_frames
    assert dataframe_options == [
        {"width": "stretch", "hide_index": True},
        {"width": "stretch", "hide_index": True},
    ]
    assert expanders == ["Detalhes técnicos dos sellers"]
    assert len(executive_ranking) == 20
    assert len(technical_ranking) == 20
    expected_revenue = (
        pd.to_numeric(technical_ranking["avg_ticket"], errors="coerce").fillna(0)
        * pd.to_numeric(
            technical_ranking["seller_order_count"], errors="coerce"
        ).fillna(0)
    )
    pd.testing.assert_series_equal(
        technical_ranking["estimated_revenue"],
        expected_revenue,
        check_names=False,
    )
    assert technical_ranking["estimated_revenue"].is_monotonic_decreasing
    assert technical_ranking["seller_key"].tolist() == [
        f"seller_id_{index:016x}" for index in range(22, 2, -1)
    ]
    assert executive_ranking["Seller"].tolist() == [
        f"Seller • {value[-8:]}" for value in technical_ranking["seller_key"]
    ]
    assert executive_ranking["Ticket médio"].str.startswith("R$ ").all()
    assert executive_ranking["Taxa de atraso"].str.endswith("%").all()
    assert executive_ranking["Entrega média"].str.endswith(" dias").all()
    pd.testing.assert_frame_equal(seller_df, original)

    monkeypatch.setattr(seller_page, "_load_seller_slice", lambda: pd.DataFrame())
    seller_page.render_seller_performance(locale="en-US")  # type: ignore[arg-type]
    assert infos == ["Dados de sellers não disponíveis neste ambiente."]


def test_render_cohort_retention_with_and_without_data(monkeypatch) -> None:
    titles: list[str] = []
    subtitles: list[str] = []
    captions: list[str] = []
    markdown_calls: list[str] = []
    write_calls: list[str] = []
    metrics: list[tuple[str, object]] = []
    tabs: list[str] = []
    plot_calls: list[object] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []
    expanders: list[str] = []
    infos: list[str] = []
    imshow_frames: list[pd.DataFrame] = []
    imshow_options: list[dict[str, object]] = []
    merge_calls: list[dict[str, object]] = []
    pivot_calls: list[dict[str, object]] = []

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs) -> None:
            metrics.append((label, value))

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def subheader(self, value: str) -> None:
            subtitles.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def write(self, value: str) -> None:
            write_calls.append(value)

        def columns(self, count: int):  # type: ignore[no-untyped-def]
            return tuple(CapturingContainer() for _ in range(count))

        def tabs(self, tab_names):  # type: ignore[no-untyped-def]
            tabs.extend(tab_names)
            return tuple(CapturingContainer() for _ in tab_names)

        def plotly_chart(self, figure: object, **_kwargs) -> None:
            plot_calls.append(figure)

        def dataframe(self, frame: pd.DataFrame, **kwargs: object) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

        def expander(self, label: str, **_kwargs):  # type: ignore[no-untyped-def]
            expanders.append(label)
            return self

        def info(self, value: str) -> None:
            infos.append(value)

        def selectbox(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("Customer Retention must not introduce filters")

    class CapturingFigure:
        def __init__(self) -> None:
            self.trace_updates: list[dict[str, object]] = []
            self.xaxis_updates: list[dict[str, object]] = []
            self.yaxis_updates: list[dict[str, object]] = []

        def update_traces(self, **kwargs: object) -> None:
            self.trace_updates.append(kwargs)

        def update_xaxes(self, **kwargs: object) -> None:
            self.xaxis_updates.append(kwargs)

        def update_yaxes(self, **kwargs: object) -> None:
            self.yaxis_updates.append(kwargs)

    figures: list[CapturingFigure] = []

    class CapturingPlotlyExpress:
        @staticmethod
        def imshow(frame: pd.DataFrame, **kwargs: object) -> CapturingFigure:
            imshow_frames.append(frame.copy())
            imshow_options.append(kwargs)
            figure = CapturingFigure()
            figures.append(figure)
            return figure

    original_merge = pd.DataFrame.merge
    original_pivot_table = pd.DataFrame.pivot_table

    def capturing_merge(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        merge_calls.append(dict(kwargs))
        return original_merge(self, *args, **kwargs)

    def capturing_pivot_table(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        pivot_calls.append(dict(kwargs))
        return original_pivot_table(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "merge", capturing_merge)
    monkeypatch.setattr(pd.DataFrame, "pivot_table", capturing_pivot_table)
    monkeypatch.setattr(cohort_page, "st", CapturingStreamlit())
    monkeypatch.setattr(cohort_page, "px", CapturingPlotlyExpress())

    cohort_df = pd.DataFrame(
        {
            "purchase_cohort_month": [
                "2024-01",
                "2024-01",
                "2024-02",
                "2024-02",
                "2024-03",
            ],
            "cohort_order_month_number": [0, 1, 0, 1, 1],
            "customers": [100, 45, 0, 10, 5],
            "avg_ticket": [120.0, 115.0, 130.0, 125.0, 140.0],
        }
    )
    original = cohort_df.copy(deep=True)
    monkeypatch.setattr(cohort_page, "_load_cohort_slice", lambda: cohort_df.copy())
    cohort_page.render_cohort_retention(locale="pt-BR")  # type: ignore[arg-type]

    assert titles == ["Retenção de Clientes"]
    assert subtitles == [
        "Análise por cohorts para acompanhar a permanência de clientes ao longo "
        "dos meses após a primeira compra."
    ]
    assert (
        "A retenção compara, em cada cohort, a quantidade de clientes de cada mês "
        "relativo com o volume do mês inicial."
    ) in captions
    assert "### Como interpretar esta página" in markdown_calls
    assert any("O Mês 0 é o baseline" in value for value in write_calls)
    assert (
        "**Retenção = clientes no mês relativo ÷ clientes do Mês 0 × 100**"
        in markdown_calls
    )
    assert metrics == [
        ("Cohorts analisados", "1"),
        ("Período analisado", "2024-01 a 2024-03"),
        ("Meses relativos observados", "2"),
        ("Células com retenção calculável", "2"),
    ]
    assert "### Leitura executiva" in markdown_calls
    assert tabs == ["Retenção", "Ticket médio"]
    assert len(plot_calls) == 2

    assert merge_calls == [{"on": "purchase_cohort_month", "how": "left"}]
    assert [call["aggfunc"] for call in pivot_calls] == ["mean", "mean"]
    assert [call["values"] for call in pivot_calls] == [
        "retention_rate",
        "avg_ticket",
    ]
    assert all(call["index"] == "purchase_cohort_month" for call in pivot_calls)
    assert all(
        call["columns"] == "cohort_order_month_number" for call in pivot_calls
    )

    expected_retention_pivot = pd.DataFrame(
        [[100.0, 45.0]],
        index=pd.Index(["2024-01"], name="purchase_cohort_month"),
        columns=pd.Index([0, 1], name="cohort_order_month_number"),
    )
    pd.testing.assert_frame_equal(
        imshow_frames[0], expected_retention_pivot, check_dtype=False
    )
    expected_ticket_pivot = pd.DataFrame(
        [[120.0, 115.0], [130.0, 125.0], [float("nan"), 140.0]],
        index=pd.Index(
            ["2024-01", "2024-02", "2024-03"],
            name="purchase_cohort_month",
        ),
        columns=pd.Index([0, 1], name="cohort_order_month_number"),
    )
    pd.testing.assert_frame_equal(
        imshow_frames[1], expected_ticket_pivot, check_dtype=False
    )
    assert imshow_options[0] == {
        "text_auto": False,
        "aspect": "auto",
        "color_continuous_scale": "Teal",
        "title": "Matriz de retenção por cohort (%)",
        "labels": {
            "x": "Meses desde a primeira compra",
            "y": "Cohort de compra",
            "color": "Retenção (%)",
        },
    }
    assert imshow_options[1] == {
        "text_auto": False,
        "aspect": "auto",
        "color_continuous_scale": "Blues",
        "title": "Ticket médio por cohort",
        "labels": {
            "x": "Meses desde a primeira compra",
            "y": "Cohort de compra",
            "color": "Ticket médio",
        },
    }
    assert figures[0].trace_updates[0]["text"].tolist() == [
        ["100,0%", "45,0%"]
    ]
    assert figures[1].trace_updates[0]["text"].tolist() == [
        ["R$ 120,00", "R$ 115,00"],
        ["R$ 130,00", "R$ 125,00"],
        ["—", "R$ 140,00"],
    ]
    assert figures[0].xaxis_updates[0]["ticktext"] == ["Mês 0", "Mês 1"]
    assert figures[1].xaxis_updates[0]["ticktext"] == ["Mês 0", "Mês 1"]
    assert imshow_frames[0].columns.tolist() == [0, 1]
    assert imshow_frames[1].columns.tolist() == [0, 1]

    assert len(displayed_frames) == 2
    executive_table, technical_table = displayed_frames
    assert executive_table.columns.tolist() == [
        "Cohort",
        "Mês relativo",
        "Clientes",
        "Retenção",
        "Ticket médio",
    ]
    assert len(executive_table) == len(cohort_df)
    assert executive_table["Cohort"].tolist() == [
        "2024-01",
        "2024-01",
        "2024-02",
        "2024-02",
        "2024-03",
    ]
    assert executive_table["Mês relativo"].tolist() == [
        "Mês 0",
        "Mês 1",
        "Mês 0",
        "Mês 1",
        "Mês 1",
    ]
    assert executive_table["Clientes"].tolist() == ["100", "45", "0", "10", "5"]
    assert executive_table["Retenção"].tolist() == [
        "100,0%",
        "45,0%",
        "—",
        "—",
        "—",
    ]
    assert executive_table["Ticket médio"].tolist() == [
        "R$ 120,00",
        "R$ 115,00",
        "R$ 130,00",
        "R$ 125,00",
        "R$ 140,00",
    ]
    assert dataframe_options == [
        {"width": "stretch", "hide_index": True},
        {"width": "stretch", "hide_index": True},
    ]

    assert expanders == ["Detalhes técnicos da retenção"]
    assert technical_table.columns.tolist() == [
        "purchase_cohort_month",
        "cohort_order_month_number",
        "customers",
        "baseline_customers",
        "retention_rate",
        "avg_ticket",
    ]
    assert technical_table["cohort_order_month_number"].tolist() == [0, 1, 0, 1, 1]
    assert technical_table["baseline_customers"].iloc[:4].tolist() == [100, 100, 0, 0]
    assert pd.isna(technical_table["baseline_customers"].iloc[4])
    assert technical_table["retention_rate"].iloc[:2].tolist() == [100.0, 45.0]
    assert technical_table["retention_rate"].iloc[2:].isna().all()
    assert any("identificadores e cálculos" in value for value in captions)
    pd.testing.assert_frame_equal(cohort_df, original)

    monkeypatch.setattr(cohort_page, "_load_cohort_slice", lambda: pd.DataFrame())
    cohort_page.render_cohort_retention(locale="pt-BR")  # type: ignore[arg-type]
    monkeypatch.setattr(
        cohort_page,
        "_load_cohort_slice",
        lambda: pd.DataFrame({"purchase_cohort_month": ["2024-01"]}),
    )
    cohort_page.render_cohort_retention(locale="pt-BR")  # type: ignore[arg-type]
    assert infos == [
        "Dados de retenção não disponíveis neste ambiente.",
        "Dados de retenção não disponíveis neste ambiente.",
    ]


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
        "source_id;title;category\n" "phone_case_001;Phone Case;Accessories\n" ";;\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(genai_page, "GENAI_FEATURES_PATH", csv_path)
    loaded = genai_page._load_genai_features()
    assert len(loaded) == 1
    assert loaded.iloc[0]["source_id"] == "phone_case_001"


def test_render_data_catalog_with_filters_and_without_data(monkeypatch) -> None:
    titles: list[str] = []
    subtitles: list[str] = []
    captions: list[str] = []
    markdown_calls: list[str] = []
    write_calls: list[str] = []
    metrics: list[tuple[str, object]] = []
    displayed_frames: list[pd.DataFrame] = []
    dataframe_options: list[dict[str, object]] = []
    expanders: list[str] = []
    text_inputs: list[tuple[str, dict[str, object]]] = []
    multiselect_calls: list[tuple[str, dict[str, object]]] = []
    merge_calls: list[dict[str, object]] = []
    contains_calls: list[tuple[object, dict[str, object]]] = []
    isin_calls: list[list[object]] = []
    search_results = iter(["", "CUSTOMER", "", ""])
    classification_results = iter([[], [], ["indirect_identifier"], []])

    class CapturingContainer(_FakeContainer):
        def metric(self, label: str, value: object, **_kwargs: object) -> None:
            metrics.append((label, value))

        def dataframe(
            self, frame: pd.DataFrame, **kwargs: object
        ) -> None:
            displayed_frames.append(frame.copy())
            dataframe_options.append(kwargs)

    class CapturingStreamlit(CapturingContainer):
        def title(self, value: str) -> None:
            titles.append(value)

        def subheader(self, value: str) -> None:
            subtitles.append(value)

        def caption(self, value: str) -> None:
            captions.append(value)

        def markdown(self, value: str) -> None:
            markdown_calls.append(value)

        def write(self, value: str) -> None:
            write_calls.append(value)

        def columns(self, specification):  # type: ignore[no-untyped-def]
            count = specification if isinstance(specification, int) else len(specification)
            return tuple(CapturingContainer() for _ in range(count))

        def text_input(self, label: str, **kwargs: object) -> str:
            text_inputs.append((label, kwargs))
            return next(search_results)

        def multiselect(self, label: str, **kwargs: object) -> list[str]:
            multiselect_calls.append((label, kwargs))
            return next(classification_results)

        def expander(self, label: str, **_kwargs: object) -> CapturingContainer:
            expanders.append(label)
            return CapturingContainer()

    original_merge = pd.DataFrame.merge
    string_methods_type = type(pd.Series(["column"]).str)
    original_contains = string_methods_type.contains
    original_isin = pd.Series.isin

    def capturing_merge(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        merge_calls.append(dict(kwargs))
        return original_merge(self, *args, **kwargs)

    def capturing_contains(
        self, pattern, *args, **kwargs  # type: ignore[no-untyped-def]
    ):
        contains_calls.append((pattern, dict(kwargs)))
        return original_contains(self, pattern, *args, **kwargs)

    def capturing_isin(self, values):  # type: ignore[no-untyped-def]
        isin_calls.append(list(values))
        return original_isin(self, values)

    monkeypatch.setattr(pd.DataFrame, "merge", capturing_merge)
    monkeypatch.setattr(string_methods_type, "contains", capturing_contains)
    monkeypatch.setattr(pd.Series, "isin", capturing_isin)
    monkeypatch.setattr(data_catalog_page, "st", CapturingStreamlit())

    df = pd.DataFrame(
        {
            "customer_unique_id": pd.Series(["A", "A", None], dtype="object"),
            "PRICE": pd.Series([10, 20, 20], dtype="int64"),
            "notes": pd.Series(["ok", None, "ok"], dtype="object"),
            None: pd.Series([1.5, 2.5, 3.5], dtype="float64"),
        }
    )
    classification_df = pd.DataFrame(
        {
            "column_name": ["customer_unique_id", "PRICE", "notes", None],
            "dtype": ["object", "int64", "object", "float64"],
            "lgpd_classification": [
                "personal_data",
                "non_personal",
                "indirect_identifier",
                "sensitive_personal_data",
            ],
            "risk_level": ["high", "low", "medium", "high"],
            "recommended_action": ["mask", "keep", "review", "custom_action"],
            "reason": ["personal", "public", "indirect", "sensitive"],
        }
    )
    original_df = df.copy(deep=True)
    original_classification_df = classification_df.copy(deep=True)

    data_catalog_page.render_data_catalog(
        df, classification_df, locale="pt-BR"  # type: ignore[arg-type]
    )
    data_catalog_page.render_data_catalog(
        df, classification_df, locale="pt-BR"  # type: ignore[arg-type]
    )
    data_catalog_page.render_data_catalog(
        df, classification_df, locale="pt-BR"  # type: ignore[arg-type]
    )
    empty_df = df.iloc[0:0].copy()
    data_catalog_page.render_data_catalog(
        empty_df, classification_df, locale="pt-BR"  # type: ignore[arg-type]
    )

    assert titles == ["Catálogo de Dados"] * 4
    assert subtitles == [
        "Inventário técnico das colunas do ativo analítico, com perfil estrutural "
        "e classificação de governança."
    ] * 4
    assert (
        "A página apresenta metadados calculados sobre o dataset ativo e consome a "
        "classificação LGPD já produzida pelas regras de governança."
    ) in captions
    assert "### Como interpretar esta página" in markdown_calls
    assert any("Cada linha representa uma coluna" in value for value in write_calls)
    assert "### Leitura executiva" in markdown_calls
    assert any("não é uma decisão de publicação" in value for value in captions)
    assert metrics[:4] == [
        ("Colunas catalogadas", "4"),
        ("Dados pessoais", "1"),
        ("Identificadores indiretos", "1"),
        ("Colunas que exigem ação", "3"),
    ]
    assert any("**3 registros**" in value for value in markdown_calls)
    assert any("**0 registros**" in value for value in markdown_calls)

    assert text_inputs == [
        (
            "Buscar coluna",
            {
                "placeholder": "Ex.: customer_unique_id",
                "help": "Pesquisa apenas pelo nome técnico da coluna.",
                "key": "catalog_search",
            },
        )
    ] * 4
    assert [label for label, _kwargs in multiselect_calls] == [
        "Classificação LGPD"
    ] * 4
    expected_options = [
        "indirect_identifier",
        "non_personal",
        "personal_data",
        "sensitive_personal_data",
    ]
    assert all(call["options"] == expected_options for _, call in multiselect_calls)
    assert all(call["default"] == [] for _, call in multiselect_calls)
    assert all(call["key"] == "catalog_lgpd_filter" for _, call in multiselect_calls)
    format_func = multiselect_calls[0][1]["format_func"]
    assert callable(format_func)
    assert format_func("non_personal") == "Não pessoal"
    assert format_func("indirect_identifier") == "Identificador indireto"
    assert format_func("personal_data") == "Dado pessoal"
    assert format_func("sensitive_personal_data") == "Dado pessoal sensível"

    assert merge_calls == [
        {"on": "column_name", "how": "left"},
        {"on": "column_name", "how": "left"},
        {"on": "column_name", "how": "left"},
        {"on": "column_name", "how": "left"},
    ]
    assert contains_calls == [("CUSTOMER", {"case": False, "na": False})]
    assert ["indirect_identifier"] in isin_calls
    assert "Exibindo 4 de 4 colunas" in captions
    assert captions.count("Exibindo 1 de 4 colunas") == 2

    assert len(displayed_frames) == 8
    executive_table = displayed_frames[0]
    technical_table = displayed_frames[1]
    search_executive_table = displayed_frames[2]
    classification_executive_table = displayed_frames[4]
    empty_executive_table = displayed_frames[6]
    empty_technical_table = displayed_frames[7]

    assert executive_table.columns.tolist() == [
        "Coluna",
        "Tipo",
        "Nulos",
        "Valores distintos",
        "Classificação LGPD",
        "Ação recomendada",
    ]
    assert executive_table["Coluna"].tolist() == df.columns.tolist()
    assert executive_table["Tipo"].tolist() == [
        str(dtype) for dtype in df.dtypes
    ]
    assert executive_table["Nulos"].tolist() == [
        "33,33%",
        "0,00%",
        "33,33%",
        "0,00%",
    ]
    assert executive_table["Valores distintos"].tolist() == ["2", "2", "2", "3"]
    assert executive_table["Classificação LGPD"].tolist() == [
        "Dado pessoal",
        "Não pessoal",
        "Identificador indireto",
        "Dado pessoal sensível",
    ]
    assert executive_table["Ação recomendada"].tolist() == [
        "Mascarar",
        "Manter",
        "Revisar",
        "custom_action",
    ]
    assert technical_table.columns.tolist() == [
        "column_name",
        "dtype",
        "null_pct",
        "distinct_values",
        "lgpd_classification",
        "recommended_action",
    ]
    assert technical_table["column_name"].tolist() == df.columns.tolist()
    assert technical_table["dtype"].tolist() == [str(dtype) for dtype in df.dtypes]
    assert technical_table["null_pct"].tolist() == [33.33, 0.0, 33.33, 0.0]
    assert technical_table["distinct_values"].tolist() == [2, 2, 2, 3]
    assert technical_table["lgpd_classification"].tolist() == [
        "personal_data",
        "non_personal",
        "indirect_identifier",
        "sensitive_personal_data",
    ]
    assert technical_table["recommended_action"].tolist() == [
        "mask",
        "keep",
        "review",
        "custom_action",
    ]
    assert search_executive_table["Coluna"].tolist() == ["customer_unique_id"]
    assert classification_executive_table["Coluna"].tolist() == ["notes"]
    assert len(empty_executive_table) == len(df.columns)
    assert empty_executive_table["Coluna"].tolist() == df.columns.tolist()
    assert empty_executive_table["Nulos"].tolist() == ["—"] * len(df.columns)
    assert empty_technical_table["null_pct"].isna().all()
    assert empty_technical_table["distinct_values"].tolist() == [0, 0, 0, 0]
    assert dataframe_options == [
        {"width": "stretch", "hide_index": True}
    ] * 8
    assert expanders == ["Detalhes técnicos do catálogo"] * 4

    pd.testing.assert_frame_equal(df, original_df)
    pd.testing.assert_frame_equal(classification_df, original_classification_df)

    source = Path(data_catalog_page.__file__).read_text(encoding="utf-8")
    assert '"dtype": [str(dtype) for dtype in df.dtypes]' in source
    assert '"null_pct": (df.isna().mean() * 100).round(2).values' in source
    assert "nunique(dropna=False)" in source
    assert 'on="column_name"' in source
    assert 'how="left"' in source
    assert ".str.contains(search, case=False, na=False)" in source
    assert ".isin(selected_classifications)" in source
    assert "groupby(" not in source
    assert "threshold" not in source.lower()
    assert ".head(" not in source
    assert "classify_dataframe_columns" not in source
