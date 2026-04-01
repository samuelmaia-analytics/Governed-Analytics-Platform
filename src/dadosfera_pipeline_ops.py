from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.dadosfera_catalog_sync import (
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
from src.resilient_http import DEFAULT_RETRY_POLICY, RetryPolicy, request_with_retry
from src.settings import load_app_settings

DEFAULT_LIST_ENDPOINT = "/platform/pipelines"
DEFAULT_CREATE_ENDPOINT = "/platform/pipeline"
DEFAULT_GET_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}"
DEFAULT_RUN_ENDPOINT = "/platform/pipeline/execute"
DEFAULT_RUNS_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}/pipeline_run"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineApiConfig:
    list_endpoint: str = DEFAULT_LIST_ENDPOINT
    create_endpoint: str = DEFAULT_CREATE_ENDPOINT
    get_endpoint_template: str = DEFAULT_GET_ENDPOINT_TEMPLATE
    run_endpoint: str = DEFAULT_RUN_ENDPOINT
    runs_endpoint_template: str = DEFAULT_RUNS_ENDPOINT_TEMPLATE


def normalize_endpoint_path(path: str) -> str:
    cleaned = path.strip()
    if not cleaned:
        raise ValueError("Endpoint path nao pode ser vazio.")
    return cleaned if cleaned.startswith("/") else f"/{cleaned}"


class DadosferaPipelineClient:
    def __init__(
        self,
        *,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        totp: str | None = None,
        access_token: str | None = None,
        config: PipelineApiConfig | None = None,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username or ""
        self.password = password or ""
        self.totp = totp
        self.config = config or PipelineApiConfig()
        self.retry_policy = retry_policy
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
                    "access-token": access_token,
                    "Authorization": f"Bearer {access_token}",
                }
            )
            self.auth_diagnostics = {
                "mode": "token_env",
                "endpoint": "env",
                "body_keys": [],
                "header_keys": ["access-token", "authorization"],
                "has_cookies": False,
            }

    def _request(self, method: str, path: str, *, operation: str, **kwargs: Any) -> requests.Response:
        try:
            response = request_with_retry(
                self.session,
                method,
                f"{self.base_url}{path}",
                logger=LOGGER,
                operation=operation,
                retry_policy=self.retry_policy,
                **kwargs,
            )
        except requests.HTTPError as exc:
            raise_runtime_for_pipeline_http_error(
                exc,
                path=path,
                operation=operation,
                has_authorization=bool(self.session.headers.get("Authorization")),
                auth_diagnostics=self.auth_diagnostics,
            )

        LOGGER.info(
            "Chamada à API concluída.",
            extra={
                "operation": operation,
                "http_method": method.upper(),
                "path": path,
                "status_code": getattr(response, "status_code", 200),
            },
        )
        return response

    def sign_in(self) -> None:
        if self.session.headers.get("Authorization"):
            return
        last_body: dict[str, Any] = {}
        last_headers: Any | None = None
        last_sign_in_error: RuntimeError | None = None

        for payload in build_sign_in_payloads(username=self.username, password=self.password, totp=self.totp):
            for endpoint in ("/auth/sign-in", "/auth/signin"):
                response = request_with_retry(
                    self.session,
                    "POST",
                    f"{self.base_url}{endpoint}",
                    logger=LOGGER,
                    operation="dadosfera_pipeline_sign_in",
                    retry_policy=self.retry_policy,
                    json=payload,
                    timeout=60,
                    raise_for_status=False,
                )
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

    def list_pipelines(self) -> dict[str, Any]:
        response = self._request(
            "GET",
            normalize_endpoint_path(self.config.list_endpoint),
            operation="dadosfera_list_pipelines",
            timeout=60,
        )
        return response.json()

    def create_pipeline(self, definition: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            "POST",
            normalize_endpoint_path(self.config.create_endpoint),
            operation="dadosfera_create_pipeline",
            json=definition,
            timeout=60,
        )
        return response.json()

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.get_endpoint_template.format(pipeline_id=pipeline_id))
        response = self._request("GET", endpoint, operation="dadosfera_get_pipeline", timeout=60)
        return response.json()

    def run_pipeline(self, pipeline_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.run_endpoint)
        body = {"pipeline_id": pipeline_id}
        if payload:
            body.update(payload)
        response = self._request("POST", endpoint, operation="dadosfera_run_pipeline", json=body, timeout=60)
        return response.json()

    def list_pipeline_runs(self, pipeline_id: str) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.runs_endpoint_template.format(pipeline_id=pipeline_id))
        response = self._request("GET", endpoint, operation="dadosfera_list_pipeline_runs", timeout=60)
        return response.json()


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_pipeline_items(response_body: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("items", "pipelines", "data_assets", "data"):
        candidate = response_body.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    if isinstance(response_body.get("pipeline"), dict):
        return [response_body["pipeline"]]
    return []


def resolve_pipeline_id(pipeline_body: dict[str, Any]) -> str:
    for key in ("id", "pipeline_id", "uuid"):
        value = pipeline_body.get(key)
        if value:
            return str(value)
    raise RuntimeError("Resposta da pipeline sem identificador utilizavel.")


def find_pipeline_by_name(client: DadosferaPipelineClient, pipeline_name: str) -> dict[str, Any] | None:
    response = client.list_pipelines()
    for pipeline in extract_pipeline_items(response):
        if str(pipeline.get("name") or pipeline.get("display_name") or "") == pipeline_name:
            return pipeline
    return None


def raise_runtime_for_pipeline_http_error(
    error: requests.HTTPError,
    *,
    path: str,
    operation: str,
    has_authorization: bool,
    auth_diagnostics: dict[str, Any] | None = None,
) -> None:
    response = error.response
    status_code = getattr(response, "status_code", None)

    if status_code in {401, 403}:
        auth_summary = ""
        if auth_diagnostics:
            auth_summary = (
                " Diagnostico de auth: "
                f"mode={auth_diagnostics.get('mode')}, "
                f"endpoint={auth_diagnostics.get('endpoint')}, "
                f"has_cookies={auth_diagnostics.get('has_cookies')}, "
                f"body_keys={auth_diagnostics.get('body_keys')}, "
                f"header_keys={auth_diagnostics.get('header_keys')}."
            )
        auth_hint = (
            "A requisicao foi enviada com cabecalho de autorizacao, mas a API rejeitou o acesso. "
            "Valide escopo, expiracao e tenant do token configurado."
            if has_authorization
            else "A autenticacao nao foi aceita. Valide DADOSFERA_ACCESS_TOKEN/DADOSFERA_API_TOKEN ou usuario e senha."
        )
        raise RuntimeError(
            f"Falha de autenticacao/autorizacao na Dadosfera durante `{operation}` em `{path}` (HTTP {status_code}). {auth_hint}{auth_summary}"
        ) from error

    if status_code == 404:
        raise RuntimeError(
            f"Endpoint de pipeline nao encontrado durante `{operation}` em `{path}` (HTTP 404). "
            "Ajuste `DADOSFERA_PIPELINE_LIST_ENDPOINT`, `DADOSFERA_PIPELINE_CREATE_ENDPOINT`, "
            "`DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE`, `DADOSFERA_PIPELINE_RUN_ENDPOINT` "
            "e `DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE` para os caminhos reais do seu tenant."
        ) from error

    raise RuntimeError(
        f"Chamada de pipeline da Dadosfera falhou durante `{operation}` em `{path}` com HTTP {status_code or 'desconhecido'}."
    ) from error


def parse_args() -> argparse.Namespace:
    settings = load_app_settings()
    parser = argparse.ArgumentParser(
        description="Opera pipelines nativos da Dadosfera via API usando a mesma autenticacao do sync de catalogo."
    )
    parser.add_argument("--base-url", default=settings.dadosfera.base_url)
    parser.add_argument("--list-endpoint", default=settings.dadosfera.list_endpoint)
    parser.add_argument("--create-endpoint", default=settings.dadosfera.create_endpoint)
    parser.add_argument(
        "--get-endpoint-template",
        default=settings.dadosfera.get_endpoint_template,
    )
    parser.add_argument(
        "--run-endpoint",
        default=settings.dadosfera.run_endpoint,
    )
    parser.add_argument(
        "--runs-endpoint-template",
        default=settings.dadosfera.runs_endpoint_template,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="Lista pipelines disponiveis no endpoint configurado.")

    create_parser = subparsers.add_parser("create", help="Cria pipeline a partir de definicao JSON.")
    create_parser.add_argument("--definition", type=Path, required=True, help="Arquivo JSON com a definicao do pipeline.")
    create_parser.add_argument("--execute", action="store_true", help="Executa o pipeline logo apos a criacao.")
    create_parser.add_argument(
        "--run-payload",
        type=Path,
        help="Arquivo JSON opcional com payload de execucao usado quando --execute estiver habilitado.",
    )

    get_parser = subparsers.add_parser("get", help="Consulta uma pipeline pelo ID.")
    get_parser.add_argument("--pipeline-id", required=True)

    run_parser = subparsers.add_parser("run", help="Executa uma pipeline existente.")
    run_parser.add_argument("--pipeline-id", required=True)
    run_parser.add_argument("--payload", type=Path, help="Arquivo JSON opcional com payload de execucao.")

    runs_parser = subparsers.add_parser("runs", help="Lista execucoes de uma pipeline.")
    runs_parser.add_argument("--pipeline-id", required=True)

    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Garante a existencia da pipeline pelo nome da definicao e opcionalmente executa logo em seguida.",
    )
    deploy_parser.add_argument("--definition", type=Path, required=True)
    deploy_parser.add_argument("--execute", action="store_true")
    deploy_parser.add_argument("--run-payload", type=Path)

    return parser.parse_args()


def build_client_from_args(args: argparse.Namespace) -> DadosferaPipelineClient:
    dadosfera_settings = load_app_settings().dadosfera
    dadosfera_settings.validate_credentials(operation="pipeline_ops")

    config = PipelineApiConfig(
        list_endpoint=args.list_endpoint,
        create_endpoint=args.create_endpoint,
        get_endpoint_template=args.get_endpoint_template,
        run_endpoint=args.run_endpoint,
        runs_endpoint_template=args.runs_endpoint_template,
    )
    return DadosferaPipelineClient(
        base_url=args.base_url,
        username=dadosfera_settings.username,
        password=dadosfera_settings.password,
        totp=dadosfera_settings.totp,
        access_token=dadosfera_settings.effective_access_token,
        config=config,
    )


def main() -> None:
    configure_logging()
    args = parse_args()
    client = build_client_from_args(args)
    client.sign_in()

    if args.command == "list":
        print(json.dumps(client.list_pipelines(), indent=2, ensure_ascii=False))
        return

    if args.command == "create":
        definition = load_json_file(args.definition.resolve())
        response = client.create_pipeline(definition)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        if args.execute:
            pipeline_id = resolve_pipeline_id(response)
            payload = load_json_file(args.run_payload.resolve()) if args.run_payload else {}
            run_response = client.run_pipeline(pipeline_id, payload)
            print(json.dumps(run_response, indent=2, ensure_ascii=False))
        return

    if args.command == "get":
        print(json.dumps(client.get_pipeline(args.pipeline_id), indent=2, ensure_ascii=False))
        return

    if args.command == "run":
        payload = load_json_file(args.payload.resolve()) if args.payload else {}
        print(json.dumps(client.run_pipeline(args.pipeline_id, payload), indent=2, ensure_ascii=False))
        return

    if args.command == "runs":
        print(json.dumps(client.list_pipeline_runs(args.pipeline_id), indent=2, ensure_ascii=False))
        return

    if args.command == "deploy":
        definition = load_json_file(args.definition.resolve())
        pipeline_name = str(definition.get("name") or "").strip()
        if not pipeline_name:
            raise RuntimeError("A definicao JSON precisa conter o campo `name` para deploy idempotente.")
        existing = find_pipeline_by_name(client, pipeline_name)
        response = existing or client.create_pipeline(definition)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        if args.execute:
            payload = load_json_file(args.run_payload.resolve()) if args.run_payload else {}
            run_response = client.run_pipeline(resolve_pipeline_id(response), payload)
            print(json.dumps(run_response, indent=2, ensure_ascii=False))
        return

    raise RuntimeError(f"Comando nao suportado: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
