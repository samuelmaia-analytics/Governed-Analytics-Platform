from __future__ import annotations

import json
from pathlib import Path

import requests

from src.dadosfera_catalog_sync import (
    LOGGER,
    CatalogAssetSpec,
    DadosferaMaestroClient,
    apply_auth_from_response,
    build_create_payload,
    build_sign_in_payloads,
    build_update_payload,
    extract_access_token,
    find_existing_asset,
    load_manifest,
    raise_runtime_for_auth_response,
    raise_runtime_for_sign_in_failure,
    safe_json_body,
    sync_assets,
    try_refresh_access_token,
)
from src.resilient_http import RetryPolicy, request_with_retry


class FakeDadosferaClient:
    def __init__(self, existing_assets: list[dict[str, object]] | None = None) -> None:
        self.assets = list(existing_assets or [])
        self.created_payloads: list[dict[str, object]] = []
        self.updated_payloads: list[tuple[int, dict[str, object]]] = []
        self.next_id = 100

    def list_data_assets(self, *, size: int = 1000) -> list[dict[str, object]]:
        return list(self.assets)

    def create_data_asset(self, payload: dict[str, object]) -> dict[str, object]:
        asset_id = self.next_id
        self.next_id += 1
        self.created_payloads.append(payload)
        self.assets.append(
            {
                "id": asset_id,
                "display_name": payload["display_name"],
                "external_url": payload["external_url"],
            }
        )
        return {"id": asset_id}

    def update_data_asset(
        self, asset_id: int, payload: dict[str, object]
    ) -> dict[str, object]:
        self.updated_payloads.append((asset_id, payload))
        return {"id": asset_id}


def build_asset() -> CatalogAssetSpec:
    return CatalogAssetSpec(
        display_name="App",
        description="Dashboard publicado",
        data_asset_type="dashboard",
        external_url="https://example.com/app",
        location="streamlit_cloud",
        tags=["streamlit", "dashboard"],
        share_type="public",
    )


def test_build_payloads_match_documented_schema() -> None:
    asset = build_asset()

    create_payload = build_create_payload(asset)
    update_payload = build_update_payload(asset)

    assert create_payload == {
        "display_name": "App",
        "description": "Dashboard publicado",
        "data_asset_type": "dashboard",
        "external_url": "https://example.com/app",
        "location": "streamlit_cloud",
    }
    assert update_payload == {
        "name": "App",
        "description": "Dashboard publicado",
        "tags": ["streamlit", "dashboard"],
        "share_type": "public",
    }


def test_load_manifest_reads_asset_specs(tmp_path: Path) -> None:
    manifest_path = tmp_path / "catalog_assets.json"
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "display_name": "Video",
                    "description": "Apresentacao",
                    "data_asset_type": "link",
                    "external_url": "https://example.com/video",
                    "location": "youtube",
                    "tags": ["video"],
                    "share_type": "public",
                }
            ]
        ),
        encoding="utf-8",
    )

    assets = load_manifest(manifest_path)

    assert assets == [
        CatalogAssetSpec(
            display_name="Video",
            description="Apresentacao",
            data_asset_type="link",
            external_url="https://example.com/video",
            location="youtube",
            tags=["video"],
            share_type="public",
            embed_url=None,
        )
    ]


def test_find_existing_asset_prefers_external_url_match() -> None:
    asset = build_asset()
    existing_assets = [
        {"id": 1, "display_name": "Outro", "external_url": "https://example.com/outro"},
        {"id": 2, "display_name": "App", "external_url": "https://example.com/app"},
    ]

    matched = find_existing_asset(existing_assets, asset)

    assert matched == {
        "id": 2,
        "display_name": "App",
        "external_url": "https://example.com/app",
    }


def test_sync_assets_creates_new_asset_and_updates_metadata() -> None:
    asset = build_asset()
    client = FakeDadosferaClient()

    results = sync_assets(client=client, assets=[asset], dry_run=False)

    assert [result.action for result in results] == ["created"]
    assert client.created_payloads == [build_create_payload(asset)]
    assert client.updated_payloads == [(100, build_update_payload(asset))]


def test_sync_assets_updates_existing_asset() -> None:
    asset = build_asset()
    client = FakeDadosferaClient(
        existing_assets=[
            {"id": 7, "display_name": "App", "external_url": "https://example.com/app"}
        ]
    )

    results = sync_assets(client=client, assets=[asset], dry_run=False)

    assert [result.action for result in results] == ["updated"]
    assert client.created_payloads == []
    assert client.updated_payloads == [(7, build_update_payload(asset))]


def test_sync_assets_supports_dry_run() -> None:
    asset = build_asset()
    client = FakeDadosferaClient()

    results = sync_assets(client=client, assets=[asset], dry_run=True)

    assert [result.action for result in results] == ["would_create"]
    assert client.created_payloads == []
    assert client.updated_payloads == []


def test_extract_access_token_supports_nested_tokens_response() -> None:
    assert extract_access_token({"tokens": {"accessToken": "abc123"}}) == "abc123"


def test_extract_access_token_supports_flat_response() -> None:
    assert extract_access_token({"accessToken": "abc123"}) == "abc123"


def test_extract_access_token_supports_authorization_header() -> None:
    assert extract_access_token({}, {"Authorization": "Bearer abc123"}) == "abc123"


def test_extract_access_token_supports_raw_authorization_header() -> None:
    assert extract_access_token({}, {"Authorization": "abc123"}) == "abc123"


def test_extract_access_token_supports_access_token_header() -> None:
    assert extract_access_token({}, {"access-token": "abc123"}) == "abc123"


def test_extract_access_token_returns_none_when_missing() -> None:
    assert extract_access_token({"message": "unauthorized"}) is None


def test_build_sign_in_payloads_supports_username_email_and_mfa_variants() -> None:
    payloads = build_sign_in_payloads(
        username="[email protected]", password="secret", totp="123456"
    )

    assert {
        "username": "[email protected]",
        "password": "secret",
        "totp": "123456",
    } in payloads
    assert {
        "email": "[email protected]",
        "password": "secret",
        "mfaCode": "123456",
    } in payloads


def test_apply_auth_from_response_sets_bearer_headers() -> None:
    import requests

    session = requests.Session()

    authenticated = apply_auth_from_response(session, {"accessToken": "abc123"}, {})

    assert authenticated is True
    assert session.headers["Authorization"] == "abc123"


def test_try_refresh_access_token_uses_refresh_endpoint() -> None:
    import requests

    class DummyResponse:
        status_code = 200
        headers = {}

        @staticmethod
        def json() -> dict[str, str]:
            return {"accessToken": "abc123"}

    class DummySession(requests.Session):
        def post(self, url: str, timeout: int = 60):  # type: ignore[override]
            assert url == "https://maestro.dadosfera.ai/auth/refresh-access-token"
            assert timeout == 60
            return DummyResponse()

    session = DummySession()

    refreshed = try_refresh_access_token(session, "https://maestro.dadosfera.ai")

    assert refreshed is True
    assert session.headers["Authorization"] == "abc123"


def test_sign_in_falls_back_to_legacy_signin_endpoint() -> None:
    class DummyResponse:
        def __init__(
            self, status_code: int, body: dict[str, str] | None = None
        ) -> None:
            self.status_code = status_code
            self._body = body or {}
            self.headers: dict[str, str] = {}

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise RuntimeError(f"http {self.status_code}")

        def json(self) -> dict[str, str]:
            return self._body

    class DummySession:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {"Content-Type": "application/json"}
            self.cookies: dict[str, str] = {}
            self.calls: list[str] = []

        def post(self, url: str, json: dict[str, str] | None = None, timeout: int = 60):  # type: ignore[override]
            self.calls.append(url)
            if url.endswith("/auth/sign-in"):
                return DummyResponse(500)
            if url.endswith("/auth/signin"):
                return DummyResponse(200, {"accessToken": "abc123"})
            if url.endswith("/auth/refresh-access-token"):
                return DummyResponse(401)
            raise AssertionError(f"Unexpected URL: {url}")

    client = DadosferaMaestroClient(
        base_url="https://maestro.dadosfera.ai",
        username="user",
        password="secret",
        retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
    )
    client.session = DummySession()  # type: ignore[assignment]

    client.sign_in()

    assert client.session.headers["Authorization"] == "abc123"
    assert client.session.calls[:2] == [
        "https://maestro.dadosfera.ai/auth/sign-in",
        "https://maestro.dadosfera.ai/auth/signin",
    ]


def test_raise_runtime_for_auth_response_includes_diagnostic_keys() -> None:
    try:
        raise_runtime_for_auth_response(
            {"message": "unauthorized", "error": "AUTH.UNAUTHORIZED"},
            {"Content-Type": "application/json"},
        )
    except RuntimeError as exc:
        assert "Chaves recebidas: error, message" in str(exc)
        assert "Headers recebidos: content-type" in str(exc)
        assert "message='unauthorized'" in str(exc)
        assert "error='AUTH.UNAUTHORIZED'" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when access token is missing")


def test_client_with_access_token_skips_interactive_sign_in() -> None:
    client = DadosferaMaestroClient(
        base_url="https://maestro.dadosfera.ai",
        access_token="abc123",
    )

    client.sign_in()

    assert client.session.headers["Authorization"] == "abc123"


def test_request_with_retry_retries_retryable_status(monkeypatch) -> None:
    class DummyResponse:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code
            self.headers: dict[str, str] = {}

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError(f"http {self.status_code}")

    class DummySession:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, url: str, timeout: int = 60):  # type: ignore[override]
            self.calls += 1
            return DummyResponse(503 if self.calls == 1 else 200)

    monkeypatch.setattr("src.resilient_http.sleep", lambda seconds: None)
    session = DummySession()

    response = request_with_retry(
        session,  # type: ignore[arg-type]
        "GET",
        "https://example.com/catalog",
        logger=LOGGER,
        operation="catalog_test",
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=0),
        timeout=60,
    )

    assert response.status_code == 200
    assert session.calls == 2


def test_catalog_client_raises_actionable_message_on_unauthorized() -> None:
    class DummyResponse:
        status_code = 401
        headers: dict[str, str] = {}

        def raise_for_status(self) -> None:
            raise requests.HTTPError("401 unauthorized", response=self)

        @staticmethod
        def json() -> dict[str, object]:
            return {"message": "unauthorized"}

    class DummySession:
        def __init__(self) -> None:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": "token",
            }

        def get(
            self, url: str, params: dict[str, object] | None = None, timeout: int = 60
        ):  # type: ignore[override]
            return DummyResponse()

    client = DadosferaMaestroClient(
        base_url="https://maestro.dadosfera.ai", access_token="token"
    )
    client.session = DummySession()  # type: ignore[assignment]

    try:
        client.list_data_assets()
    except RuntimeError as exc:
        assert "Falha de autenticacao/autorizacao" in str(exc)
        assert "Valide escopo, expiracao e tenant do token" in str(exc)
    else:
        raise AssertionError(
            "Expected actionable RuntimeError for unauthorized catalog request"
        )


def test_raise_runtime_for_sign_in_failure_includes_body_and_header_keys() -> None:
    response = requests.Response()
    response.status_code = 401
    response._content = b'{"message":"unauthorized","code":"AUTH.UNAUTHORIZED"}'
    response.headers["Content-Type"] = "application/json"
    error = requests.HTTPError("401 unauthorized", response=response)

    try:
        raise_runtime_for_sign_in_failure(
            error,
            endpoint="/auth/sign-in",
            response_body=safe_json_body(response),
            response_headers=response.headers,
        )
    except RuntimeError as exc:
        assert (
            "Autenticacao da Dadosfera falhou em `/auth/sign-in` com HTTP 401"
            in str(exc)
        )
        assert "message" in str(exc)
        assert "code" in str(exc)
        assert "content-type" in str(exc)
        assert "message='unauthorized'" in str(exc)
        assert "error='AUTH.UNAUTHORIZED'" in str(exc)
    else:
        raise AssertionError("Expected actionable RuntimeError for sign-in failure")
