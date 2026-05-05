from __future__ import annotations

import importlib
from types import SimpleNamespace

import pandas as pd

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

    fake_st = SimpleNamespace(sidebar=FakeSidebar())
    monkeypatch.setattr(context_module, "st", fake_st)
    monkeypatch.setattr(context_module.pd, "read_csv", lambda _uploaded: expected.copy())

    result = context_module.load_input_dataframe("pt-BR")
    pd.testing.assert_frame_equal(result, expected)


def test_main_entrypoints_are_callable() -> None:
    assert callable(main_module.main)
    assert callable(main_module._render_executive_page)
    assert callable(main_module._render_catalog_page)
    assert callable(main_module._render_lgpd_page)
    assert callable(main_module._render_quality_page)
    assert callable(main_module._render_eda_page)
    assert callable(main_module._render_report_page)
    assert callable(main_module._render_control_center_page)


def test_main_builds_navigation_and_runs_selected_page(monkeypatch) -> None:
    calls: list[str] = []

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
        def Page(fn, **_kwargs):  # type: ignore[no-untyped-def]
            calls.append("page")
            return fn

        @staticmethod
        def navigation(*_args, **_kwargs):  # type: ignore[no-untyped-def]
            return FakeNavigation()

    monkeypatch.setattr(main_module, "st", FakeStreamlit())
    monkeypatch.setattr(main_module, "build_locale_selector", lambda: "pt-BR")
    monkeypatch.setattr(main_module, "t", lambda _key, _locale: "x")
    monkeypatch.setattr(main_module, "build_context", lambda _locale: SimpleNamespace())
    monkeypatch.setattr(main_module, "_render_executive_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_catalog_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_lgpd_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_quality_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_eda_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_report_page", lambda _context, _locale: None)
    monkeypatch.setattr(main_module, "_render_control_center_page", lambda _context, _locale: None)

    main_module.main()

    assert calls.count("page") == 7
    assert "navigation_run" in calls
