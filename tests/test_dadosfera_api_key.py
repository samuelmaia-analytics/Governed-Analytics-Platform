from __future__ import annotations

from pathlib import Path

from src.dadosfera_api_key import (
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
