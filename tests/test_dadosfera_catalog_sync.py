from __future__ import annotations

import json
from pathlib import Path

from src.dadosfera_catalog_sync import (
    CatalogAssetSpec,
    build_create_payload,
    build_update_payload,
    find_existing_asset,
    load_manifest,
    sync_assets,
)


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

    def update_data_asset(self, asset_id: int, payload: dict[str, object]) -> dict[str, object]:
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

    assert matched == {"id": 2, "display_name": "App", "external_url": "https://example.com/app"}


def test_sync_assets_creates_new_asset_and_updates_metadata() -> None:
    asset = build_asset()
    client = FakeDadosferaClient()

    results = sync_assets(client=client, assets=[asset], dry_run=False)

    assert [result.action for result in results] == ["created"]
    assert client.created_payloads == [build_create_payload(asset)]
    assert client.updated_payloads == [(100, build_update_payload(asset))]


def test_sync_assets_updates_existing_asset() -> None:
    asset = build_asset()
    client = FakeDadosferaClient(existing_assets=[{"id": 7, "display_name": "App", "external_url": "https://example.com/app"}])

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
