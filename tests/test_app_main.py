from __future__ import annotations

import importlib
from types import SimpleNamespace

import pandas as pd
import pytest

import app.context as context_module
import app.main as main_module


def test_import_app_main_module_without_errors() -> None:
    module = importlib.import_module("app.main")
    assert module is not None


def test_load_input_dataframe_mocks_io_and_csv_read(monkeypatch) -> None:
    expected = pd.DataFrame({"a": [1], "b": ["x"]})

    class FakeSidebar:
        def header(self, *_args, **_kwargs) -> None:
            return None

        def file_uploader(self, *_args, **_kwargs):
            return SimpleNamespace(name="input.csv")

        def toggle(self, *_args, **_kwargs) -> bool:
            return False

        def caption(self, *_args, **_kwargs) -> None:
            return None

    fake_st = SimpleNamespace(sidebar=FakeSidebar())
    monkeypatch.setattr(context_module, "st", fake_st)
    monkeypatch.setattr(
        context_module.pd, "read_csv", lambda _uploaded: expected.copy()
    )

    result = context_module.load_input_dataframe("pt-BR")
    pd.testing.assert_frame_equal(result, expected)
    assert result.attrs["uses_persisted_governance"] is False


def test_platform_source_distinguishes_published_data_from_sample(monkeypatch) -> None:
    monkeypatch.setattr(context_module, "load_dataset", lambda _path: pd.DataFrame({"value": [1]}))
    published = context_module._load_platform_dataframe(context_module.DEFAULT_PUBLISHED_DATASET)
    sample = context_module._load_platform_dataframe(context_module.DEFAULT_SAMPLE_DATASET)
    assert published.attrs["uses_persisted_governance"] is True
    assert sample.attrs["uses_persisted_governance"] is False


def test_build_context_passes_provenance_as_separate_cache_argument(monkeypatch) -> None:
    dataframe = pd.DataFrame({"value": [1]})
    dataframe.attrs["uses_persisted_governance"] = False
    calls = []
    monkeypatch.setattr(context_module, "load_input_dataframe", lambda _locale: dataframe)
    monkeypatch.setattr(
        context_module, "_build_context_from_dataframe",
        lambda frame, **kwargs: calls.append((frame, kwargs)),
    )
    context_module.build_context("pt-BR")
    dataframe.attrs["uses_persisted_governance"] = True
    context_module.build_context("pt-BR")
    assert [kwargs["uses_persisted_governance"] for _, kwargs in calls] == [False, True]


def test_uploaded_parquet_cannot_claim_published_provenance(monkeypatch) -> None:
    dataframe = pd.DataFrame({"value": [1]})
    dataframe.attrs["uses_persisted_governance"] = True
    sidebar = SimpleNamespace(
        header=lambda *_args: None,
        file_uploader=lambda *_args, **_kwargs: SimpleNamespace(name="input.parquet"),
        toggle=lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(context_module, "st", SimpleNamespace(sidebar=sidebar))
    monkeypatch.setattr(context_module, "_render_data_freshness_sidebar", lambda _locale: None)
    monkeypatch.setattr(context_module.pd, "read_parquet", lambda _uploaded: dataframe)
    assert context_module.load_input_dataframe("pt-BR").attrs["uses_persisted_governance"] is False


def test_context_for_upload_does_not_write_shared_reports(monkeypatch) -> None:
    dataframe = pd.DataFrame({"value": [1]})
    monkeypatch.setattr(context_module, "classify_dataframe_columns", lambda _frame: pd.DataFrame())
    monkeypatch.setattr(context_module, "run_data_quality_checks", lambda _frame: {})
    monkeypatch.setattr(context_module, "generate_data_quality_table", lambda _frame: pd.DataFrame())
    monkeypatch.setattr(context_module, "calculate_privacy_risk_score", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(context_module, "generate_markdown_reports", lambda *_args, **_kwargs: pytest.fail("Upload must not overwrite reports"))
    context = context_module._build_context_from_dataframe.__wrapped__(dataframe, uses_persisted_governance=False)
    assert context.report_paths == {}
    assert context.uses_persisted_governance is False


def test_main_entrypoints_are_callable() -> None:
    assert callable(main_module.main)
    assert callable(main_module._render_executive_page)
    assert callable(main_module._render_catalog_page)
    assert callable(main_module._render_lgpd_page)
    assert callable(main_module._render_quality_page)
    assert callable(main_module._render_eda_page)
    assert callable(main_module._render_revenue_page)
    assert callable(main_module._render_seller_performance_page)
    assert callable(main_module._render_cohort_retention_page)
    assert callable(main_module._render_genai_page)
    assert callable(main_module._render_assistant_page)
    assert callable(main_module._render_report_page)
    assert callable(main_module._render_control_center_page)
    assert callable(main_module._render_n8n_automation_page)
    assert callable(main_module._render_publication_governance_page)
    assert callable(main_module._render_snowflake_page)


def test_main_builds_navigation_and_runs_selected_page(monkeypatch) -> None:
    calls: list[str] = []
    url_paths: list[str] = []
    navigation_titles: list[str] = []
    registered_pages: list[SimpleNamespace] = []
    eda_calls: list[tuple[object, str]] = []
    context = SimpleNamespace()

    class FakeNavigation:
        def run(self) -> None:
            calls.append("navigation_run")

    class FakeStreamlit:
        @staticmethod
        def title(_value: str) -> None:
            calls.append("title")

        @staticmethod
        def caption(_value: str) -> None:
            calls.append("caption")

        @staticmethod
        def Page(fn, **kwargs):  # type: ignore[no-untyped-def]
            calls.append("page")
            url_paths.append(str(kwargs.get("url_path", "")))
            page = SimpleNamespace(
                fn=fn,
                title=str(kwargs.get("title", "")),
                icon=str(kwargs.get("icon", "")),
                url_path=str(kwargs.get("url_path", "")),
            )
            registered_pages.append(page)
            return page

        @staticmethod
        def navigation(*_args, **kwargs):  # type: ignore[no-untyped-def]
            navigation_titles.extend(page.title for page in kwargs["pages"])
            return FakeNavigation()

    monkeypatch.setattr(main_module, "st", FakeStreamlit())
    monkeypatch.setattr(main_module, "build_locale_selector", lambda: "pt-BR")
    monkeypatch.setattr(main_module, "build_context", lambda _locale: context)
    monkeypatch.setattr(
        main_module, "_render_executive_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_catalog_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_lgpd_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_quality_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module,
        "_render_eda_page",
        lambda in_context, in_locale: eda_calls.append((in_context, in_locale)),
    )
    monkeypatch.setattr(
        main_module, "_render_revenue_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_seller_performance_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_cohort_retention_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_genai_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_report_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_control_center_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module, "_render_n8n_automation_page", lambda _context, _locale: None
    )
    monkeypatch.setattr(
        main_module,
        "_render_publication_governance_page",
        lambda _context, _locale: None,
    )
    monkeypatch.setattr(
        main_module, "_render_snowflake_page", lambda _context, _locale: None
    )

    main_module.main()

    assert calls.count("page") == 15
    expected_routes = {
        "Portfolio Overview": "executive-overview",
        "Business Insights": "revenue-analytics",
        "Publication Governance": "publication-governance",
        "Privacy & LGPD Controls": "lgpd-privacy-risk",
        "Data Quality": "data-quality",
        "Seller Performance": "seller-performance",
        "Customer Retention": "cohort-retention",
        "Data Catalog": "data-catalog",
        "Technical Analysis": "technical-analysis",
        "Governance Evidence": "governance-report",
        "Governance Lab": "governance-control-center",
        "Automation & Orchestration": "n8n-automation",
        "GenAI Experiment": "genai-insights",
        "Assistente de Governan\u00e7a": "governance-assistant",
        "Snowflake Integration": "snowflake-explorer",
    }
    registered_routes = {page.title: page.url_path for page in registered_pages}
    assert len(registered_pages) == len(expected_routes)
    assert len(registered_routes) == len(expected_routes)
    assert len(set(url_paths)) == len(expected_routes)
    assert set(url_paths) == set(expected_routes.values())
    assert registered_routes == expected_routes
    assert "eda" not in url_paths
    assert navigation_titles == [
        "Portfolio Overview",
        "Business Insights",
        "Publication Governance",
        "Privacy & LGPD Controls",
        "Data Quality",
        "Seller Performance",
        "Customer Retention",
        "Data Catalog",
        "Technical Analysis",
        "Governance Evidence",
        "Governance Lab",
        "Automation & Orchestration",
        "GenAI Experiment",
        "Assistente de Governan\u00e7a",
        "Snowflake Integration",
    ]
    technical_page = next(
        page for page in registered_pages if page.title == "Technical Analysis"
    )
    assert technical_page.title == "Technical Analysis"
    assert technical_page.icon == ":material/monitoring:"
    assert technical_page.url_path == "technical-analysis"
    assert callable(technical_page.fn)
    technical_page.fn()
    assert eda_calls == [(context, "pt-BR")]
    assert "navigation_run" in calls
