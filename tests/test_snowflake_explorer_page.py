from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

import app.pages.snowflake_explorer as page


class _Container:
    def __init__(self, streamlit: _Streamlit, scope: str) -> None:
        self._streamlit = streamlit
        self._scope = scope
        self._previous_scope = "main"

    def __enter__(self) -> _Container:
        self._previous_scope = self._streamlit.scope
        self._streamlit.scope = self._scope
        return self

    def __exit__(self, *_: object) -> None:
        self._streamlit.scope = self._previous_scope

    def metric(self, label: str, value: object) -> None:
        self._streamlit.metrics.append((self._scope, label, value))

    def caption(self, value: object) -> None:
        self._streamlit.records.append(("caption", self._scope, str(value)))

    def markdown(self, value: object) -> None:
        self._streamlit.records.append(("markdown", self._scope, str(value)))


class _Streamlit:
    def __init__(
        self,
        *,
        clicked: set[str] | None = None,
        sql: str = "SELECT CURRENT_DATE()",
    ) -> None:
        self.clicked = clicked or set()
        self.sql = sql
        self.scope = "main"
        self.records: list[tuple[str, str, str]] = []
        self.metrics: list[tuple[str, str, object]] = []
        self.buttons: list[str] = []
        self.text_areas: list[tuple[str, str, int]] = []
        self.frames: list[pd.DataFrame] = []
        self.frame_options: list[dict[str, object]] = []

    def _record(self, kind: str, value: object) -> None:
        self.records.append((kind, self.scope, str(value)))

    def title(self, value: object) -> None:
        self._record("title", value)

    def markdown(self, value: object) -> None:
        self._record("markdown", value)

    def caption(self, value: object) -> None:
        self._record("caption", value)

    def write(self, value: object) -> None:
        self._record("write", value)

    def warning(self, value: object) -> None:
        self._record("warning", value)

    def info(self, value: object) -> None:
        self._record("info", value)

    def error(self, value: object) -> None:
        self._record("error", value)

    def code(self, value: object, **kwargs: object) -> None:
        self._record("code", value)
        self.records.append(("code_options", self.scope, repr(kwargs)))

    def columns(self, count: int) -> list[_Container]:
        return [_Container(self, f"column:{index}") for index in range(count)]

    def expander(self, label: str) -> _Container:
        self._record("expander", label)
        return _Container(self, f"expander:{label}")

    def button(self, label: str) -> bool:
        self.buttons.append(label)
        return label in self.clicked

    def text_area(self, label: str, *, value: str, height: int) -> str:
        self.text_areas.append((label, value, height))
        return self.sql

    def dataframe(self, frame: pd.DataFrame, **kwargs: object) -> None:
        self.frames.append(frame.copy(deep=True))
        self.frame_options.append(dict(kwargs))

    def rendered_text(self, *, scope: str | None = None) -> str:
        return "\n".join(
            value
            for _kind, item_scope, value in self.records
            if scope is None or item_scope == scope
        )


class _Connector:
    def __init__(
        self,
        *,
        tables: list[dict[str, str]] | None = None,
        result: pd.DataFrame | None = None,
        list_error: Exception | None = None,
        query_error: Exception | None = None,
    ) -> None:
        self.tables = [] if tables is None else tables
        self.result = pd.DataFrame() if result is None else result
        self.list_error = list_error
        self.query_error = query_error
        self.enter_count = 0
        self.exit_count = 0
        self.list_count = 0
        self.queries: list[str] = []

    def __enter__(self) -> _Connector:
        self.enter_count += 1
        return self

    def __exit__(self, *_: object) -> None:
        self.exit_count += 1

    def list_tables(self) -> list[dict[str, str]]:
        self.list_count += 1
        if self.list_error is not None:
            raise self.list_error
        return self.tables

    def query(self, sql: str) -> pd.DataFrame:
        self.queries.append(sql)
        if self.query_error is not None:
            raise self.query_error
        return self.result


def _config() -> page.SnowflakeConfig:
    return page.SnowflakeConfig(
        account="account-test",
        user="user-test",
        password="SECRET-MUST-NOT-BE-RENDERED",
        warehouse="warehouse-test",
        database="database-test",
        schema="schema-test",
        role="role-test",
    )


def _install_fakes(
    monkeypatch: pytest.MonkeyPatch,
    streamlit: _Streamlit,
    *,
    connector: _Connector | None = None,
    missing_config: bool = False,
) -> list[_Connector]:
    monkeypatch.setattr(page, "st", streamlit)
    if missing_config:
        def raise_missing_config() -> page.SnowflakeConfig:
            raise EnvironmentError("Missing Snowflake env vars: SNOWFLAKE_ACCOUNT")

        monkeypatch.setattr(
            page.SnowflakeConfig,
            "from_env",
            staticmethod(raise_missing_config),
        )
    else:
        config = _config()
        monkeypatch.setattr(
            page.SnowflakeConfig,
            "from_env",
            staticmethod(lambda: config),
        )

    connector_calls: list[_Connector] = []

    def connector_factory() -> _Connector:
        fake = connector or _Connector()
        connector_calls.append(fake)
        return fake

    monkeypatch.setattr(page, "get_snowflake_connector", connector_factory)
    return connector_calls


def test_render_is_callable_and_missing_config_returns_without_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    streamlit = _Streamlit()
    connector_calls = _install_fakes(
        monkeypatch,
        streamlit,
        missing_config=True,
    )

    assert callable(page.render_snowflake_explorer)
    page.render_snowflake_explorer("pt-BR")

    rendered = streamlit.rendered_text()
    assert "Integração Snowflake" in rendered
    assert "Configuração Snowflake incompleta neste ambiente." in rendered
    assert "SNOWFLAKE_ACCOUNT" in rendered
    assert "Missing Snowflake env vars" in rendered
    assert connector_calls == []


@pytest.mark.parametrize(
    ("locale", "title", "refresh", "run", "operation_warning"),
    [
        (
            "pt-BR",
            "Integração Snowflake",
            "Atualizar",
            "Executar",
            "Operações sob demanda",
        ),
        (
            "en-US",
            "Snowflake Integration",
            "Refresh",
            "Run",
            "On-demand operations",
        ),
    ],
)
def test_render_configured_page_is_inert_until_user_action(
    monkeypatch: pytest.MonkeyPatch,
    locale: str,
    title: str,
    refresh: str,
    run: str,
    operation_warning: str,
) -> None:
    streamlit = _Streamlit()
    connector_calls = _install_fakes(monkeypatch, streamlit)

    page.render_snowflake_explorer(locale)

    rendered = streamlit.rendered_text()
    main_text = streamlit.rendered_text(scope="main")
    assert title in rendered
    assert operation_warning in rendered
    metric_values = [str(value) for _scope, _label, value in streamlit.metrics]
    assert any(
        "Not verified" in value or "Não verificada" in value
        for value in metric_values
    )
    assert "local e limitada" in rendered or "local and limited" in rendered
    assert "somente SELECT" not in rendered
    assert "only SELECT" not in rendered
    assert refresh in streamlit.buttons
    assert run in streamlit.buttons
    assert streamlit.text_areas == [("SQL", "SELECT CURRENT_DATE()", 120)]
    assert connector_calls == []
    assert "account-test" not in main_text
    assert "account-test" in rendered
    assert "SECRET-MUST-NOT-BE-RENDERED" not in rendered


def test_refresh_lists_tables_once_without_mutating_values_or_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tables = [
        {"table": "SECOND", "database": "DB", "schema": "RAW"},
        {"table": "FIRST", "database": "DB", "schema": "CURATED"},
    ]
    original_tables = deepcopy(tables)
    connector = _Connector(tables=tables)
    streamlit = _Streamlit(clicked={"Atualizar"})
    connector_calls = _install_fakes(
        monkeypatch,
        streamlit,
        connector=connector,
    )

    page.render_snowflake_explorer("pt-BR")

    assert connector_calls == [connector]
    assert connector.enter_count == 1
    assert connector.exit_count == 1
    assert connector.list_count == 1
    assert connector.queries == []
    assert tables == original_tables
    assert len(streamlit.frames) == 1
    assert list(streamlit.frames[0].columns) == ["Tabela", "Database", "Schema"]
    assert streamlit.frames[0].to_dict("records") == [
        {"Tabela": "SECOND", "Database": "DB", "Schema": "RAW"},
        {"Tabela": "FIRST", "Database": "DB", "Schema": "CURATED"},
    ]
    assert streamlit.frame_options[0]["hide_index"] is True


def test_run_sends_exact_sql_and_blocked_prefix_never_reaches_connector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sql = "  SELECT CURRENT_DATE() AS current_date  "
    result = pd.DataFrame({"CURRENT_DATE()": ["2026-08-21"]})
    original_result = result.copy(deep=True)
    connector = _Connector(result=result)
    streamlit = _Streamlit(clicked={"Executar"}, sql=sql)
    connector_calls = _install_fakes(
        monkeypatch,
        streamlit,
        connector=connector,
    )

    page.render_snowflake_explorer("pt-BR")

    assert connector_calls == [connector]
    assert connector.queries == [sql]
    assert connector.enter_count == 1
    assert connector.exit_count == 1
    pd.testing.assert_frame_equal(result, original_result)
    pd.testing.assert_frame_equal(streamlit.frames[0], original_result)
    assert streamlit.frame_options[0]["hide_index"] is True
    assert "Resultado retornado pela consulta executada sob demanda." in (
        streamlit.rendered_text()
    )

    blocked_streamlit = _Streamlit(clicked={"Executar"}, sql="DELETE FROM sample")
    blocked_calls = _install_fakes(monkeypatch, blocked_streamlit)
    page.render_snowflake_explorer("pt-BR")

    assert blocked_calls == []
    assert "bloqueada pela validação local" in blocked_streamlit.rendered_text()


def test_empty_tables_and_operational_errors_preserve_fallbacks_and_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_connector = _Connector(tables=[])
    empty_streamlit = _Streamlit(clicked={"Atualizar"})
    _install_fakes(monkeypatch, empty_streamlit, connector=empty_connector)

    page.render_snowflake_explorer("pt-BR")

    assert "Nenhuma tabela encontrada." in empty_streamlit.rendered_text()

    list_error = RuntimeError("technical-list-error")
    error_connector = _Connector(list_error=list_error)
    error_streamlit = _Streamlit(clicked={"Atualizar"})
    _install_fakes(monkeypatch, error_streamlit, connector=error_connector)

    page.render_snowflake_explorer("pt-BR")

    rendered = error_streamlit.rendered_text()
    assert "Não foi possível listar as tabelas." in rendered
    assert "technical-list-error" in rendered


def test_page_source_adds_no_external_or_persistent_operations() -> None:
    source = Path(page.__file__).read_text(encoding="utf-8")

    assert ".health_check(" not in source
    assert "snowflake.connector.connect" not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "subprocess." not in source
    assert "os.system(" not in source
    assert ".write_text(" not in source
    assert ".write_bytes(" not in source
    assert ".to_csv(" not in source
    assert ".to_json(" not in source
    assert "FastAPI" not in source
    assert "dbt" in source  # limitation copy only; no dbt integration is imported
    assert "import dbt" not in source
    assert "from dbt" not in source
