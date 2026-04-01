from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_DADOSFERA_BASE_URL = "https://maestro.dadosfera.ai"
DEFAULT_DADOSFERA_PIPELINE_LIST_ENDPOINT = "/platform/pipelines"
DEFAULT_DADOSFERA_PIPELINE_CREATE_ENDPOINT = "/platform/pipeline"
DEFAULT_DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}"
DEFAULT_DADOSFERA_PIPELINE_RUN_ENDPOINT = "/platform/pipeline/execute"
DEFAULT_DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}/pipeline_run"


def env_flag(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class LoggingSettings:
    format: str = "text"


@dataclass(frozen=True)
class DadosferaSettings:
    enabled: bool
    base_url: str
    access_token: str | None
    api_token: str | None
    username: str | None
    password: str | None
    totp: str | None
    list_endpoint: str
    create_endpoint: str
    get_endpoint_template: str
    run_endpoint: str
    runs_endpoint_template: str

    @property
    def effective_access_token(self) -> str | None:
        return self.access_token or self.api_token

    def validate_credentials(self, *, operation: str) -> None:
        if not self.enabled:
            raise RuntimeError(
                f"Integrações da Dadosfera estão desabilitadas para `{operation}`. Defina DADOSFERA_ENABLED=true para habilitar."
            )
        if self.effective_access_token:
            return
        if self.username and self.password:
            return
        raise RuntimeError(
            f"Credenciais insuficientes para `{operation}`. "
            "Defina DADOSFERA_ACCESS_TOKEN/DADOSFERA_API_TOKEN ou DADOSFERA_USERNAME e DADOSFERA_PASSWORD."
        )


@dataclass(frozen=True)
class OpenAISettings:
    enabled: bool
    api_key: str | None

    def validate_credentials(self) -> None:
        if not self.enabled:
            raise RuntimeError("Integrações OpenAI estão desabilitadas. Defina OPENAI_ENABLED=true para habilitar.")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada.")


@dataclass(frozen=True)
class AppSettings:
    logging: LoggingSettings
    dadosfera: DadosferaSettings
    openai: OpenAISettings


def load_app_settings() -> AppSettings:
    load_dotenv()
    return AppSettings(
        logging=LoggingSettings(format=os.getenv("LOG_FORMAT", "text").strip().lower()),
        dadosfera=DadosferaSettings(
            enabled=env_flag("DADOSFERA_ENABLED", default=False),
            base_url=os.getenv("DADOSFERA_MAESTRO_BASE_URL", DEFAULT_DADOSFERA_BASE_URL),
            access_token=os.getenv("DADOSFERA_ACCESS_TOKEN") or None,
            api_token=os.getenv("DADOSFERA_API_TOKEN") or None,
            username=os.getenv("DADOSFERA_USERNAME") or None,
            password=os.getenv("DADOSFERA_PASSWORD") or None,
            totp=os.getenv("DADOSFERA_TOTP") or None,
            list_endpoint=os.getenv("DADOSFERA_PIPELINE_LIST_ENDPOINT", DEFAULT_DADOSFERA_PIPELINE_LIST_ENDPOINT),
            create_endpoint=os.getenv("DADOSFERA_PIPELINE_CREATE_ENDPOINT", DEFAULT_DADOSFERA_PIPELINE_CREATE_ENDPOINT),
            get_endpoint_template=os.getenv(
                "DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE",
                DEFAULT_DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE,
            ),
            run_endpoint=os.getenv("DADOSFERA_PIPELINE_RUN_ENDPOINT", DEFAULT_DADOSFERA_PIPELINE_RUN_ENDPOINT),
            runs_endpoint_template=os.getenv(
                "DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE",
                DEFAULT_DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE,
            ),
        ),
        openai=OpenAISettings(
            enabled=env_flag("OPENAI_ENABLED", default=False),
            api_key=os.getenv("OPENAI_API_KEY") or None,
        ),
    )


SETTINGS = load_app_settings()
