from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import requests
from dotenv import load_dotenv

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DOCS_DIR, ROOT_DIR


DEFAULT_MAESTRO_BASE_URL = "https://maestro.dadosfera.ai"
DEFAULT_MANIFEST_PATH = ROOT_DIR / "contracts" / "catalog" / "dadosfera_catalog_assets.json"
DEFAULT_REPORT_PATH = DOCS_DIR / "dadosfera_api_sync.md"


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
    def __init__(self, *, base_url: str, username: str, password: str, totp: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.totp = totp
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def sign_in(self) -> None:
        last_body: dict[str, Any] = {}
        last_headers: Any | None = None

        for payload in build_sign_in_payloads(username=self.username, password=self.password, totp=self.totp):
            response = self.session.post(f"{self.base_url}/auth/sign-in", json=payload, timeout=60)
            response.raise_for_status()
            body = response.json()
            last_body = body
            last_headers = response.headers

            if apply_auth_from_response(self.session, body, response.headers):
                return

            if try_refresh_access_token(self.session, self.base_url):
                return

        raise_runtime_for_auth_response(last_body, last_headers)

    def list_data_assets(self, *, size: int = 1000) -> list[dict[str, Any]]:
        page = 1
        assets: list[dict[str, Any]] = []
        total = None

        while total is None or len(assets) < total:
            response = self.session.get(
                f"{self.base_url}/catalog",
                params={"size": size, "page": page, "sort_by": "created_at", "order": "desc"},
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            assets.extend(body.get("data_assets", []))
            total = int(body.get("total", len(assets)))
            if not body.get("data_assets"):
                break
            page += 1

        return assets

    def create_data_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(f"{self.base_url}/catalog", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def update_data_asset(self, asset_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.put(f"{self.base_url}/catalog/data-asset/{asset_id}", json=payload, timeout=60)
        response.raise_for_status()
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


def build_sign_in_payloads(*, username: str, password: str, totp: str | None) -> list[dict[str, str]]:
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


def apply_auth_from_response(session: requests.Session, response_body: dict[str, Any], response_headers: Any | None) -> bool:
    access_token = extract_access_token(response_body, response_headers)
    if access_token:
        session.headers.update(
            {
                "access-token": access_token,
                "Authorization": f"Bearer {access_token}",
            }
        )
        return True

    return bool(session.cookies)


def try_refresh_access_token(session: requests.Session, base_url: str) -> bool:
    response = session.post(f"{base_url}/auth/refresh-access-token", timeout=60)
    if response.status_code >= 400:
        return False

    body = response.json()
    return apply_auth_from_response(session, body, response.headers)


def extract_access_token(response_body: dict[str, Any], response_headers: Any | None = None) -> str | None:
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
        normalized_headers = {str(key).lower(): str(value) for key, value in response_headers.items()}
        token_candidates.extend(
            [
                normalized_headers.get("access-token"),
                normalized_headers.get("x-access-token"),
            ]
        )

        authorization = normalized_headers.get("authorization")
        if isinstance(authorization, str) and authorization.lower().startswith("bearer "):
            token_candidates.append(authorization[7:].strip())

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


def raise_runtime_for_auth_response(response_body: dict[str, Any], response_headers: Any | None = None) -> None:
    available_keys = ", ".join(sorted(response_body.keys())) or "<none>"
    header_keys = "<none>"
    if response_headers is not None:
        header_keys = ", ".join(sorted(str(key).lower() for key in response_headers.keys())) or "<none>"

    mfa_status = response_body.get("mfaStatus")
    mfa_hint = ""
    if mfa_status not in (None, False, "disabled", "DISABLED"):
        mfa_hint = " A resposta indica MFA ativo; valide DADOSFERA_TOTP e o formato do payload de autenticacao."

    raise RuntimeError(
        "Nao foi possivel localizar o access token nem cookies de sessao na resposta de autenticacao da Dadosfera. "
        f"Chaves recebidas: {available_keys}. Headers recebidos: {header_keys}.{mfa_hint}"
    )


def find_existing_asset(existing_assets: list[dict[str, Any]], target: CatalogAssetSpec) -> dict[str, Any] | None:
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
                results.append(SyncResult("would_create", asset.display_name, None, asset.external_url))
                continue

            create_response = client.create_data_asset(build_create_payload(asset))
            created_id = extract_asset_id(create_response)
            if created_id is None:
                refreshed_assets = client.list_data_assets()
                matched = find_existing_asset(refreshed_assets, asset)
                created_id = int(matched["id"]) if matched and matched.get("id") is not None else None

            if created_id is not None:
                client.update_data_asset(created_id, build_update_payload(asset))

            results.append(SyncResult("created", asset.display_name, created_id, asset.external_url))
            continue

        asset_id = int(existing["id"])
        if dry_run:
            results.append(SyncResult("would_update", asset.display_name, asset_id, asset.external_url))
            continue

        client.update_data_asset(asset_id, build_update_payload(asset))
        results.append(SyncResult("updated", asset.display_name, asset_id, asset.external_url))

    return results


def render_report(results: list[SyncResult], *, manifest_path: Path, dry_run: bool) -> str:
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
        lines.append(f"| `{result.action}` | `{result.asset_name}` | {asset_id} | `{result.external_url}` |")
    return "\n".join(lines) + "\n"


def save_report(report_path: Path, content: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sincroniza ativos do manifesto local com o catalogo da Dadosfera via API.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Manifesto JSON com os ativos a sincronizar.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH, help="Caminho do relatorio markdown gerado.")
    parser.add_argument("--base-url", default=os.getenv("DADOSFERA_MAESTRO_BASE_URL", DEFAULT_MAESTRO_BASE_URL))
    parser.add_argument("--dry-run", action="store_true", help="Mostra o plano de sincronizacao sem escrever na API.")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    username = os.getenv("DADOSFERA_USERNAME")
    password = os.getenv("DADOSFERA_PASSWORD")
    totp = os.getenv("DADOSFERA_TOTP")
    if not username or not password:
        raise RuntimeError("Defina DADOSFERA_USERNAME e DADOSFERA_PASSWORD para sincronizar o catalogo.")

    manifest_path = args.manifest.resolve()
    assets = load_manifest(manifest_path)
    client = DadosferaMaestroClient(
        base_url=args.base_url,
        username=username,
        password=password,
        totp=totp,
    )
    client.sign_in()
    results = sync_assets(client=client, assets=assets, dry_run=args.dry_run)
    report = render_report(results, manifest_path=manifest_path, dry_run=args.dry_run)
    save_report(args.report.resolve(), report)
    print(report)


if __name__ == "__main__":
    main()
