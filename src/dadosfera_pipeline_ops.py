from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from src.dadosfera_catalog_sync import (
    DEFAULT_MAESTRO_BASE_URL,
    apply_auth_from_response,
    build_sign_in_payloads,
    raise_runtime_for_auth_response,
    try_refresh_access_token,
)

DEFAULT_LIST_ENDPOINT = "/platform/pipeline"
DEFAULT_CREATE_ENDPOINT = "/platform/pipeline"
DEFAULT_GET_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}"
DEFAULT_RUN_ENDPOINT = "/platform/pipeline/execute"
DEFAULT_RUNS_ENDPOINT_TEMPLATE = "/platform/pipeline/{pipeline_id}/pipeline_run"


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
        username: str,
        password: str,
        totp: str | None = None,
        config: PipelineApiConfig | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.totp = totp
        self.config = config or PipelineApiConfig()
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def sign_in(self) -> None:
        last_body: dict[str, Any] = {}
        last_headers: Any | None = None

        for payload in build_sign_in_payloads(username=self.username, password=self.password, totp=self.totp):
            for endpoint in ("/auth/sign-in", "/auth/signin"):
                response = self.session.post(f"{self.base_url}{endpoint}", json=payload, timeout=60)
                if response.status_code >= 500:
                    last_headers = response.headers
                    continue

                response.raise_for_status()
                body = response.json()
                last_body = body
                last_headers = response.headers

                if apply_auth_from_response(self.session, body, response.headers):
                    return

                if try_refresh_access_token(self.session, self.base_url):
                    return

        raise_runtime_for_auth_response(last_body, last_headers)

    def list_pipelines(self) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}{normalize_endpoint_path(self.config.list_endpoint)}", timeout=60)
        response.raise_for_status()
        return response.json()

    def create_pipeline(self, definition: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}{normalize_endpoint_path(self.config.create_endpoint)}",
            json=definition,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.get_endpoint_template.format(pipeline_id=pipeline_id))
        response = self.session.get(f"{self.base_url}{endpoint}", timeout=60)
        response.raise_for_status()
        return response.json()

    def run_pipeline(self, pipeline_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.run_endpoint)
        body = {"pipeline_id": pipeline_id}
        if payload:
            body.update(payload)
        response = self.session.post(f"{self.base_url}{endpoint}", json=body, timeout=60)
        response.raise_for_status()
        return response.json()

    def list_pipeline_runs(self, pipeline_id: str) -> dict[str, Any]:
        endpoint = normalize_endpoint_path(self.config.runs_endpoint_template.format(pipeline_id=pipeline_id))
        response = self.session.get(f"{self.base_url}{endpoint}", timeout=60)
        response.raise_for_status()
        return response.json()


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Opera pipelines nativos da Dadosfera via API usando a mesma autenticacao do sync de catalogo."
    )
    parser.add_argument("--base-url", default=os.getenv("DADOSFERA_MAESTRO_BASE_URL", DEFAULT_MAESTRO_BASE_URL))
    parser.add_argument("--list-endpoint", default=os.getenv("DADOSFERA_PIPELINE_LIST_ENDPOINT", DEFAULT_LIST_ENDPOINT))
    parser.add_argument("--create-endpoint", default=os.getenv("DADOSFERA_PIPELINE_CREATE_ENDPOINT", DEFAULT_CREATE_ENDPOINT))
    parser.add_argument(
        "--get-endpoint-template",
        default=os.getenv("DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE", DEFAULT_GET_ENDPOINT_TEMPLATE),
    )
    parser.add_argument(
        "--run-endpoint",
        default=os.getenv("DADOSFERA_PIPELINE_RUN_ENDPOINT", DEFAULT_RUN_ENDPOINT),
    )
    parser.add_argument(
        "--runs-endpoint-template",
        default=os.getenv("DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE", DEFAULT_RUNS_ENDPOINT_TEMPLATE),
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

    return parser.parse_args()


def build_client_from_args(args: argparse.Namespace) -> DadosferaPipelineClient:
    username = os.getenv("DADOSFERA_USERNAME")
    password = os.getenv("DADOSFERA_PASSWORD")
    totp = os.getenv("DADOSFERA_TOTP")
    if not username or not password:
        raise RuntimeError("Defina DADOSFERA_USERNAME e DADOSFERA_PASSWORD para operar pipelines da Dadosfera.")

    config = PipelineApiConfig(
        list_endpoint=args.list_endpoint,
        create_endpoint=args.create_endpoint,
        get_endpoint_template=args.get_endpoint_template,
        run_endpoint=args.run_endpoint,
        runs_endpoint_template=args.runs_endpoint_template,
    )
    return DadosferaPipelineClient(
        base_url=args.base_url,
        username=username,
        password=password,
        totp=totp,
        config=config,
    )


def main() -> None:
    load_dotenv()
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
            pipeline_id = str(response.get("id") or response.get("pipeline_id") or response.get("uuid") or "")
            if not pipeline_id:
                raise RuntimeError("Pipeline criada, mas a resposta nao trouxe identificador para execucao automatica.")
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

    raise RuntimeError(f"Comando nao suportado: {args.command}")


if __name__ == "__main__":
    main()
