from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.dadosfera_pipeline_ops import (
    DadosferaPipelineClient,
    PipelineApiConfig,
    extract_pipeline_items,
    find_pipeline_by_name,
    load_json_file,
    normalize_endpoint_path,
    resolve_pipeline_id,
)
from src.resilient_http import RetryPolicy


def test_normalize_endpoint_path_adds_leading_slash() -> None:
    assert normalize_endpoint_path("process/pipelines") == "/process/pipelines"


def test_normalize_endpoint_path_rejects_empty_value() -> None:
    try:
        normalize_endpoint_path("   ")
    except ValueError as exc:
        assert "nao pode ser vazio" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty endpoint path")


def test_load_json_file_reads_definition(tmp_path: Path) -> None:
    path = tmp_path / "pipeline.json"
    path.write_text(json.dumps({"name": "olist-pipeline"}), encoding="utf-8")

    assert load_json_file(path) == {"name": "olist-pipeline"}


def test_pipeline_client_uses_configured_endpoints() -> None:
    class DummyResponse:
        headers: dict[str, str] = {}

        def __init__(self, body: dict[str, object]) -> None:
            self._body = body

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return self._body

    class DummySession:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/json"}
            self.calls: list[tuple[str, str, dict[str, object] | None]] = []

        def get(self, url: str, timeout: int = 60):  # type: ignore[override]
            self.calls.append(("GET", url, None))
            return DummyResponse({"items": []})

        def post(self, url: str, json: dict[str, object] | None = None, timeout: int = 60):  # type: ignore[override]
            self.calls.append(("POST", url, json))
            return DummyResponse({"id": "pipeline-1"})

    client = DadosferaPipelineClient(
        base_url="https://maestro.dadosfera.ai",
        username="user",
        password="secret",
        config=PipelineApiConfig(
            list_endpoint="/custom/pipelines",
            create_endpoint="/custom/pipelines",
            get_endpoint_template="/custom/pipelines/{pipeline_id}",
            run_endpoint="/custom/pipelines/execute",
            runs_endpoint_template="/custom/pipelines/{pipeline_id}/runs",
        ),
    )
    client.session = DummySession()  # type: ignore[assignment]

    assert client.list_pipelines() == {"items": []}
    assert client.create_pipeline({"name": "olist"}) == {"id": "pipeline-1"}
    assert client.get_pipeline("123") == {"items": []}
    assert client.run_pipeline("123", {"force": True}) == {"id": "pipeline-1"}
    assert client.list_pipeline_runs("123") == {"items": []}

    assert client.session.calls == [
        ("GET", "https://maestro.dadosfera.ai/custom/pipelines", None),
        ("POST", "https://maestro.dadosfera.ai/custom/pipelines", {"name": "olist"}),
        ("GET", "https://maestro.dadosfera.ai/custom/pipelines/123", None),
        ("POST", "https://maestro.dadosfera.ai/custom/pipelines/execute", {"pipeline_id": "123", "force": True}),
        ("GET", "https://maestro.dadosfera.ai/custom/pipelines/123/runs", None),
    ]


def test_extract_pipeline_items_and_find_pipeline_by_name_support_generic_payloads() -> None:
    response = {"items": [{"id": "1", "name": "pipe-a"}, {"id": "2", "name": "pipe-b"}]}

    assert extract_pipeline_items(response) == response["items"]

    class DummyClient:
        @staticmethod
        def list_pipelines() -> dict[str, object]:
            return response

    matched = find_pipeline_by_name(DummyClient(), "pipe-b")  # type: ignore[arg-type]

    assert matched == {"id": "2", "name": "pipe-b"}


def test_resolve_pipeline_id_supports_common_identifier_keys() -> None:
    assert resolve_pipeline_id({"uuid": "pipe-123"}) == "pipe-123"


def test_pipeline_client_retries_create_request_on_retryable_status(monkeypatch) -> None:
    class DummyResponse:
        headers: dict[str, str] = {}

        def __init__(self, status_code: int, body: dict[str, object]) -> None:
            self.status_code = status_code
            self._body = body

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise RuntimeError(f"http {self.status_code}")

        def json(self) -> dict[str, object]:
            return self._body

    class DummySession:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/json"}
            self.calls = 0

        def post(self, url: str, json: dict[str, object] | None = None, timeout: int = 60):  # type: ignore[override]
            self.calls += 1
            if self.calls == 1:
                return DummyResponse(503, {"message": "retry"})
            return DummyResponse(200, {"id": "pipeline-1"})

    monkeypatch.setattr("src.resilient_http.sleep", lambda seconds: None)
    client = DadosferaPipelineClient(
        base_url="https://maestro.dadosfera.ai",
        access_token="token",
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=0),
    )
    client.session = DummySession()  # type: ignore[assignment]

    response = client.create_pipeline({"name": "olist"})

    assert response == {"id": "pipeline-1"}
    assert client.session.calls == 2


def test_pipeline_client_raises_actionable_message_on_missing_endpoint() -> None:
    class DummyResponse:
        headers: dict[str, str] = {}

        def __init__(self, status_code: int) -> None:
            self.status_code = status_code

        def raise_for_status(self) -> None:
            raise requests.HTTPError("404 not found", response=self)

        @staticmethod
        def json() -> dict[str, object]:
            return {"message": "not found"}

    class DummySession:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/json", "Authorization": "token"}

        def get(self, url: str, timeout: int = 60):  # type: ignore[override]
            return DummyResponse(404)

    import requests

    client = DadosferaPipelineClient(base_url="https://maestro.dadosfera.ai", access_token="token")
    client.session = DummySession()  # type: ignore[assignment]

    try:
        client.list_pipelines()
    except RuntimeError as exc:
        assert "Endpoint de pipeline nao encontrado" in str(exc)
        assert "DADOSFERA_PIPELINE_LIST_ENDPOINT" in str(exc)
    else:
        raise AssertionError("Expected actionable RuntimeError for missing pipeline endpoint")


def test_extract_pipeline_items_supports_single_pipeline_payload() -> None:
    payload = {"pipeline": {"id": "pipe-123", "name": "olist"}}

    assert extract_pipeline_items(payload) == [{"id": "pipe-123", "name": "olist"}]


def test_resolve_pipeline_id_raises_when_identifier_is_missing() -> None:
    with pytest.raises(RuntimeError, match="sem identificador utilizavel"):
        resolve_pipeline_id({"name": "olist"})


def test_find_pipeline_by_name_matches_display_name() -> None:
    class DummyClient:
        @staticmethod
        def list_pipelines() -> dict[str, object]:
            return {"items": [{"id": "2", "display_name": "pipe-b"}]}

    matched = find_pipeline_by_name(DummyClient(), "pipe-b")  # type: ignore[arg-type]

    assert matched == {"id": "2", "display_name": "pipe-b"}
