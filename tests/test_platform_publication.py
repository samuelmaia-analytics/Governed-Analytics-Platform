from __future__ import annotations

import json
from pathlib import Path

import src.platform_publication as platform_publication
from src.dadosfera_catalog_sync import CatalogAssetSpec, SyncResult


def test_run_catalog_publication_returns_summary(monkeypatch, tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(platform_publication, "load_manifest", lambda path: [  # type: ignore[arg-type]
        CatalogAssetSpec(
            display_name="App",
            description="Dashboard",
            data_asset_type="dashboard",
            external_url="https://example.com/app",
            location="streamlit",
            tags=["dashboard"],
        )
    ])

    class DummyClient:
        @staticmethod
        def sign_in() -> None:
            return None

    monkeypatch.setattr(platform_publication, "build_catalog_client", lambda base_url: DummyClient())
    monkeypatch.setattr(
        platform_publication,
        "sync_assets",
        lambda client, assets, dry_run: [SyncResult("would_create", "App", None, "https://example.com/app")],
    )

    _, result = platform_publication.run_catalog_publication(
        base_url="https://maestro.example.com",
        manifest_path=manifest_path,
        dry_run=True,
    )

    assert result.stage == "catalog_sync"
    assert result.status == "DRY_RUN"
    assert "1 ativos processados" in result.details


def test_run_pipeline_publication_supports_existing_pipeline_dry_run(monkeypatch, tmp_path: Path) -> None:
    definition_path = tmp_path / "pipeline.json"
    definition_path.write_text(json.dumps({"name": "olist-pipeline"}), encoding="utf-8")

    class DummyClient:
        @staticmethod
        def sign_in() -> None:
            return None

    monkeypatch.setattr(platform_publication, "build_pipeline_client", lambda base_url: DummyClient())
    monkeypatch.setattr(
        platform_publication,
        "find_pipeline_by_name",
        lambda client, pipeline_name: {"id": "pipe-1", "name": pipeline_name},
    )

    result = platform_publication.run_pipeline_publication(
        base_url="https://maestro.example.com",
        definition_path=definition_path,
        dry_run=True,
        execute_pipeline=True,
    )

    assert result.stage == "pipeline_publication"
    assert result.status == "DRY_RUN"
    assert "já existe" in result.details
    assert "seria executada" in result.details


def test_render_report_includes_results_table(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    definition_path = tmp_path / "pipeline.json"
    manifest_path.write_text("[]", encoding="utf-8")
    definition_path.write_text("{}", encoding="utf-8")

    report = platform_publication.render_report(
        target_environment="prod",
        manifest_path=manifest_path,
        definition_path=definition_path,
        results=[
            platform_publication.PlatformPublicationResult(
                stage="catalog_sync",
                status="SUCCESS",
                details="ok",
            )
        ],
    )

    assert "| Etapa | Status | Detalhes |" in report
    assert "`catalog_sync`" in report
