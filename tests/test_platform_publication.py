from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

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


def test_to_project_path_returns_relative_path_inside_repo(tmp_path: Path) -> None:
    relative_path = platform_publication.ROOT_DIR / "docs" / "platform_publication.md"

    assert platform_publication.to_project_path(relative_path) == "docs/platform_publication.md"


def test_run_pipeline_publication_requires_name_field(tmp_path: Path) -> None:
    definition_path = tmp_path / "pipeline.json"
    definition_path.write_text(json.dumps({"display_name": "missing-name"}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="campo `name`"):
        platform_publication.run_pipeline_publication(
            base_url="https://maestro.example.com",
            definition_path=definition_path,
            dry_run=False,
            execute_pipeline=False,
        )


def test_run_pipeline_publication_creates_and_executes_pipeline(monkeypatch, tmp_path: Path) -> None:
    definition_path = tmp_path / "pipeline.json"
    definition_path.write_text(json.dumps({"name": "olist-pipeline"}), encoding="utf-8")

    class DummyClient:
        def __init__(self) -> None:
            self.created_definition: dict[str, str] | None = None
            self.run_calls: list[tuple[str, dict[str, str]]] = []

        @staticmethod
        def sign_in() -> None:
            return None

        def create_pipeline(self, definition: dict[str, str]) -> dict[str, str]:
            self.created_definition = definition
            return {"id": "pipe-123"}

        def run_pipeline(self, pipeline_id: str, payload: dict[str, str]) -> dict[str, str]:
            self.run_calls.append((pipeline_id, payload))
            return {"run_id": "run-456"}

    client = DummyClient()
    monkeypatch.setattr(platform_publication, "build_pipeline_client", lambda base_url: client)
    monkeypatch.setattr(platform_publication, "find_pipeline_by_name", lambda client, pipeline_name: None)

    result = platform_publication.run_pipeline_publication(
        base_url="https://maestro.example.com",
        definition_path=definition_path,
        dry_run=False,
        execute_pipeline=True,
    )

    assert result.status == "SUCCESS"
    assert "pipe-123" in result.details
    assert "run-456" in result.details
    assert client.created_definition == {"name": "olist-pipeline"}
    assert client.run_calls == [("pipe-123", {})]


def test_build_clients_validate_settings_and_forward_credentials(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    class DummyDadosferaSettings:
        base_url = "https://maestro.example.com"
        username = "user"
        password = "secret"
        totp = "123456"
        effective_access_token = "token"

        @staticmethod
        def validate_credentials(*, operation: str) -> None:
            calls.append(("validate", operation))

    class DummySettings:
        dadosfera = DummyDadosferaSettings()

    monkeypatch.setattr(platform_publication, "load_app_settings", lambda: DummySettings())
    monkeypatch.setattr(platform_publication, "DadosferaMaestroClient", lambda **kwargs: ("catalog", kwargs))
    monkeypatch.setattr(platform_publication, "DadosferaPipelineClient", lambda **kwargs: ("pipeline", kwargs))

    catalog_client = platform_publication.build_catalog_client("https://maestro.example.com")
    pipeline_client = platform_publication.build_pipeline_client("https://maestro.example.com")

    assert calls == [
        ("validate", "platform_publication_catalog"),
        ("validate", "platform_publication_pipeline"),
    ]
    assert catalog_client[1]["username"] == "user"
    assert pipeline_client[1]["access_token"] == "token"


def test_parse_args_reads_flags(monkeypatch, tmp_path: Path) -> None:
    class DummySettings:
        class DadosferaSettings:
            base_url = "https://maestro.example.com"

        dadosfera = DadosferaSettings()

    report_path = tmp_path / "report.md"
    monkeypatch.setattr(platform_publication, "load_app_settings", lambda: DummySettings())
    monkeypatch.setattr(
        "sys.argv",
        [
            "platform_publication.py",
            "--target-environment",
            "stage",
            "--report",
            str(report_path),
            "--dry-run",
            "--skip-catalog-sync",
        ],
    )

    args = platform_publication.parse_args()

    assert args.base_url == "https://maestro.example.com"
    assert args.target_environment == "stage"
    assert args.report == report_path
    assert args.dry_run is True
    assert args.skip_catalog_sync is True


def test_main_generates_report_with_selected_steps(monkeypatch, tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "platform_publication.md"
    manifest_path = tmp_path / "manifest.json"
    definition_path = tmp_path / "pipeline.json"
    manifest_path.write_text("[]", encoding="utf-8")
    definition_path.write_text("{}", encoding="utf-8")

    args = argparse.Namespace(
        base_url="https://maestro.example.com",
        target_environment="prod",
        manifest=manifest_path,
        pipeline_definition=definition_path,
        report=report_path,
        dry_run=True,
        skip_catalog_sync=False,
        skip_pipeline_publication=False,
        execute_pipeline=False,
    )

    monkeypatch.setattr(platform_publication, "configure_logging", lambda: None)
    monkeypatch.setattr(platform_publication, "parse_args", lambda: args)
    monkeypatch.setattr(
        platform_publication,
        "run_catalog_publication",
        lambda **kwargs: ([], platform_publication.PlatformPublicationResult("catalog_sync", "DRY_RUN", "ok")),
    )
    monkeypatch.setattr(
        platform_publication,
        "run_pipeline_publication",
        lambda **kwargs: platform_publication.PlatformPublicationResult("pipeline_publication", "DRY_RUN", "ok"),
    )

    platform_publication.main()

    saved_report = report_path.read_text(encoding="utf-8")
    stdout = capsys.readouterr().out
    assert "`catalog_sync`" in saved_report
    assert "`pipeline_publication`" in saved_report
    assert stdout == saved_report + "\n" or stdout == saved_report
