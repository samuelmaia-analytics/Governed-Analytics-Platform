from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import requests

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ROOT_DIR
from src.dadosfera_catalog_sync import (
    DadosferaMaestroClient,
    apply_auth_from_response,
    build_auth_diagnostics,
    build_sign_in_failure,
    build_sign_in_payloads,
    detect_session_auth_mode,
    raise_runtime_for_auth_response,
    safe_json_body,
    try_refresh_access_token,
)
from src.observability import configure_logging
from src.settings import load_app_settings

LOGGER = logging.getLogger(__name__)
DEFAULT_ENV_PATH = ROOT_DIR / ".env"


class DadosferaApiKeyClient:
    def __init__(
        self,
        *,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        totp: str | None = None,
        access_token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username or ""
        self.password = password or ""
        self.totp = totp
        self.session = requests.Session()
        self.auth_diagnostics: dict[str, Any] = {
            "mode": "none",
            "endpoint": None,
            "body_keys": [],
            "header_keys": [],
            "has_cookies": False,
        }
        self.session.headers.update({"Content-Type": "application/json"})
        if access_token:
            self.session.headers.update(
                {
                    "Authorization": access_token,
                }
            )
            self.auth_diagnostics = {
                "mode": "token_env",
                "endpoint": "env",
                "body_keys": [],
                "header_keys": ["authorization"],
                "has_cookies": False,
            }

    def sign_in(self) -> None:
        if self.session.headers.get("Authorization"):
            return
        last_body: dict[str, Any] = {}
        last_headers: Any | None = None
        last_sign_in_error: RuntimeError | None = None

        for payload in build_sign_in_payloads(username=self.username, password=self.password, totp=self.totp):
            for endpoint in ("/auth/sign-in", "/auth/signin"):
                response = self.session.post(f"{self.base_url}{endpoint}", json=payload, timeout=60)
                if response.status_code >= 500:
                    last_headers = response.headers
                    continue

                try:
                    response.raise_for_status()
                except requests.HTTPError as exc:
                    body = safe_json_body(response)
                    status_code = getattr(response, "status_code", None)
                    if status_code == 404:
                        if not last_body:
                            last_body = body
                            last_headers = response.headers
                        continue
                    sign_in_error = build_sign_in_failure(
                        exc,
                        endpoint=endpoint,
                        response_body=body,
                        response_headers=response.headers,
                    )
                    last_sign_in_error = sign_in_error
                    if status_code in {401, 403}:
                        continue
                    raise sign_in_error

                body = response.json()
                last_body = body
                last_headers = response.headers

                if apply_auth_from_response(self.session, body, response.headers):
                    self.auth_diagnostics = build_auth_diagnostics(
                        session=self.session,
                        endpoint=endpoint,
                        response_body=body,
                        response_headers=response.headers,
                    )
                    return

                if try_refresh_access_token(self.session, self.base_url):
                    self.auth_diagnostics = {
                        "mode": detect_session_auth_mode(self.session),
                        "endpoint": "/auth/refresh-access-token",
                        "body_keys": [],
                        "header_keys": [],
                        "has_cookies": bool(self.session.cookies),
                    }
                    return

        if last_sign_in_error is not None:
            raise last_sign_in_error
        raise_runtime_for_auth_response(last_body, last_headers)

    def list_api_keys(self) -> list[dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/api-key", timeout=60)
        response.raise_for_status()
        return extract_api_key_items(response.json())

    def create_api_key(self, permissions: list[int]) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api-key",
            json={"permissions": permissions},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()


def extract_api_key_items(response_body: Any) -> list[dict[str, Any]]:
    if isinstance(response_body, list):
        return [item for item in response_body if isinstance(item, dict)]
    if not isinstance(response_body, dict):
        return []
    for key in ("items", "data", "results", "api_keys"):
        candidate = response_body.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    if isinstance(response_body.get("result"), list):
        return [item for item in response_body["result"] if isinstance(item, dict)]
    return [response_body]


def extract_api_key_secret(response_body: dict[str, Any]) -> str | None:
    candidates = [response_body]
    for key in ("data", "result", "api_key", "token"):
        nested = response_body.get(key)
        if isinstance(nested, dict):
            candidates.append(nested)

    for candidate in candidates:
        for key in ("api_key", "key", "token", "value", "secret"):
            value = candidate.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def parse_permissions(raw_permissions: str) -> list[int]:
    values = [chunk.strip() for chunk in raw_permissions.split(",")]
    permissions = [int(value) for value in values if value]
    if not permissions:
        raise ValueError("Informe pelo menos uma permissao numerica.")
    return permissions


def upsert_env_var(env_path: Path, key: str, value: str) -> None:
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        lines = content.splitlines()
    else:
        content = ""
        lines = []

    updated = False
    new_lines: list[str] = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if content and not content.endswith(("\n", "\r")):
            new_lines.append("")
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cria uma API key da Dadosfera e opcionalmente salva no .env.")
    parser.add_argument("--permissions", default="1,2,5", help="Lista de IDs de permissao separada por virgula.")
    parser.add_argument("--env-path", type=Path, default=DEFAULT_ENV_PATH, help="Arquivo .env de destino.")
    parser.add_argument("--env-var", default="DADOSFERA_API_TOKEN", help="Nome da variavel a persistir no .env.")
    parser.add_argument("--save-env", action="store_true", help="Salva a nova API key no arquivo .env.")
    parser.add_argument("--list-only", action="store_true", help="Nao cria chave; apenas lista as chaves existentes.")
    parser.add_argument("--json", action="store_true", help="Emite saida em JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging()
    settings = load_app_settings()
    settings.dadosfera.validate_credentials(operation="dadosfera_api_key")

    client = DadosferaApiKeyClient(
        base_url=settings.dadosfera.base_url,
        username=settings.dadosfera.username,
        password=settings.dadosfera.password,
        totp=settings.dadosfera.totp,
        access_token=settings.dadosfera.effective_access_token,
    )
    client.sign_in()

    output: dict[str, Any] = {"api_keys": client.list_api_keys()}

    if not args.list_only:
        permissions = parse_permissions(args.permissions)
        created = client.create_api_key(permissions)
        created_key = extract_api_key_secret(created)
        output["created"] = created
        output["created_secret"] = created_key
        if args.save_env:
            if not created_key:
                raise RuntimeError("A API respondeu sem retornar o valor secreto da nova chave.")
            upsert_env_var(args.env_path, args.env_var, created_key)
            output["saved_env_path"] = str(args.env_path)
            output["saved_env_var"] = args.env_var

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"API keys listadas: {len(output['api_keys'])}")
        if "created" in output:
            print("Nova API key criada com sucesso.")
            if output.get("created_secret"):
                print(f"Valor secreto retornado: {output['created_secret']}")
            else:
                print("A resposta de criacao nao expôs o valor secreto da chave.")
        if output.get("saved_env_path"):
            print(f"Chave salva em {output['saved_env_path']} na variavel {output['saved_env_var']}.")

    LOGGER.info(
        "Fluxo de API key finalizado.",
        extra={
            "operation": "dadosfera_api_key",
            "created": "created" in output,
            "listed_count": len(output["api_keys"]),
            "saved_env": bool(output.get("saved_env_path")),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
