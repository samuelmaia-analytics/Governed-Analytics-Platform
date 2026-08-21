from __future__ import annotations

import ast
import inspect
import json
from copy import deepcopy
from pathlib import Path
from types import TracebackType
from typing import Any

import pytest

import app.pages.n8n_automation as n8n_page


class _FakeMetricColumn:
    def __init__(self, owner: _FakeStreamlit) -> None:
        self.owner = owner

    def metric(self, label: str, value: object) -> None:
        self.owner.metrics.append((label, value))


class _FakeExpander:
    def __enter__(self) -> _FakeExpander:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        return None


class _FakeStreamlit:
    def __init__(self) -> None:
        self.titles: list[str] = []
        self.markdowns: list[str] = []
        self.captions: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.writes: list[object] = []
        self.metrics: list[tuple[str, object]] = []
        self.dataframes: list[tuple[object, dict[str, object]]] = []
        self.selectbox_calls: list[tuple[str, list[str]]] = []
        self.json_payloads: list[object] = []
        self.expanders: list[str] = []

    def title(self, value: str) -> None:
        self.titles.append(value)

    def markdown(self, value: str) -> None:
        self.markdowns.append(value)

    def caption(self, value: str) -> None:
        self.captions.append(value)

    def warning(self, value: str) -> None:
        self.warnings.append(value)

    def info(self, value: str) -> None:
        self.infos.append(value)

    def write(self, value: object) -> None:
        self.writes.append(value)

    def columns(self, count: int) -> list[_FakeMetricColumn]:
        return [_FakeMetricColumn(self) for _index in range(count)]

    def dataframe(self, data: object, **kwargs: object) -> None:
        self.dataframes.append((deepcopy(data), dict(kwargs)))

    def selectbox(self, label: str, options: list[str]) -> str:
        copied_options = list(options)
        self.selectbox_calls.append((label, copied_options))
        return copied_options[0]

    def expander(self, label: str, **_kwargs: object) -> _FakeExpander:
        self.expanders.append(label)
        return _FakeExpander()

    def json(self, payload: object) -> None:
        self.json_payloads.append(deepcopy(payload))


def _find_list_table(
    fake_st: _FakeStreamlit, expected_keys: set[str]
) -> tuple[list[dict[str, Any]], dict[str, object]]:
    for data, kwargs in fake_st.dataframes:
        if (
            isinstance(data, list)
            and data
            and isinstance(data[0], dict)
            and set(data[0]) == expected_keys
        ):
            return data, kwargs
    raise AssertionError(f"Table with keys {expected_keys!r} was not rendered")


def test_workflow_rows_preserves_payload_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    workflow_files = [Path("first.json"), Path("fallback_name.json"), Path("bad.json")]
    payloads: dict[Path, dict[str, Any]] = {
        workflow_files[0]: {
            "name": "First Workflow",
            "nodes": [{"name": "A"}, {"name": "B"}],
        },
        workflow_files[1]: {"nodes": [{"name": "Only"}]},
        workflow_files[2]: {},
    }
    original_payloads = deepcopy(payloads)
    monkeypatch.setattr(n8n_page, "read_json_safe", lambda path: payloads[path])
    monkeypatch.setattr(n8n_page, "relative_path", lambda path: path.as_posix())

    rows = n8n_page._workflow_rows(workflow_files)

    assert callable(n8n_page.render_n8n_automation)
    signature = inspect.signature(n8n_page.render_n8n_automation)
    assert list(signature.parameters) == []
    assert rows == [
        {
            "workflow_file": "first.json",
            "workflow_name": "First Workflow",
            "status": "importable JSON",
            "node_count": 2,
        },
        {
            "workflow_file": "fallback_name.json",
            "workflow_name": "fallback_name",
            "status": "importable JSON",
            "node_count": 1,
        },
        {
            "workflow_file": "bad.json",
            "workflow_name": "bad",
            "status": "read error",
            "node_count": 0,
        },
    ]
    assert payloads == original_payloads


def test_render_n8n_automation_is_read_only_and_preserves_templates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeStreamlit()
    diagnostics_calls: list[bool] = []
    workflow_files = sorted(n8n_page.WORKFLOWS_DIR.glob("*.json"))
    protected_paths = [
        *workflow_files,
        n8n_page.PIPELINE_LOG_PATH,
        n8n_page.PUBLICATION_DECISION_PATH,
        n8n_page.DOCS_DIR / "n8n_automation.md",
    ]
    original_bytes = {path: path.read_bytes() for path in protected_paths}
    original_payloads = {
        path: json.loads(content.decode("utf-8"))
        for path, content in original_bytes.items()
        if path.suffix == ".json" and path.parent == n8n_page.WORKFLOWS_DIR
    }
    monkeypatch.setattr(n8n_page, "st", fake_st)
    monkeypatch.setattr(
        n8n_page,
        "render_artifact_diagnostics",
        lambda: diagnostics_calls.append(True),
    )

    n8n_page.render_n8n_automation()

    assert fake_st.titles == ["Automação e Orquestração"]
    assert any("somente demonstrativa e read-only" in text for text in fake_st.captions)
    assert any("nenhuma execução é iniciada aqui" in text for text in fake_st.warnings)
    assert fake_st.metrics == [
        ("Templates encontrados", 2),
        ("Nodes declarados", 14),
        ("Artefatos disponíveis", 4),
    ]
    assert diagnostics_calls == [True]

    technical_workflows, technical_workflow_kwargs = _find_list_table(
        fake_st,
        {"workflow_file", "workflow_name", "status", "node_count"},
    )
    assert technical_workflow_kwargs["hide_index"] is True
    assert [row["node_count"] for row in technical_workflows] == [4, 10]
    assert [row["status"] for row in technical_workflows] == [
        "importable JSON",
        "importable JSON",
    ]
    workflow_presentation, workflow_presentation_kwargs = _find_list_table(
        fake_st,
        {"Arquivo", "Workflow", "Estado do arquivo", "Nodes declarados"},
    )
    assert workflow_presentation_kwargs["hide_index"] is True
    assert [row["Estado do arquivo"] for row in workflow_presentation] == [
        "JSON disponível para inspeção",
        "JSON disponível para inspeção",
    ]
    assert any(
        "Não representa validação de schema" in text for text in fake_st.captions
    )

    artifact_presentation, artifact_kwargs = _find_list_table(
        fake_st, {"Artefato", "Estado"}
    )
    assert artifact_kwargs["hide_index"] is True
    assert [row["Artefato"] for row in artifact_presentation] == [
        "Templates n8n",
        "Logs de execução do pipeline",
        "Decisão de publicação persistida",
        "Documentação da automação",
    ]
    assert {row["Estado"] for row in artifact_presentation} == {"Disponível"}
    assert any(
        "indica apenas que o artefato existe" in text for text in fake_st.captions
    )

    expected_options = [n8n_page.relative_path(path) for path in workflow_files]
    assert fake_st.selectbox_calls == [("Inspecionar workflow", expected_options)]
    selected_payload = original_payloads[workflow_files[0]]
    assert fake_st.json_payloads == [selected_payload]
    assert "JSON técnico do workflow" in fake_st.expanders
    assert "Detalhes técnicos da automação" in fake_st.expanders

    technical_nodes, technical_node_kwargs = _find_list_table(
        fake_st, {"node", "type", "notes"}
    )
    assert technical_node_kwargs["hide_index"] is True
    expected_error_nodes = [
        "Error Trigger",
        "Extract Error Metadata",
        "Register Error Log",
        "Send Error Alert",
    ]
    assert [row["node"] for row in technical_nodes] == expected_error_nodes
    node_presentation, node_presentation_kwargs = _find_list_table(
        fake_st, {"Etapa", "Node", "Tipo técnico", "Configuração resumida"}
    )
    assert node_presentation_kwargs["hide_index"] is True
    assert [row["Node"] for row in node_presentation] == expected_error_nodes
    assert [row["Etapa"] for row in node_presentation] == [
        "Disparo de erro",
        "Extrair metadados do erro",
        "Registrar log de erro",
        "Enviar alerta de erro",
    ]

    main_payload = original_payloads[workflow_files[1]]
    assert [node["name"] for node in main_payload["nodes"]] == [
        technical_name for technical_name, _label in n8n_page._MAIN_WORKFLOW_STEPS
    ]
    assert len(main_payload["nodes"]) == 10
    assert len(selected_payload["nodes"]) == 4
    assert any("Trigger declarado: a cada 24 horas" in text for text in fake_st.infos)
    assert any("Retry: não configurado" in str(value) for value in fake_st.writes)
    assert any("Webhook: não configurado" in str(value) for value in fake_st.writes)

    assert {path: path.read_bytes() for path in protected_paths} == original_bytes


@pytest.mark.parametrize("directory_exists", [False, True])
def test_render_n8n_automation_preserves_missing_and_empty_directory_fallbacks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    directory_exists: bool,
) -> None:
    workflow_dir = tmp_path / "workflows" / "n8n"
    if directory_exists:
        workflow_dir.mkdir(parents=True)
    fake_st = _FakeStreamlit()
    file_warning_calls: list[tuple[Path, str]] = []
    diagnostics_calls: list[bool] = []
    monkeypatch.setattr(n8n_page, "st", fake_st)
    monkeypatch.setattr(n8n_page, "WORKFLOWS_DIR", workflow_dir)
    monkeypatch.setattr(
        n8n_page,
        "render_file_warning",
        lambda path, guidance: file_warning_calls.append((path, guidance)),
    )
    monkeypatch.setattr(
        n8n_page,
        "render_artifact_diagnostics",
        lambda: diagnostics_calls.append(True),
    )

    n8n_page.render_n8n_automation()

    assert fake_st.metrics[0] == ("Templates encontrados", 0)
    assert fake_st.metrics[1] == ("Nodes declarados", 0)
    assert fake_st.selectbox_calls == []
    assert diagnostics_calls == [True]
    if directory_exists:
        assert file_warning_calls == []
        assert any("Nenhum arquivo JSON" in text for text in fake_st.warnings)
    else:
        assert len(file_warning_calls) == 1
        assert file_warning_calls[0][0] == workflow_dir
        assert any("não estão disponíveis" in text for text in fake_st.warnings)


def test_render_n8n_automation_preserves_invalid_json_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow_dir = tmp_path / "workflows" / "n8n"
    workflow_dir.mkdir(parents=True)
    invalid_path = workflow_dir / "invalid.json"
    invalid_path.write_text("{invalid", encoding="utf-8")
    original_bytes = invalid_path.read_bytes()
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(n8n_page, "st", fake_st)
    monkeypatch.setattr(n8n_page, "WORKFLOWS_DIR", workflow_dir)
    monkeypatch.setattr(n8n_page, "read_json_safe", lambda _path: {})
    monkeypatch.setattr(n8n_page, "relative_path", lambda path: path.as_posix())
    monkeypatch.setattr(n8n_page, "render_artifact_diagnostics", lambda: None)

    n8n_page.render_n8n_automation()

    technical_workflows, _kwargs = _find_list_table(
        fake_st,
        {"workflow_file", "workflow_name", "status", "node_count"},
    )
    assert technical_workflows[0]["status"] == "read error"
    assert technical_workflows[0]["node_count"] == 0
    workflow_presentation, _kwargs = _find_list_table(
        fake_st,
        {"Arquivo", "Workflow", "Estado do arquivo", "Nodes declarados"},
    )
    assert workflow_presentation[0]["Estado do arquivo"] == "Erro de leitura"
    assert any("não pôde ser lido como JSON" in text for text in fake_st.warnings)
    assert fake_st.json_payloads == []
    assert invalid_path.read_bytes() == original_bytes


def test_page_source_has_no_operational_execution_or_writes() -> None:
    source_path = Path(inspect.getfile(n8n_page))
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    forbidden_writes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"write_text", "write_bytes", "to_csv", "to_json"}
    }

    assert imported_roots.isdisjoint(
        {"subprocess", "requests", "httpx", "urllib", "socket"}
    )
    assert forbidden_writes == set()
    assert "st.button(" not in source
    assert "subprocess" not in source
    assert "requests." not in source
