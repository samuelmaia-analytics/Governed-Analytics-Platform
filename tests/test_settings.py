from __future__ import annotations

from src.settings import env_flag, load_app_settings


def test_env_flag_interprets_common_truthy_values(monkeypatch) -> None:
    monkeypatch.setenv("FEATURE_X", "true")

    assert env_flag("FEATURE_X") is True


def test_load_app_settings_reads_feature_flags_and_tokens(monkeypatch) -> None:
    monkeypatch.setenv("DADOSFERA_ENABLED", "true")
    monkeypatch.setenv("DADOSFERA_ACCESS_TOKEN", "secret-token")
    monkeypatch.setenv("OPENAI_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("LOG_FORMAT", "json")

    settings = load_app_settings()

    assert settings.logging.format == "json"
    assert settings.dadosfera.enabled is True
    assert settings.dadosfera.effective_access_token == "secret-token"
    assert settings.openai.enabled is True
    assert settings.openai.api_key == "openai-secret"


def test_dadosfera_settings_require_enablement_and_credentials(monkeypatch) -> None:
    monkeypatch.delenv("DADOSFERA_ENABLED", raising=False)
    monkeypatch.delenv("DADOSFERA_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("DADOSFERA_API_TOKEN", raising=False)
    monkeypatch.delenv("DADOSFERA_USERNAME", raising=False)
    monkeypatch.delenv("DADOSFERA_PASSWORD", raising=False)

    settings = load_app_settings()

    try:
        settings.dadosfera.validate_credentials(operation="catalog_sync")
    except RuntimeError as exc:
        assert "desabilitadas" in str(exc)
    else:
        raise AssertionError("Era esperado erro ao usar integração desabilitada.")


def test_openai_settings_require_api_key_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_ENABLED", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_app_settings()

    try:
        settings.openai.validate_credentials()
    except RuntimeError as exc:
        assert "OPENAI_API_KEY" in str(exc)
    else:
        raise AssertionError("Era esperado erro quando OpenAI está habilitado sem chave.")
