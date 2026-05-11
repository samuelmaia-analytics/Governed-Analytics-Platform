from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, ROOT_DIR
from src.observability import configure_logging
from src.resilient_http import DEFAULT_RETRY_POLICY, RetryPolicy, request_with_retry
from src.settings import load_app_settings

DEFAULT_MAESTRO_BASE_URL = "https://maestro.dadosfera.ai"
DEFAULT_MANIFEST_PATH = (
    ROOT_DIR / "contracts" / "catalog" / "dadosfera_catalog_assets.json"
)
DEFAULT_REPORT_PATH = DOCS_DIR / "dadosfera_api_sync.md"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CatalogAssetSpec:
    display_name: str
    description: str
    data_asset_type: str
    external_url: str
    location: str
    tags: list[str]
    share_type: str = "public"
    embed_url: str | None = None


@dataclass(frozen=True)
class SyncResult:
    action: str
    asset_name: str
    asset_id: int | None
    external_url: str


class DadosferaMaestroClient:
    def __init__(
        self,
        *,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        totp: str | None = None,
        access_token: str | None = None,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username or ""
        self.password = password or ""
        self.totp = totp
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

    def _request(
        self,
        method: str,
        path: str,
        *,
        operation: str,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        try:
            response = request_with_retry(
                self.session,
                method,
                f"{self.base_url}{path}",
                logger=LOGGER,
                operation=operation,
                retry_policy=self.retry_policy,
                raise_for_status=raise_for_status,
                **kwargs,
            )
        except requests.HTTPError as exc:
            raise_runtime_for_http_error(
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

        for payload in build_sign_in_payloads(
            username=self.username, password=self.password, totp=self.totp
        ):
            for endpoint in ("/auth/sign-in", "/auth/signin"):
                response = self._request(
                    "POST",
                    endpoint,
                    operation="dadosfera_sign_in",
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

    def list_data_assets(self, *, size: int = 1000) -> list[dict[str, Any]]:
        page = 1
        assets: list[dict[str, Any]] = []
        total = None

        while total is None or len(assets) < total:
            response = self._request(
                "GET",
                "/catalog",
                operation="dadosfera_list_catalog_assets",
                params={
                    "size": size,
                    "page": page,
                    "sort_by": "created_at",
                    "order": "desc",
                },
                timeout=60,
            )
            body = response.json()
            assets.extend(body.get("data_assets", []))
            total = int(body.get("total", len(assets)))
            if not body.get("data_assets"):
                break
            page += 1

        return assets

    def create_data_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/catalog",
            operation="dadosfera_create_catalog_asset",
            json=payload,
            timeout=60,
        )
        return response.json()

    def update_data_asset(
        self, asset_id: int, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = self._request(
            "PUT",
            f"/catalog/data-asset/{asset_id}",
            operation="dadosfera_update_catalog_asset",
            json=payload,
            timeout=60,
        )
        return response.json()


def load_manifest(path: Path) -> list[CatalogAssetSpec]:
    raw_assets = json.loads(path.read_text(encoding="utf-8"))
    assets: list[CatalogAssetSpec] = []
    for raw in raw_assets:
        assets.append(
            CatalogAssetSpec(
                display_name=raw["display_name"],
                description=raw["description"],
                data_asset_type=raw["data_asset_type"],
                external_url=raw["external_url"],
                location=raw["location"],
                tags=list(raw.get("tags", [])),
                share_type=raw.get("share_type", "public"),
                embed_url=raw.get("embed_url"),
            )
        )
    return assets


def build_create_payload(asset: CatalogAssetSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "display_name": asset.display_name,
        "description": asset.description,
        "data_asset_type": asset.data_asset_type,
        "external_url": asset.external_url,
        "location": asset.location,
    }
    if asset.embed_url:
        payload["embed"] = {"url": asset.embed_url}
    return payload


def build_update_payload(asset: CatalogAssetSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": asset.display_name,
        "description": asset.description,
        "tags": asset.tags,
        "share_type": asset.share_type,
    }
    if asset.embed_url:
        payload["embed"] = {"url": asset.embed_url}
    return payload


def extract_asset_id(response_body: dict[str, Any]) -> int | None:
    if isinstance(response_body.get("id"), int):
        return response_body["id"]
    for key in ("data_asset", "asset", "result"):
        nested = response_body.get(key)
        if isinstance(nested, dict) and isinstance(nested.get("id"), int):
            return nested["id"]
    return None


def build_sign_in_payloads(
    *, username: str, password: str, totp: str | None
) -> list[dict[str, str]]:
    payloads: list[dict[str, str]] = [
        {"username": username, "password": password},
        {"email": username, "password": password},
    ]

    if not totp:
        return payloads

    enriched_payloads: list[dict[str, str]] = []
    for payload in payloads:
        for field in ("totp", "code", "mfaCode", "mfa_code", "token"):
            candidate = dict(payload)
            candidate[field] = totp
            enriched_payloads.append(candidate)

    return enriched_payloads + payloads


def apply_auth_from_response(
    session: requests.Session,
    response_body: dict[str, Any],
    response_headers: Any | None,
) -> bool:
    access_token = extract_access_token(response_body, response_headers)
    if access_token:
        session.headers.update(
            {
                "Authorization": access_token,
            }
        )
        return True

    return bool(session.cookies)


def detect_session_auth_mode(session: requests.Session) -> str:
    if session.headers.get("Authorization"):
        return "authorization"
    if session.headers.get("access-token"):
        return "access-token"
    if session.cookies:
        return "cookies"
    return "none"


def build_auth_diagnostics(
    *,
    session: requests.Session,
    endpoint: str,
    response_body: dict[str, Any],
    response_headers: Any | None,
) -> dict[str, Any]:
    header_keys: list[str] = []
    if response_headers is not None:
        header_keys = sorted(str(key).lower() for key in response_headers.keys())
    return {
        "mode": detect_session_auth_mode(session),
        "endpoint": endpoint,
        "body_keys": sorted(response_body.keys()),
        "header_keys": header_keys,
        "has_cookies": bool(session.cookies),
    }


def try_refresh_access_token(session: requests.Session, base_url: str) -> bool:
    response = request_with_retry(
        session,
        "POST",
        f"{base_url}/auth/refresh-access-token",
        logger=LOGGER,
        operation="dadosfera_refresh_access_token",
        retry_policy=DEFAULT_RETRY_POLICY,
        timeout=60,
        raise_for_status=False,
    )
    if response.status_code >= 400:
        return False

    body = response.json()
    return apply_auth_from_response(session, body, response.headers)


def extract_access_token(
    response_body: dict[str, Any], response_headers: Any | None = None
) -> str | None:
    token_candidates = [
        response_body.get("accessToken"),
        response_body.get("access_token"),
    ]

    nested_tokens = response_body.get("tokens")
    if isinstance(nested_tokens, dict):
        token_candidates.extend(
            [
                nested_tokens.get("accessToken"),
                nested_tokens.get("access_token"),
                nested_tokens.get("token"),
            ]
        )

    auth_data = response_body.get("data")
    if isinstance(auth_data, dict):
        token_candidates.extend(
            [
                auth_data.get("accessToken"),
                auth_data.get("access_token"),
                auth_data.get("token"),
            ]
        )

    normalized_headers: dict[str, str] = {}
    if response_headers is not None:
        normalized_headers = {
            str(key).lower(): str(value) for key, value in response_headers.items()
        }
        token_candidates.extend(
            [
                normalized_headers.get("access-token"),
                normalized_headers.get("x-access-token"),
            ]
        )

        authorization = normalized_headers.get("authorization")
        if isinstance(authorization, str) and authorization.strip():
            token_candidates.append(
                authorization[7:].strip()
                if authorization.lower().startswith("bearer ")
                else authorization.strip()
            )

        set_cookie = normalized_headers.get("set-cookie")
        if isinstance(set_cookie, str):
            for pattern in (
                r"access[-_]?token=([^;,\s]+)",
                r"token=([^;,\s]+)",
                r"jwt=([^;,\s]+)",
            ):
                match = re.search(pattern, set_cookie, flags=re.IGNORECASE)
                if match:
                    token_candidates.append(match.group(1))

    for token in token_candidates:
        if isinstance(token, str) and token.strip():
            return token

    return None


def raise_runtime_for_auth_response(
    response_body: dict[str, Any], response_headers: Any | None = None
) -> None:
    available_keys = ", ".join(sorted(response_body.keys())) or "<none>"
    header_keys = "<none>"
    if response_headers is not None:
        header_keys = (
            ", ".join(sorted(str(key).lower() for key in response_headers.keys()))
            or "<none>"
        )

    mfa_status = response_body.get("mfaStatus")
    mfa_hint = ""
    if mfa_status not in (None, False, "disabled", "DISABLED"):
        mfa_hint = " A resposta indica MFA ativo; valide DADOSFERA_TOTP e o formato do payload de autenticacao."
    response_message = response_body.get("message")
    response_error = response_body.get("error")
    detail_parts: list[str] = []
    if isinstance(response_message, str) and response_message.strip():
        detail_parts.append(f"message={response_message.strip()!r}")
    if isinstance(response_error, str) and response_error.strip():
        detail_parts.append(f"error={response_error.strip()!r}")
    detail_suffix = (
        f" Detalhes da resposta: {', '.join(detail_parts)}." if detail_parts else ""
    )

    raise RuntimeError(
        "Nao foi possivel localizar o access token nem cookies de sessao na resposta de autenticacao da Dadosfera. "
        f"Chaves recebidas: {available_keys}. Headers recebidos: {header_keys}.{mfa_hint}{detail_suffix}"
    )


def safe_json_body(response: requests.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def build_sign_in_failure(
    error: requests.HTTPError,
    *,
    endpoint: str,
    response_body: dict[str, Any],
    response_headers: Any | None,
) -> RuntimeError:
    status_code = getattr(error.response, "status_code", None)
    body_keys = sorted(response_body.keys())
    header_keys = (
        sorted(str(key).lower() for key in response_headers.keys())
        if response_headers is not None
        else []
    )
    message = response_body.get("message")
    error_code = response_body.get("code") or response_body.get("error")
    details = []
    if isinstance(message, str) and message.strip():
        details.append(f"message={message.strip()!r}")
    if isinstance(error_code, str) and error_code.strip():
        details.append(f"error={error_code.strip()!r}")
    detail_suffix = f" Detalhes: {', '.join(details)}." if details else ""
    return RuntimeError(
        f"Autenticacao da Dadosfera falhou em `{endpoint}` com HTTP {status_code or 'desconhecido'}. "
        f"Chaves do body: {body_keys or ['<none>']}. Headers: {header_keys or ['<none>']}. "
        f"Valide tenant, credenciais, MFA/TOTP e o contrato atual do endpoint de login.{detail_suffix}"
    )


def raise_runtime_for_sign_in_failure(
    error: requests.HTTPError,
    *,
    endpoint: str,
    response_body: dict[str, Any],
    response_headers: Any | None,
) -> None:
    raise build_sign_in_failure(
        error,
        endpoint=endpoint,
        response_body=response_body,
        response_headers=response_headers,
    ) from error


def raise_runtime_for_http_error(
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
            f"Endpoint da Dadosfera nao encontrado durante `{operation}` em `{path}` (HTTP 404). "
            "Valide a base URL do Maestro e o caminho real exposto pelo seu tenant."
        ) from error

    raise RuntimeError(
        f"Chamada da Dadosfera falhou durante `{operation}` em `{path}` com HTTP {status_code or 'desconhecido'}."
    ) from error


def find_existing_asset(
    existing_assets: list[dict[str, Any]], target: CatalogAssetSpec
) -> dict[str, Any] | None:
    for asset in existing_assets:
        if asset.get("external_url") == target.external_url:
            return asset

    for asset in existing_assets:
        asset_name = asset.get("display_name") or asset.get("name")
        if asset_name == target.display_name:
            return asset

    return None


def sync_assets(
    *,
    client: DadosferaMaestroClient,
    assets: list[CatalogAssetSpec],
    dry_run: bool = False,
) -> list[SyncResult]:
    existing_assets = client.list_data_assets()
    results: list[SyncResult] = []

    for asset in assets:
        existing = find_existing_asset(existing_assets, asset)
        if existing is None:
            if dry_run:
                results.append(
                    SyncResult(
                        "would_create", asset.display_name, None, asset.external_url
                    )
                )
                continue

            create_response = client.create_data_asset(build_create_payload(asset))
            created_id = extract_asset_id(create_response)
            if created_id is None:
                refreshed_assets = client.list_data_assets()
                matched = find_existing_asset(refreshed_assets, asset)
                created_id = (
                    int(matched["id"])
                    if matched and matched.get("id") is not None
                    else None
                )

            if created_id is not None:
                client.update_data_asset(created_id, build_update_payload(asset))

            results.append(
                SyncResult(
                    "created", asset.display_name, created_id, asset.external_url
                )
            )
            continue

        asset_id = int(existing["id"])
        if dry_run:
            results.append(
                SyncResult(
                    "would_update", asset.display_name, asset_id, asset.external_url
                )
            )
            continue

        client.update_data_asset(asset_id, build_update_payload(asset))
        results.append(
            SyncResult("updated", asset.display_name, asset_id, asset.external_url)
        )

    return results


def render_report(
    results: list[SyncResult], *, manifest_path: Path, dry_run: bool
) -> str:
    lines = [
        "# Sync de Catalogo via API da Dadosfera",
        "",
        f"- Manifesto usado: `{manifest_path.relative_to(ROOT_DIR).as_posix()}`",
        f"- Modo dry-run: `{dry_run}`",
        "",
        "| Acao | Asset | ID | URL |",
        "| --- | --- | ---: | --- |",
    ]
    for result in results:
        asset_id = "" if result.asset_id is None else str(result.asset_id)
        lines.append(
            f"| `{result.action}` | `{result.asset_name}` | {asset_id} | `{result.external_url}` |"
        )
    return "\n".join(lines) + "\n"


def save_report(report_path: Path, content: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    settings = load_app_settings()
    parser = argparse.ArgumentParser(
        description="Sincroniza ativos do manifesto local com o catalogo da Dadosfera via API."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Manifesto JSON com os ativos a sincronizar.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Caminho do relatorio markdown gerado.",
    )
    parser.add_argument("--base-url", default=settings.dadosfera.base_url)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o plano de sincronizacao sem escrever na API.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    dadosfera_settings = load_app_settings().dadosfera
    dadosfera_settings.validate_credentials(operation="catalog_sync")

    manifest_path = args.manifest.resolve()
    assets = load_manifest(manifest_path)
    client = DadosferaMaestroClient(
        base_url=args.base_url,
        username=dadosfera_settings.username,
        password=dadosfera_settings.password,
        totp=dadosfera_settings.totp,
        access_token=dadosfera_settings.effective_access_token,
    )
    client.sign_in()
    results = sync_assets(client=client, assets=assets, dry_run=args.dry_run)
    report = render_report(results, manifest_path=manifest_path, dry_run=args.dry_run)
    save_report(args.report.resolve(), report)
    print(report)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
