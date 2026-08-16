from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import app.components.cards as cards
import app.pages.cohort_retention as cohort_page
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
        "source_id;title;category\n" "phone_case_001;Phone Case;Accessories\n" ";;\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(genai_page, "GENAI_FEATURES_PATH", csv_path)
    loaded = genai_page._load_genai_features()
    assert len(loaded) == 1
    assert loaded.iloc[0]["source_id"] == "phone_case_001"
