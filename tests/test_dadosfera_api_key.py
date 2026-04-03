from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.dadosfera_api_key as dadosfera_api_key
from src.dadosfera_api_key import (
    DadosferaApiKeyClient,
    extract_api_key_items,
    extract_api_key_secret,
    parse_permissions,
    upsert_env_var,
)


def test_parse_permissions_supports_comma_separated_values() -> None:
    assert parse_permissions("1, 2,5") == [1, 2, 5]


def test_extract_api_key_items_supports_list_and_wrapped_payloads() -> None:
    assert extract_api_key_items([{"id": 1}]) == [{"id": 1}]
    assert extract_api_key_items({"data": [{"id": 2}]}) == [{"id": 2}]


def test_extract_api_key_secret_supports_multiple_common_keys() -> None:
    assert extract_api_key_secret({"api_key": "secret-1"}) == "secret-1"
    assert extract_api_key_secret({"result": {"token": "secret-2"}}) == "secret-2"


def test_upsert_env_var_replaces_existing_value(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("DADOSFERA_API_TOKEN=old\nLOG_FORMAT=text\n", encoding="utf-8")

    upsert_env_var(env_path, "DADOSFERA_API_TOKEN", "new-secret")

    assert env_path.read_text(encoding="utf-8") == "DADOSFERA_API_TOKEN=new-secret\nLOG_FORMAT=text\n"


def test_upsert_env_var_appends_new_value(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("LOG_FORMAT=text\n", encoding="utf-8")

    upsert_env_var(env_path, "DADOSFERA_API_TOKEN", "new-secret")

    assert env_path.read_text(encoding="utf-8") == "LOG_FORMAT=text\nDADOSFERA_API_TOKEN=new-secret\n"


def test_parse_permissions_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="pelo menos uma permissao"):
        parse_permissions(" , ")


def test_extract_api_key_items_supports_result_list() -> None:
    assert extract_api_key_items({"result": [{"id": 3}]}) == [{"id": 3}]


def test_main_list_only_json_output(monkeypatch, capsys) -> None:
    class DummySettings:
        class DadosferaSettings:
            base_url = "https://maestro.example.com"
            username = "user"
            password = "secret"
            totp = None
            effective_access_token = "token"

            @staticmethod
            def validate_credentials(*, operation: str) -> None:
                assert operation == "dadosfera_api_key"

        dadosfera = DadosferaSettings()

    class DummyClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

        @staticmethod
        def sign_in() -> None:
            return None

        @staticmethod
        def list_api_keys() -> list[dict[str, object]]:
            return [{"id": 1, "name": "default"}]

    monkeypatch.setattr(dadosfera_api_key, "load_app_settings", lambda: DummySettings())
    monkeypatch.setattr(dadosfera_api_key, "DadosferaApiKeyClient", DummyClient)
    monkeypatch.setattr(dadosfera_api_key, "configure_logging", lambda: None)

    exit_code = dadosfera_api_key.main(["--list-only", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["api_keys"] == [{"id": 1, "name": "default"}]


def test_main_raises_when_save_env_requested_without_secret(monkeypatch, tmp_path: Path) -> None:
    class DummySettings:
        class DadosferaSettings:
            base_url = "https://maestro.example.com"
            username = "user"
            password = "secret"
            totp = None
            effective_access_token = "token"

            @staticmethod
            def validate_credentials(*, operation: str) -> None:
                assert operation == "dadosfera_api_key"

        dadosfera = DadosferaSettings()

    class DummyClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

        @staticmethod
        def sign_in() -> None:
            return None

        @staticmethod
        def list_api_keys() -> list[dict[str, object]]:
            return []

        @staticmethod
        def create_api_key(permissions: list[int]) -> dict[str, object]:
            assert permissions == [1, 2, 5]
            return {"id": 123}

    monkeypatch.setattr(dadosfera_api_key, "load_app_settings", lambda: DummySettings())
    monkeypatch.setattr(dadosfera_api_key, "DadosferaApiKeyClient", DummyClient)
    monkeypatch.setattr(dadosfera_api_key, "configure_logging", lambda: None)

    with pytest.raises(RuntimeError, match="sem retornar o valor secreto"):
        dadosfera_api_key.main(["--save-env", "--env-path", str(tmp_path / ".env")])


def test_api_key_client_with_token_skips_sign_in() -> None:
    client = DadosferaApiKeyClient(base_url="https://maestro.example.com", access_token="token")

    client.sign_in()

    assert client.session.headers["Authorization"] == "token"


def test_api_key_client_lists_and_creates_keys() -> None:
    class DummyResponse:
        def __init__(self, payload: object) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> object:
            return self._payload

    class DummySession:
        def __init__(self) -> None:
            self.headers = {"Content-Type": "application/json"}
            self.calls: list[tuple[str, str, object | None]] = []

        def get(self, url: str, timeout: int = 60):  # type: ignore[override]
            self.calls.append(("GET", url, None))
            return DummyResponse({"items": [{"id": 1}]})

        def post(self, url: str, json: object | None = None, timeout: int = 60):  # type: ignore[override]
            self.calls.append(("POST", url, json))
            return DummyResponse({"token": "secret-123"})

    client = DadosferaApiKeyClient(base_url="https://maestro.example.com")
    client.session = DummySession()  # type: ignore[assignment]

    assert client.list_api_keys() == [{"id": 1}]
    assert client.create_api_key([1, 2]) == {"token": "secret-123"}
    assert client.session.calls == [
        ("GET", "https://maestro.example.com/api-key", None),
        ("POST", "https://maestro.example.com/api-key", {"permissions": [1, 2]}),
    ]


def test_main_creates_key_and_saves_env(monkeypatch, tmp_path: Path, capsys) -> None:
    class DummySettings:
        class DadosferaSettings:
            base_url = "https://maestro.example.com"
            username = "user"
            password = "secret"
            totp = None
            effective_access_token = "token"

            @staticmethod
            def validate_credentials(*, operation: str) -> None:
                assert operation == "dadosfera_api_key"

        dadosfera = DadosferaSettings()

    class DummyClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

        @staticmethod
        def sign_in() -> None:
            return None

        @staticmethod
        def list_api_keys() -> list[dict[str, object]]:
            return [{"id": 1}]

        @staticmethod
        def create_api_key(permissions: list[int]) -> dict[str, object]:
            assert permissions == [9]
            return {"api_key": "secret-999"}

    env_path = tmp_path / ".env"
    monkeypatch.setattr(dadosfera_api_key, "load_app_settings", lambda: DummySettings())
    monkeypatch.setattr(dadosfera_api_key, "DadosferaApiKeyClient", DummyClient)
    monkeypatch.setattr(dadosfera_api_key, "configure_logging", lambda: None)

    exit_code = dadosfera_api_key.main(
        ["--permissions", "9", "--save-env", "--env-path", str(env_path), "--env-var", "CUSTOM_TOKEN"]
    )

    assert exit_code == 0
    assert "CUSTOM_TOKEN=secret-999" in env_path.read_text(encoding="utf-8")
    assert "Nova API key criada com sucesso." in capsys.readouterr().out
